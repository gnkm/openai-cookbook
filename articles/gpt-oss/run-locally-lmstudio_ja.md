# LM Studioを使ってgpt-ossをローカルで実行する方法

[LM Studio](https://lmstudio.ai)は、ローカルハードウェア上で大規模言語モデル（LLM）を実行するための高性能でユーザーフレンドリーなデスクトップアプリケーションです。このガイドでは、LM Studioを使用して**gpt-oss-20b**または**gpt-oss-120b**モデルをセットアップして実行する方法を説明します。これには、モデルとのチャット、MCPサーバーの使用、またはLM Studioのローカル開発API経由でのモデルとの対話が含まれます。

このガイドは、PCやMacでgpt-ossを実行するなど、コンシューマーハードウェア向けであることにご注意ください。NVIDIAのH100などの専用GPUを搭載したサーバーアプリケーションについては、[vLLMガイドをご確認ください](https://cookbook.openai.com/articles/gpt-oss/run-vllm)。

## モデルを選択する

LM Studioは、gpt-ossの両方のモデルサイズをサポートしています：

- [**`openai/gpt-oss-20b`**](https://lmstudio.ai/models/openai/gpt-oss-20b)
  - 小さいモデル
  - 最低**16GBのVRAM**のみが必要
  - ハイエンドコンシューマーGPUやApple Silicon Macに最適
- [**`openai/gpt-oss-120b`**](https://lmstudio.ai/models/openai/gpt-oss-120b)
  - より大きなフルサイズモデル
  - **≥60GB VRAM**が最適
  - マルチGPUまたは高性能ワークステーション設定に理想的

LM Studioには、[llama.cpp](https://github.com/ggml-org/llama.cpp)推論エンジン（GGUF形式のモデルを実行）と、Apple Silicon Mac用の[Apple MLX](https://github.com/ml-explore/mlx)エンジンの両方が搭載されています。

## クイックセットアップ

1. **LM Studioをインストール**
   LM StudioはWindows、macOS、Linuxで利用できます。[こちらから入手してください](https://lmstudio.ai/download)。

2. **gpt-ossモデルをダウンロード** → 

```shell
# 20B用
lms get openai/gpt-oss-20b
# または120B用
lms get openai/gpt-oss-120b
``` 

3. **LM Studioでモデルを読み込み** 
  → LM Studioを開き、モデル読み込みインターフェースを使用してダウンロードしたgpt-ossモデルを読み込みます。または、コマンドラインを使用することもできます：

```shell
# 20B用
lms load openai/gpt-oss-20b
# または120B用
lms load openai/gpt-oss-120b
```

4. **モデルを使用** → 読み込み後、LM Studioのチャットインターフェースで直接モデルと対話するか、API経由で使用できます。

## gpt-ossとチャットする

LM Studioのチャットインターフェースを使用してgpt-ossとの会話を開始するか、ターミナルで`chat`コマンドを使用します：

```shell
lms chat openai/gpt-oss-20b
```

プロンプト形式に関する注意：LM Studioは、llama.cppとMLXの両方で実行する際に、gpt-ossモデルへの入力を構築するためにOpenAIの[Harmony](https://cookbook.openai.com/articles/openai-harmony)ライブラリを利用します。

## ローカル/v1/chat/completionsエンドポイントでgpt-ossを使用する

LM Studioは**Chat Completions互換API**を公開しているため、大きな変更なしにOpenAI SDKを使用できます。以下はPythonの例です：

```py
from openai import OpenAI

client = OpenAI(
    base_url="http://localhost:1234/v1",
    api_key="not-needed"  # LM StudioはAPIキーを必要としません
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

OpenAI SDKを以前に使用したことがある場合、これは即座に馴染みやすく感じられ、ベースURLを変更するだけで既存のコードが動作するはずです。

## チャットUIでMCPを使用する方法

LM Studioは[MCPクライアント](https://lmstudio.ai/docs/app/plugins/mcp)であり、MCPサーバーを接続できます。これにより、gpt-ossモデルに外部ツールを提供できます。

LM StudioのmCP.jsonファイルは以下の場所にあります：

```shell
~/.lmstudio/mcp.json
```

## PythonまたはTypeScriptでgpt-ossを使ったローカルツール使用

LM StudioのSDKは[Python](https://github.com/lmstudio-ai/lmstudio-python)と[TypeScript](https://github.com/lmstudio-ai/lmstudio-js)の両方で利用できます。SDKを活用して、gpt-ossでツール呼び出しとローカル関数実行を実装できます。

これを実現する方法は`.act()`呼び出しを通じてであり、gpt-ossにツールを提供し、タスクを完了するまでツール呼び出しと推論を行き来させることができます。

以下の例は、ローカルファイルシステムにファイルを作成できる単一のツールをモデルに提供する方法を示しています。この例を出発点として使用し、より多くのツールで拡張できます。ツール定義に関するドキュメントは[Python](https://lmstudio.ai/docs/python/agent/tools)と[TypeScript](https://lmstudio.ai/docs/typescript/agent/tools)をご覧ください。

```shell
uv pip install lmstudio
```

```python
import readline # 入力行編集を有効にする
from pathlib import Path

import lmstudio as lms

# モデルによって呼び出される関数を定義し、ツールとしてモデルに提供する。
# ツールは通常のPython関数です。何でも構いません。
def create_file(name: str, content: str):
    """指定された名前と内容でファイルを作成する。"""
    dest_path = Path(name)
    if dest_path.exists():
        return "Error: File already exists."
    try:
        dest_path.write_text(content, encoding="utf-8")
    except Exception as exc:
        return "Error: {exc!r}"
    return "File created."

def print_fragment(fragment, round_index=0):
    # .act()は第2パラメータとしてラウンドインデックスを提供
    # デフォルト値を設定することで、コールバックは
    # .complete()と.respond()とも互換性がある。
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

gpt-ossをローカルで利用したいTypeScript開発者向けに、`lmstudio-js`を使用した同様の例を以下に示します：

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
    // モデルがメッセージ全体を完了したら、チャットにプッシュ
    onMessage: (message) => chat.append(message),
    onPredictionFragment: ({ content }) => {
      process.stdout.write(content);
    },
  });
  process.stdout.write("\n");
}
```