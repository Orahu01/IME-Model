Flick Lab 用の軽いAIモデル(llm-jp-3-150m を GGUF に変換し q4_0 に量子化したもの、約95MB)です。誤字補正「もしかして」に使います。

- 元モデル: llm-jp/llm-jp-3-150m(https://huggingface.co/llm-jp/llm-jp-3-150m)
- 変換・量子化: llama.cpp(MIT)。使った版は build-model-150m.yml に固定
- 元モデルのコミットとライセンス、llama.cpp の版は SOURCE.txt に、ファイルのハッシュは SHA256SUMS.txt にあります
- 元モデルからの変更点: ①形式の変換(GGUF)と量子化(q4_0)。②元モデルには tokenizer.model が無く tokenizer.json だけなので、tokenizer.json の語彙とスコアから SentencePiece 形式の tokenizer.model を作って変換に使っている(語彙・スコアは元のまま。作る手順は tools/hf_unigram_to_spm.py)。重みの中身は変えていません。量子化により、元モデルと出力が完全には一致しません
