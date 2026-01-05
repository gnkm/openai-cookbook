# Ollamaでgpt-ossをローカル実行する方法

[**OpenAI gpt-oss**](https://openai.com/open-models)を自分のハードウェアで動かしたいですか？このガイドでは、[Ollama](https://ollama.ai)を使用して**gpt-oss-20b**または**gpt-oss-120b**をローカルでセットアップし、オフラインでチャットしたり、API経由で使用したり、Agents SDKに接続したりする方法を説明します。

このガイドは、PCやMacでモデルを実行するなど、コンシューマー向けハードウェアを対象としています。NVIDIA H100などの専用GPUを搭載したサーバーアプリケーションについては、[vLLMガイドをご確認ください](https://cookbook.openai.com/articles/gpt-oss/run-vllm)。

## モデルを選択する

Ollamaはgpt-ossの両方のモデルサイズをサポートしています：

- **`gpt-oss-20b`**
  - 小さいモデル
  - **16GB以上のVRAM**または**統合メモリ**で最適
  - ハイエンドコンシューマーGPUやApple SiliconのMacに最適
- **`gpt-oss-120b`**
  - 大きなフルサイズモデル
  - **60GB以上のVRAM**または**統合メモリ**で最適
  - マルチGPUまたは高性能ワークステーション構成に最適

**いくつかの注意点：**

- これらのモデルは**MXFP4量子化**された状態で提供され、現在他の量子化はありません
- VRAMが不足している場合はCPUにオフロードできますが、動作が遅くなることが予想されます。

## クイックセットアップ

1. **Ollamaをインストール** → [こちらから入手](https://ollama.com/download)
2. **使用したいモデルをプル：**

```shell
# 20B用
ollama pull gpt-oss:20b

# 120B用
ollama pull gpt-oss:120b
```

## gpt-ossとチャットする

モデルと話す準備はできましたか？アプリまたはターミナルでチャットを開始できます：

```shell
ollama run gpt-oss:20b
```

Ollamaは[OpenAI harmony形式](https://cookbook.openai.com/articles/openai-harmony)を模倣した**チャットテンプレート**を標準で適用します。メッセージを入力して会話を開始してください。

## APIを使用する

Ollamaは**Chat Completions互換API**を公開しているため、OpenAI SDKをほとんど変更せずに使用できます。Pythonの例を以下に示します：

```py
from openai import OpenAI

client = OpenAI(
    base_url="http://localhost:11434/v1",  # ローカルOllama API
    api_key="ollama"                       # ダミーキー
)

response = client.chat.completions.create(
    model="gpt-oss:20b",
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Explain what MXFP4 quantization is."}
    ]
)

print(response.choices[0].message.content)
```

OpenAI SDKを使用したことがある場合、これは即座に馴染みのあるものに感じられるでしょう。

または、[Python](https://github.com/ollama/ollama-python)や[JavaScript](https://github.com/ollama/ollama-js)のOllama SDKを直接使用することもできます。

## ツールの使用（関数呼び出し）

Ollamaは以下のことができます：

- 関数を呼び出す
- **組み込みブラウザツール**を使用する（アプリ内）

Chat Completions経由で関数を呼び出す例：

```py
tools = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "Get current weather in a given city",
            "parameters": {
                "type": "object",
                "properties": {"city": {"type": "string"}},
                "required": ["city"]
            },
        },
    }
]

response = client.chat.completions.create(
    model="gpt-oss:20b",
    messages=[{"role": "user", "content": "What's the weather in Berlin right now?"}],
    tools=tools
)

print(response.choices[0].message)
```

モデルは思考の連鎖（CoT）の一部としてツール呼び出しを実行できるため、APIから返される推論を、モデルが最終的な答えに到達するまで答えを提供するツール呼び出しへの後続の呼び出しに戻すことが重要です。

## Responses APIの回避策

Ollamaは**Responses API**を（まだ）ネイティブサポートしていません。

Responses APIを使用したい場合は、[**Hugging Faceの`Responses.js`プロキシ**](https://github.com/huggingface/responses.js)を使用してChat CompletionsをResponses APIに変換できます。

基本的な使用例では、[**OllamaをバックエンドとしたPythonサーバーの例を実行する**](https://github.com/openai/gpt-oss?tab=readme-ov-file#responses-api)こともできます。このサーバーは基本的な例のサーバーであり、

```shell
pip install gpt-oss
python -m gpt_oss.responses_api.serve \
    --inference_backend=ollama \
    --checkpoint gpt-oss:20b
```

## Agents SDK統合

gpt-ossをOpenAIの**Agents SDK**で使用したいですか？

両方のAgents SDKでは、OpenAIベースクライアントをオーバーライドして、Chat CompletionsまたはローカルモデルのResponses.jsプロキシを使用してOllamaを指すようにできます。または、組み込み機能を使用してAgents SDKをサードパーティモデルに対して指すこともできます。

- **Python:** [LiteLLM](https://openai.github.io/openai-agents-python/models/litellm/)を使用してLiteLLM経由でOllamaにプロキシする
- **TypeScript:** [ollama adapter](https://ai-sdk.dev/providers/community-providers/ollama)と[AI SDK](https://openai.github.io/openai-agents-js/extensions/ai-sdk/)を使用する

LiteLLMを使用したPython Agents SDKの例：

```py
import asyncio
from agents import Agent, Runner, function_tool, set_tracing_disabled
from agents.extensions.models.litellm_model import LitellmModel

set_tracing_disabled(True)

@function_tool
def get_weather(city: str):
    print(f"[debug] getting weather for {city}")
    return f"The weather in {city} is sunny."


async def main(model: str, api_key: str):
    agent = Agent(
        name="Assistant",
        instructions="You only respond in haikus.",
        model=LitellmModel(model="ollama/gpt-oss:120b", api_key=api_key),
        tools=[get_weather],
    )

    result = await Runner.run(agent, "What's the weather in Tokyo?")
    print(result.final_output)

if __name__ == "__main__":
    asyncio.run(main())
```