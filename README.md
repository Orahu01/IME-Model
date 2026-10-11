# IME-Model

自作の日本語キーボード「Flick Lab」が使う、**AIモデルの配布用リポジトリ**です。置いてあるのはモデルのファイルだけで、アプリ本体は含みません。

## 中身

| ファイル | 説明 |
|---|---|
| `sarashina2.2-0.5b-q4_0.gguf` | [sbintuitions/sarashina2.2-0.5b](https://huggingface.co/sbintuitions/sarashina2.2-0.5b) を llama.cpp で GGUF に変換し、q4_0 に量子化したもの(約480MB) |
| `SHA256SUMS.txt` | 上のファイルの SHA-256 |

軽いモデルは、別のリリース(タグ `llm-jp-3-150m-v1`)にあります。

| ファイル | 説明 |
|---|---|
| `llm-jp-3-150m-q4_0.gguf` | [llm-jp/llm-jp-3-150m](https://huggingface.co/llm-jp/llm-jp-3-150m)(Apache-2.0)を同じ手順で GGUF に変換し、q4_0 に量子化したもの(約95MB)。誤字補正用 |
| `SHA256SUMS.txt` / `SOURCE.txt` / `LICENSE-llm-jp-3-150m.txt` | ハッシュ / 元モデルと llama.cpp の版 / 元モデルのライセンス文 |

作り方は `.github/workflows/build-model-150m.yml`(Actions の手動実行)です。トークナイザの変換に `tools/hf_unigram_to_spm.py` を使います。

ファイルは **Releases** にあります(ログイン不要で誰でも落とせます)。

## ライセンスと出どころ

- 元モデル: SB Intuitions の Sarashina2.2 0.5B。ライセンスは **MIT**(上のモデルカードに記載)。このリポジトリのモデルファイルも、そのライセンスに従います。
- 変換・量子化: [llama.cpp](https://github.com/ggml-org/llama.cpp)(MIT)の `convert_hf_to_gguf.py` と `llama-quantize`。使った版は `.github/workflows/build-model.yml` に固定しています。
- 内容の改変はありません(形式の変換と量子化のみ)。量子化により、元モデルと出力が完全には一致しません。
- **作り方は公開されています**: `.github/workflows/build-model.yml`(Actions の手動実行)で、誰でも同じファイルを作れます。

## 使い方

Flick Lab の設定 → AI で、モデルをこのリリースからダウンロードします(アプリ側で SHA-256 を確かめます)。手動で使う場合は、`.gguf` をスマホに保存し、アプリの「ファイルを選んで取り込む」から選びます。
