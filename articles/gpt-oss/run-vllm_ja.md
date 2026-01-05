# vLLMでgpt-ossを実行する方法

[vLLM](https://docs.vllm.ai/en/latest/)は、メモリ使用量と処理速度を最適化することで大規模言語モデル（LLM）を効率的に提供するよう設計された、オープンソースの高スループット推論エンジンです。このガイドでは、vLLMを使用してサーバー上で**gpt-oss-20b**または**gpt-oss-120b**をセットアップし、アプリケーション用のAPIとしてgpt-ossを提供し、さらにAgents SDKに接続する方法について説明します。

このガイドは、NVIDIA H100などの専用GPUを搭載したサーバーアプリケーション向けであることにご注意ください。コンシューマー向けGPUでのローカル推論については、[Ollama](https://cookbook.openai.com/articles/gpt-oss/run-locally-ollama)または[LM Studio](https://cookbook.openai.com/articles/gpt-oss/run-locally-lmstudio)のガイドをご確認ください。

## モデルを選択する

vLLMはgpt-ossの両方のモデルサイズをサポートしています：

- [**`openai/gpt-oss-20b`**](https://huggingface.co/openai/gpt-oss-20b)
  - 小さいモデル
  - 約**16GBのVRAM**のみ必要
- [**`openai/gpt-oss-120b`**](https://huggingface.co/openai/gpt-oss-120b)
  - より大きなフルサイズモデル
  - **≥60GB VRAM**が最適
  - 単一のH100またはマルチGPU構成に適合可能

両方のモデルは**MXFP4量子化**が標準で適用されています。

## クイックセットアップ

1. **vLLMをインストール**  
   vLLMでは、Python環境の管理に[uv](https://docs.astral.sh/uv/)の使用を推奨しています。これにより、環境に基づいて適切な実装を選択できます。[詳細はクイックスタートガイドをご覧ください](https://docs.vllm.ai/en/latest/getting_started/quickstart.html#installation)。新しい仮想環境を作成してvLLMをインストールするには、以下を実行してください：

```shell
uv venv --python 3.12 --seed
source .venv/bin/activate
uv pip install --pre vllm==0.10.1+gptoss \
    --extra-index-url https://wheels.vllm.ai/gpt-oss/ \
    --extra-index-url https://download.pytorch.org/whl/nightly/cu128 \
    --index-strategy unsafe-best-match
```

2. **サーバーを起動してモデルをダウンロード**  
   vLLMは`serve`コマンドを提供しており、HuggingFaceからモデルを自動的にダウンロードし、`localhost:8000`でOpenAI互換サーバーを起動します。サーバーのターミナルセッションで、希望するモデルサイズに応じて以下のコマンドを実行してください。

```shell
# 20B用
vllm serve openai/gpt-oss-20b

# 120B用
vllm serve openai/gpt-oss-120b
```

## APIを使用する

vLLMは**Chat Completions互換API**と**Responses互換API**を公開しているため、大きな変更なしにOpenAI SDKを使用できます。Pythonの例を以下に示します：

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

OpenAI SDKを以前に使用したことがある場合、これは即座に馴染みやすく感じられ、ベースURLを変更するだけで既存のコードが動作するはずです。

## ツールの使用（関数呼び出し）

vLLMは関数呼び出しとモデルにブラウジング機能を提供することをサポートしています。

関数呼び出しはResponsesとChat Completions APIの両方で動作します。

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
    model="openai/gpt-oss-120b",
    messages=[{"role": "user", "content": "What's the weather in Berlin right now?"}],
    tools=tools
)

print(response.choices[0].message)
```

モデルは思考の連鎖（CoT）の一部としてツール呼び出しを実行できるため、APIから返された推論を、答えを提供するツール呼び出しへの後続の呼び出しに戻し、モデルが最終的な答えに到達するまで続けることが重要です。

## Agents SDK統合

OpenAIの**Agents SDK**でgpt-ossを使用したいですか？

Agents SDKでは、OpenAIベースクライアントをオーバーライドして、セルフホストモデル用のvLLMを指すことができます。また、Python SDKの場合は、[LiteLLM統合](https://openai.github.io/openai-agents-python/models/litellm/)を使用してvLLMにプロキシすることも可能です。

Python Agents SDKの例を以下に示します：

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

## 直接サンプリングでのvLLMの使用

APIサーバーとして`vllm serve`を使用してvLLMを実行する以外に、vLLM Pythonライブラリを使用して推論を直接制御することができます。

vLLMを直接サンプリングに使用する場合、入力プロンプトが[harmony response format](https://cookbook.openai.com/article/harmony)に従っていることを確認することが重要です。そうでなければモデルが正しく機能しません。これには[`openai-harmony` SDK](https://github.com/openai/harmony)を使用できます。

```
uv pip install openai-harmony
```

その後、harmonyを使用してvLLMのgenerate関数によって生成されたトークンをエンコードおよび解析できます。

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

# --- 1) Harmonyでプリフィルをレンダリング ---
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

# Harmony停止トークン（出力に含まれないようサンプラーに渡す）
stop_token_ids = encoding.stop_tokens_for_assistant_actions()

# --- 2) プリフィルでvLLMを実行 ---
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

# vLLMはテキストとトークンIDの両方を提供
gen = outputs[0].outputs[0]
text = gen.text
output_tokens = gen.token_ids  # <-- これらは完了トークンID（プリフィルなし）

# --- 3) 完了トークンIDを構造化されたHarmonyメッセージに解析 ---
entries = encoding.parse_messages_from_completion_tokens(output_tokens, Role.ASSISTANT)

# 'entries'は構造化された会話エントリ（アシスタントメッセージ、ツール呼び出しなど）のシーケンス
for message in entries:
    print(f"{json.dumps(message.to_dict())}")
```