# LM Studio で gpt-oss をローカルで実行する方法

[LM Studio](https://lmstudio.ai) は、ローカルハードウェアで大規模言語モデル（LLM）を実行するための高性能でフレンドリーなデスクトップアプリケーションです。このガイドでは、LM Studio を使用して **gpt-oss-20b** または **gpt-oss-120b** モデルをセットアップして実行する方法、チャットする方法、MCP サーバーを使用する方法、または LM Studio のローカル開発 API を通じてモデルと対話する方法を説明します。

このガイドは、PC や Mac で gpt-oss を実行するようなコンシューマーハードウェアを対象としていることに注意してください。NVIDIA の H100 のような専用 GPU を使用するサーバーアプリケーションの場合は、[vLLM ガイドをご覧ください](https://cookbook.openai.com/articles/gpt-oss/run-vllm)。

## モデルを選択する

LM Studio は gpt-oss の両方のモデルサイズをサポートしています：

- [**`openai/gpt-oss-20b`**](https://lmstudio.ai/models/openai/gpt-oss-20b)
  - 小さいモデル
  - 最低 **16GB の VRAM** のみが必要
  - ハイエンドのコンシューマー GPU または Apple Silicon Mac に最適
- [**`openai/gpt-oss-120b`**](https://lmstudio.ai/models/openai/gpt-oss-120b)
  - より大きなフルサイズのモデル
  - **≥60GB VRAM** が最適
  - マルチ GPU または強力なワークステーションセットアップに最適

LM Studio は、[llama.cpp](https://github.com/ggml-org/llama.cpp) 推論エンジン（GGUF フォーマットのモデルを実行）と、Apple Silicon Mac 用の [Apple MLX](https://github.com/ml-explore/mlx) エンジンの両方を搭載しています。

## クイックセットアップ

1. **LM Studio をインストール**
   LM Studio は Windows、macOS、Linux で利用できます。[こちらから入手](https://lmstudio.ai/download)。

2. **gpt-oss モデルをダウンロード** → 

```shell
# 20B の場合
lms get openai/gpt-oss-20b
# または 120B の場合
lms get openai/gpt-oss-120b
``` 

3. **LM Studio でモデルをロード** 
  → LM Studio を開き、モデルローディングインターフェースを使用して、ダウンロードした gpt-oss モデルをロードします。または、コマンドラインを使用できます：

```shell
# 20B の場合
lms load openai/gpt-oss-20b
# または 120B の場合
lms load openai/gpt-oss-120b
```

4. **モデルを使用** → ロードされたら、LM Studio のチャットインターフェースで直接モデルと対話するか、API を通じて対話できます。

## gpt-oss とチャットする

LM Studio のチャットインターフェースを使用して gpt-oss との会話を開始するか、ターミナルで `chat` コマンドを使用します：

```shell
lms chat openai/gpt-oss-20b
```

プロンプトフォーマットに関する注意：LM Studio は、llama.cpp と MLX の両方で実行する際に、gpt-oss モデルへの入力を構築するために OpenAI の [Harmony](https://cookbook.openai.com/articles/openai-harmony) ライブラリを利用します。

## ローカルの /v1/chat/completions エンドポイントで gpt-oss を使用する

LM Studio は **Chat Completions 互換 API** を公開しているため、OpenAI SDK を大きく変更することなく使用できます。Python の例を次に示します：

```py
from openai import OpenAI

client = OpenAI(
    base_url="http://localhost:1234/v1",
    api_key="not-needed"  # LM Studio は API キーを必要としません
)

result = client.chat.completions.create(
    model="openai/gpt-oss-20b",
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Explain what MXFP4 quantization is."}
    ]
)

print(result.choices[0].message.content)
```

以前に OpenAI SDK を使用したことがある場合、これはすぐに馴染みがあり、ベース URL を変更するだけで既存のコードが機能するはずです。

## チャット UI で MCP を使用する方法

LM Studio は [MCP クライアント](https://lmstudio.ai/docs/app/plugins/mcp)であり、MCP サーバーに接続できます。これにより、gpt-oss モデルに外部ツールを提供できます。

LM Studio の mcp.json ファイルは次の場所にあります：

```shell
~/.lmstudio/mcp.json
```

## Python または TypeScript での gpt-oss を使用したローカルツールの使用

LM Studio の SDK は、[Python](https://github.com/lmstudio-ai/lmstudio-python) と [TypeScript](https://github.com/lmstudio-ai/lmstudio-js) の両方で利用できます。SDK を活用して、gpt-oss でツール呼び出しとローカル関数実行を実装できます。

これを実現する方法は、`.act()` 呼び出しを介して行われます。これにより、gpt-oss にツールを提供し、タスクを完了するまで、ツールの呼び出しと推論の間を行き来させることができます。

以下の例は、ローカルファイルシステムにファイルを作成できる単一のツールをモデルに提供する方法を示しています。この例を出発点として使用し、より多くのツールで拡張できます。ツール定義に関するドキュメントは、[Python](https://lmstudio.ai/docs/python/agent/tools) と [TypeScript](https://lmstudio.ai/docs/typescript/agent/tools) をご覧ください。

```shell
uv pip install lmstudio
```

```python
import readline # 入力行編集を有効にする
from pathlib import Path

import lmstudio as lms

# モデルによって呼び出すことができる関数を定義し、ツールとしてモデルに提供します。
# ツールは通常の Python 関数です。何でも構いません。
def create_file(name: str, content: str):
    """指定された名前とコンテンツでファイルを作成します。"""
    dest_path = Path(name)
    if dest_path.exists():
        return "Error: File already exists."
    try:
        dest_path.write_text(content, encoding="utf-8")
    except Exception as exc:
        return "Error: {exc!r}"
    return "File created."

def print_fragment(fragment, round_index=0):
    # .act() はラウンドインデックスを2番目のパラメータとして提供します
    # デフォルト値を設定すると、コールバックは
    # .complete() と .respond() とも互換性があります。
    print(fragment.content, end="", flush=True)

model = lms.llm("openai/gpt-oss-20b")
chat = lms.Chat("You are a helpful assistant running on the user's computer.")

while True:
    try:
        user_input = input("User (leave blank to exit): ")
    except EOFError:
        print()
        break
    if not user_input:
        break
    chat.add_user_message(user_input)
    print("Assistant: ", end="", flush=True)
    model.act(
        chat,
        [create_file],
        on_message=chat.append,
        on_prediction_fragment=print_fragment,
    )
    print()

```

gpt-oss をローカルで利用したい TypeScript 開発者向けに、`lmstudio-js` を使用した同様の例を次に示します：

```shell
npm install @lmstudio/sdk
```

```typescript
import { Chat, LMStudioClient, tool } from "@lmstudio/sdk";
import { existsSync } from "fs";
import { writeFile } from "fs/promises";
import { createInterface } from "readline/promises";
import { z } from "zod";

const rl = createInterface({ input: process.stdin, output: process.stdout });
const client = new LMStudioClient();
const model = await client.llm.model("openai/gpt-oss-20b");
const chat = Chat.empty();

const createFileTool = tool({
  name: "createFile",
  description: "Create a file with the given name and content.",
  parameters: { name: z.string(), content: z.string() },
  implementation: async ({ name, content }) => {
    if (existsSync(name)) {
      return "Error: File already exists.";
    }
    await writeFile(name, content, "utf-8");
    return "File created.";
  },
});

while (true) {
  const input = await rl.question("User: ");
  // ユーザー入力をチャットに追加
  chat.append("user", input);

  process.stdout.write("Assistant: ");
  await model.act(chat, [createFileTool], {
    // モデルがメッセージ全体を終了したら、チャットにプッシュ
    onMessage: (message) => chat.append(message),
    onPredictionFragment: ({ content }) => {
      process.stdout.write(content);
    },
  });
  process.stdout.write("\n");
}
```

