# vLLM で gpt-oss を実行する方法

[vLLM](https://docs.vllm.ai/en/latest/) は、メモリ使用量と処理速度を最適化することで、大規模言語モデル（LLM）を効率的に提供するように設計されたオープンソースの高スループット推論エンジンです。このガイドでは、vLLM を使用してサーバー上で **gpt-oss-20b** または **gpt-oss-120b** をセットアップし、アプリケーション用の API として gpt-oss を提供し、Agents SDK に接続する方法を説明します。

このガイドは、NVIDIA の H100 のような専用 GPU を使用するサーバーアプリケーションを対象としていることに注意してください。コンシューマー GPU でのローカル推論については、[Ollama](https://cookbook.openai.com/articles/gpt-oss/run-locally-ollama) または [LM Studio](https://cookbook.openai.com/articles/gpt-oss/run-locally-lmstudio) ガイドをご覧ください。

## モデルを選択する

vLLM は gpt-oss の両方のモデルサイズをサポートしています：

- [**`openai/gpt-oss-20b`**](https://huggingface.co/openai/gpt-oss-20b)
  - 小さいモデル
  - 約 **16GB の VRAM** のみが必要
- [**`openai/gpt-oss-120b`**](https://huggingface.co/openai/gpt-oss-120b)
  - より大きなフルサイズのモデル
  - **≥60GB VRAM** が最適
  - 単一の H100 またはマルチ GPU セットアップに収まる

両方のモデルは、すぐに使える **MXFP4 量子化**されています。

## クイックセットアップ

1. **vLLM をインストール**  
   vLLM は、Python 環境を管理するために [uv](https://docs.astral.sh/uv/) を使用することを推奨しています。これにより、環境に基づいて適切な実装を選択するのに役立ちます。[クイックスタートで詳細をご覧ください](https://docs.vllm.ai/en/latest/getting_started/quickstart.html#installation)。新しい仮想環境を作成し、vLLM をインストールするには、次を実行します：

```shell
uv venv --python 3.12 --seed
source .venv/bin/activate
uv pip install --pre vllm==0.10.1+gptoss \
    --extra-index-url https://wheels.vllm.ai/gpt-oss/ \
    --extra-index-url https://download.pytorch.org/whl/nightly/cu128 \
    --index-strategy unsafe-best-match
```

2. **サーバーを起動してモデルをダウンロード**  
   vLLM は、HuggingFace からモデルを自動的にダウンロードし、`localhost:8000` で OpenAI 互換サーバーを起動する `serve` コマンドを提供します。サーバー上のターミナルセッションで、希望するモデルサイズに応じて次のコマンドを実行します。

```shell
# 20B の場合
vllm serve openai/gpt-oss-20b

# 120B の場合
vllm serve openai/gpt-oss-120b
```

## API を使用する

vLLM は **Chat Completions 互換 API** と **Responses 互換 API** を公開しているため、OpenAI SDK を大きく変更することなく使用できます。Python の例を次に示します：

```py
from openai import OpenAI

client = OpenAI(
    base_url="http://localhost:8000/v1",
    api_key="EMPTY"
)

result = client.chat.completions.create(
    model="openai/gpt-oss-20b",
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Explain what MXFP4 quantization is."}
    ]
)

print(result.choices[0].message.content)

response = client.responses.create(
    model="openai/gpt-oss-120b",
    instructions="You are a helfpul assistant.",
    input="Explain what MXFP4 quantization is."
)

print(response.output_text)
```

以前に OpenAI SDK を使用したことがある場合、これはすぐに馴染みがあり、ベース URL を変更するだけで既存のコードが機能するはずです。

## ツールの使用（関数呼び出し）

vLLM は関数呼び出しとモデルにブラウジング機能を提供することをサポートしています。

関数呼び出しは、Responses と Chat Completions API の両方を通じて機能します。

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
    model="openai/gpt-oss-120b",
    messages=[{"role": "user", "content": "What's the weather in Berlin right now?"}],
    tools=tools
)

print(response.choices[0].message)
```

モデルは思考の連鎖（CoT）の一部としてツール呼び出しを実行できるため、モデルが最終的な答えに到達するまで、答えを提供するツール呼び出しへの後続の呼び出しに API によって返された推論を返すことが重要です。

## Agents SDK 統合

OpenAI の **Agents SDK** で gpt-oss を使用したいですか？

両方の Agents SDK を使用すると、OpenAI ベースクライアントをオーバーライドして、セルフホストモデル用の vLLM を指すことができます。または、Python SDK の場合は、[LiteLLM 統合](https://openai.github.io/openai-agents-python/models/litellm/)を使用して vLLM にプロキシすることもできます。

Python Agents SDK の例を次に示します：

```
uv pip install openai-agents
```

```py
import asyncio
from openai import AsyncOpenAI
from agents import Agent, Runner, function_tool, OpenAIResponsesModel, set_tracing_disabled

set_tracing_disabled(True)

@function_tool
def get_weather(city: str):
    print(f"[debug] getting weather for {city}")
    return f"The weather in {city} is sunny."


async def main(model: str, api_key: str):
    agent = Agent(
        name="Assistant",
        instructions="You only respond in haikus.",
        model=OpenAIResponsesModel(
            model="openai/gpt-oss-120b",
            openai_client=AsyncOpenAI(
                base_url="http://localhost:8000/v1",
                api_key="EMPTY",
            ),
        )
        tools=[get_weather],
    )

    result = await Runner.run(agent, "What's the weather in Tokyo?")
    print(result.final_output)

if __name__ == "__main__":
    asyncio.run(main())
```

## 直接サンプリングのための vLLM の使用

API サーバーとして `vllm serve` を使用して vLLM を実行するほかに、vLLM Python ライブラリを使用して推論を直接制御できます。

直接サンプリングのために vLLM を使用している場合、入力プロンプトが [harmony レスポンス形式](https://cookbook.openai.com/article/harmony)に従っていることを確認することが重要です。そうしないと、モデルは正しく機能しません。このために [`openai-harmony` SDK](https://github.com/openai/harmony) を使用できます。

```
uv pip install openai-harmony
```

その後、harmony を使用して、vLLM の generate 関数によって生成されたトークンをエンコードおよび解析できます。

```py
import json
from openai_harmony import (
    HarmonyEncodingName,
    load_harmony_encoding,
    Conversation,
    Message,
    Role,
    SystemContent,
    DeveloperContent,
)

from vllm import LLM, SamplingParams

# --- 1) Harmony でプリフィルをレンダリング ---
encoding = load_harmony_encoding(HarmonyEncodingName.HARMONY_GPT_OSS)

convo = Conversation.from_messages(
    [
        Message.from_role_and_content(Role.SYSTEM, SystemContent.new()),
        Message.from_role_and_content(
            Role.DEVELOPER,
            DeveloperContent.new().with_instructions("Always respond in riddles"),
        ),
        Message.from_role_and_content(Role.USER, "What is the weather like in SF?"),
    ]
)

prefill_ids = encoding.render_conversation_for_completion(convo, Role.ASSISTANT)

# Harmony 停止トークン（出力に含まれないようにサンプラーに渡す）
stop_token_ids = encoding.stop_tokens_for_assistant_actions()

# --- 2) プリフィルで vLLM を実行 ---
llm = LLM(
    model="openai/gpt-oss-120b",
    trust_remote_code=True,
)

sampling = SamplingParams(
    max_tokens=128,
    temperature=1,
    stop_token_ids=stop_token_ids,
)

outputs = llm.generate(
    prompt_token_ids=[prefill_ids],   # サイズ1のバッチ
    sampling_params=sampling,
)

# vLLM はテキストとトークン ID の両方を提供
gen = outputs[0].outputs[0]
text = gen.text
output_tokens = gen.token_ids  # <-- これらは補完トークン ID（プリフィルなし）

# --- 3) 補完トークン ID を構造化された Harmony メッセージに解析 ---
entries = encoding.parse_messages_from_completion_tokens(output_tokens, Role.ASSISTANT)

# 'entries' は構造化された会話エントリのシーケンス（アシスタントメッセージ、ツール呼び出しなど）。
for message in entries:
    print(f"{json.dumps(message.to_dict())}")
```

