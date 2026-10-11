#!/usr/bin/env python3
"""HF の tokenizer.json が Unigram で tokenizer.model が無いモデルに、SentencePiece の tokenizer.model を作る。

llm-jp-3 のように、トークナイザが SentencePiece Unigram なのに HF には tokenizer.json しか無いモデルは、
llama.cpp の変換器が「BPE の pre-tokenizer が未登録」で止まる(語彙の内容は Unigram なので、BPE として扱うのが誤り)。
tokenizer.model があれば、変換器は SentencePiece の経路(tokenizer.ggml.model = llama、スコア付き)で書き出し、
このリポジトリの自前 Unigram トークナイザ(native/flicklab_lm/src/spm_unigram.*)がそれを使う。

作るもの: 語彙とスコア(tokenizer.json の model.vocab)、unk/bos/eos/pad の位置、バイトフォールバック、先頭の空白の扱い。
前提: 正規化は identity。tokenizer.json に normalizer があるときは内容を表示するだけで、再現はしない
(prepare_model.py の --strict-tokenizer が HF との一致を調べるので、ずれていればそこで分かる)。

  python tools/ai/hf_unigram_to_spm.py <HFフォルダ>
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any, Dict, Iterator, List, Optional

BYTE_PIECE = re.compile(r"^<0x[0-9A-Fa-f]{2}>$")


def _walk(node: Any) -> Iterator[Dict[str, Any]]:
    """normalizer / pre_tokenizer の入れ子(Sequence)を平らにたどる。"""
    if isinstance(node, dict):
        yield node
        for key in ("normalizers", "pretokenizers"):
            for child in node.get(key, []) or []:
                yield from _walk(child)
    elif isinstance(node, list):
        for child in node:
            yield from _walk(child)


def describe(data: Dict[str, Any]) -> List[str]:
    """人が読むための要約(ログ用)。"""
    lines = []
    for key in ("normalizer", "pre_tokenizer", "post_processor", "decoder"):
        types = [n.get("type", "?") for n in _walk(data.get(key))] if data.get(key) else []
        lines.append(f"  {key}: {' > '.join(types) if types else '(なし)'}")
    m = data.get("model") or {}
    lines.append(f"  model: {m.get('type')}  vocab={len(m.get('vocab', []))}  unk_id={m.get('unk_id')}  byte_fallback={m.get('byte_fallback')}")
    return lines


def dummy_prefix(data: Dict[str, Any]) -> bool:
    """文頭に空白(▁)を足すか。Metaspace の prepend_scheme(新)/add_prefix_space(旧)から決める。"""
    for n in _walk(data.get("pre_tokenizer")):
        if n.get("type") == "Metaspace":
            scheme = n.get("prepend_scheme")
            if scheme is not None:
                return scheme != "never"
            return bool(n.get("add_prefix_space", True))
    return False


def build_proto(data: Dict[str, Any]):
    from sentencepiece import sentencepiece_model_pb2 as pb

    m = data["model"]
    vocab = m["vocab"]
    unk_id = int(m.get("unk_id", 0) or 0)
    byte_fallback = bool(m.get("byte_fallback", False))
    special = {t["content"] for t in data.get("added_tokens", []) if t.get("special")}

    proto = pb.ModelProto()
    for i, (piece, score) in enumerate(vocab):
        sp = proto.pieces.add()
        sp.piece = piece
        sp.score = float(score)
        if i == unk_id:
            sp.type = pb.ModelProto.SentencePiece.UNKNOWN
        elif byte_fallback and BYTE_PIECE.match(piece):
            sp.type = pb.ModelProto.SentencePiece.BYTE
        elif piece in special:
            sp.type = pb.ModelProto.SentencePiece.CONTROL
        else:
            sp.type = pb.ModelProto.SentencePiece.NORMAL

    def find(*names: str) -> int:
        for name in names:
            for i, (piece, _) in enumerate(vocab):
                if piece == name:
                    return i
        return -1

    ts = proto.trainer_spec
    ts.model_type = pb.TrainerSpec.UNIGRAM
    ts.vocab_size = len(vocab)
    ts.unk_id = unk_id
    ts.bos_id = find("<s>", "<|startoftext|>")
    ts.eos_id = find("</s>", "<|endoftext|>")
    ts.pad_id = find("<pad>", "[PAD]")
    ts.byte_fallback = byte_fallback

    ns = proto.normalizer_spec
    ns.name = "identity"
    ns.add_dummy_prefix = dummy_prefix(data)
    ns.remove_extra_whitespaces = False
    ns.escape_whitespaces = True
    return proto


def convert(hf_dir: Path, quiet: bool = False) -> bool:
    """作ったら True。tokenizer.model が既にある/Unigram でない/tokenizer.json が無いなら何もせず False。"""
    out = hf_dir / "tokenizer.model"
    tj = hf_dir / "tokenizer.json"
    if out.is_file() or not tj.is_file():
        return False
    data = json.loads(tj.read_text(encoding="utf-8"))
    if (data.get("model") or {}).get("type") != "Unigram":
        return False
    if not quiet:
        print("tokenizer.model が無く、tokenizer.json は Unigram → SentencePiece 形式を作ります")
        for line in describe(data):
            print(line)
        print(f"  先頭の空白(dummy prefix): {dummy_prefix(data)}")
    out.write_bytes(build_proto(data).SerializeToString())
    return True


def main(argv: Optional[List[str]] = None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    if len(argv) != 1:
        print(__doc__)
        return 2
    made = convert(Path(argv[0]))
    print("作成しました" if made else "何もしませんでした(tokenizer.model が既にある、または Unigram ではない)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
