# Ollama で gpt-oss をローカルで実行する方法

[**OpenAI gpt-oss**](https://openai.com/open-models) を自分のハードウェアで実行したいですか？このガイドでは、[Ollama](https://ollama.ai) を使用して **gpt-oss-20b** または **gpt-oss-120b** をローカルにセットアップし、オフラインでチャットし、API を通じて使用し、Agents SDK に接続する方法を説明します。

このガイドは、PC や Mac でモデルを実行するようなコンシューマーハードウェアを対象としていることに注意してください。NVIDIA の H100 のような専用 GPU を使用するサーバーアプリケーションの場合は、[vLLM ガイドをご覧ください](https://cookbook.openai.com/articles/gpt-oss/run-vllm)。

## モデルを選択する

Ollama は gpt-oss の両方のモデルサイズをサポートしています：

- **`gpt-oss-20b`**
  - 小さいモデル
  - **≥16GB VRAM** または **ユニファイドメモリ** が最適
  - ハイエンドのコンシューマー GPU または Apple Silicon Mac に最適
- **`gpt-oss-120b`**
  - より大きなフルサイズのモデル
  - **≥60GB VRAM** または **ユニファイドメモリ** が最適
  - マルチ GPU または強力なワークステーションセットアップに最適

**いくつかの注意事項：**

- これらのモデルは、すぐに使える **MXFP4 量子化**されており、現在他の量子化はありません
- VRAM が不足している場合は CPU にオフロードできますが、実行速度が遅くなることが予想されます。

## クイックセットアップ

1. **Ollama をインストール** → [こちらから入手](https://ollama.com/download)
2. **必要なモデルをプル：**

```shell
# 20B の場合
ollama pull gpt-oss:20b

# 120B の場合
ollama pull gpt-oss:120b
```

## gpt-oss とチャットする

モデルと話す準備はできましたか？アプリまたはターミナルでチャットを起動できます：

```shell
ollama run gpt-oss:20b
```

Ollama は、[OpenAI harmony 形式](https://cookbook.openai.com/articles/openai-harmony)を模倣する **chat template** をすぐに適用します。メッセージを入力して会話を開始します。

## API を使用する

Ollama は **Chat Completions 互換 API** を公開しているため、OpenAI SDK を大きく変更することなく使用できます。Python の例を次に示します：

```py
from openai import OpenAI

client = OpenAI(
    base_url="http://localhost:11434/v1",  # ローカル Ollama API
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

以前に OpenAI SDK を使用したことがある場合、これはすぐに馴染みがあるはずです。

または、[Python](https://github.com/ollama/ollama-python) または [JavaScript](https://github.com/ollama/ollama-js) で Ollama SDK を直接使用できます。

## ツールの使用（関数呼び出し）

Ollama は以下ができます：

- 関数を呼び出す
- **組み込みブラウザツール**（アプリ内）を使用する

Chat Completions を介して関数を呼び出す例：

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

モデルは思考の連鎖（CoT）の一部としてツール呼び出しを実行できるため、モデルが最終的な答えに到達するまで、答えを提供するツール呼び出しへの後続の呼び出しに API によって返された推論を返すことが重要です。

## Responses API の回避策

Ollama は（まだ）**Responses API** をネイティブにサポートしていません。

Responses API を使用したい場合は、[**Hugging Face の `Responses.js` プロキシ**](https://github.com/huggingface/responses.js)を使用して、Chat Completions を Responses API に変換できます。

基本的なユースケースの場合は、[**Ollama をバックエンドとして使用する例の Python サーバーを実行する**](https://github.com/openai/gpt-oss?tab=readme-ov-file#responses-api)こともできます。このサーバーは基本的な例のサーバーであり、

```shell
pip install gpt-oss
python -m gpt_oss.responses_api.serve \
    --inference_backend=ollama \
    --checkpoint gpt-oss:20b
```

## Agents SDK 統合

OpenAI の **Agents SDK** で gpt-oss を使用したいですか？

両方の Agents SDK を使用すると、OpenAI ベースクライアントをオーバーライドして、Chat Completions を使用して Ollama を指すか、ローカルモデル用の Responses.js プロキシを指すことができます。または、Agents SDK をサードパーティモデルに対して指すために組み込み機能を使用できます。

- **Python:** [LiteLLM](https://openai.github.io/openai-agents-python/models/litellm/) を使用して、LiteLLM を通じて Ollama にプロキシします
- **TypeScript:** [ollama アダプター](https://ai-sdk.dev/providers/community-providers/ollama)で [AI SDK](https://openai.github.io/openai-agents-js/extensions/ai-sdk/) を使用します

LiteLLM を使用した Python Agents SDK の例を次に示します：

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

