Flick Lab 用の軽いAIモデル(llm-jp-3-150m を GGUF に変換し q4_0 に量子化したもの、約95MB)です。誤字補正「もしかして」に使います。

- 元モデル: llm-jp/llm-jp-3-150m(https://huggingface.co/llm-jp/llm-jp-3-150m)
- 変換・量子化: llama.cpp(MIT)。使った版は build-model-150m.yml に固定
- 元モデルのコミットとライセンス、llama.cpp の版は SOURCE.txt に、ファイルのハッシュは SHA256SUMS.txt にあります
- 内容の改変はありません(形式の変換と量子化のみ)。量子化により、元モデルと出力が完全には一致しません
