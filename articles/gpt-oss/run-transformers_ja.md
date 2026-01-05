# Hugging Face Transformersでgpt-ossを実行する方法

Hugging FaceのTransformersライブラリは、大規模言語モデルをローカルまたはサーバー上で読み込んで実行するための柔軟な方法を提供します。このガイドでは、Transformersを使用して[OpenAI gpt-oss-20b](https://huggingface.co/openai/gpt-oss-20b)または[OpenAI gpt-oss-120b](https://huggingface.co/openai/gpt-oss-120b)を実行する方法を説明します。高レベルなパイプラインまたは生のトークンIDを使用した低レベルな`generate`呼び出しの両方について説明します。

[OpenAI gpt-oss-20b](https://huggingface.co/openai/gpt-oss-20b)または[OpenAI gpt-oss-120b](https://huggingface.co/openai/gpt-oss-120b)を高レベルなパイプライン抽象化、低レベルな`generate`呼び出し、および`transformers serve`を使用したローカルでのモデル提供について、Responses APIと互換性のある方法で説明します。

このガイドでは、**Transformers経由でgpt-ossモデルを実行する**様々な最適化された方法について説明します。

ボーナス：transformersを使用してモデルをファインチューニングすることも可能です。[ファインチューニングガイドはこちら](https://cookbook.openai.com/articles/gpt-oss/fine-tune-transformers)をご確認ください。

## モデルを選択する

両方の**gpt-oss**モデルはHugging Faceで利用可能です：

- **`openai/gpt-oss-20b`**
  - MXFP4使用時に約16GBのVRAM要件
  - 単一のハイエンドコンシューマーGPUに最適
- **`openai/gpt-oss-120b`**
  - 60GB以上のVRAMまたはマルチGPUセットアップが必要
  - H100クラスのハードウェアに理想的

両方ともデフォルトで**MXFP4量子化**されています。MXFP4はHopperまたはそれ以降のアーキテクチャでサポートされていることにご注意ください。これには、H100やGB200などのデータセンターGPU、および最新のRTX 50xxファミリーのコンシューマーカードが含まれます。

MXFP4の代わりに`bfloat16`を使用する場合、メモリ消費量は大きくなります（20bパラメータモデルで約48GB）。

## クイックセットアップ

1. **依存関係のインストール**  
   新しいPython環境を作成することをお勧めします。transformers、accelerate、およびMXFP4互換性のためのTritonカーネルをインストールします：

```bash
pip install -U transformers accelerate torch triton==3.4 kernels
```

2. **（オプション）マルチGPUの有効化**  
   大規模モデルを実行する場合は、Accelerateまたはtorchrunを使用してデバイスマッピングを自動的に処理します。

## Open AI Responses / Chat Completionsエンドポイントの作成

サーバーを起動するには、単純に`transformers serve` CLIコマンドを使用します：

```bash
transformers serve
```

サーバーと対話する最も簡単な方法は、transformers chat CLIを使用することです：

```bash
transformers chat localhost:8000 --model-name-or-path openai/gpt-oss-20b
```

または、cURLでHTTPリクエストを送信することもできます：

```bash
curl -X POST http://localhost:8000/v1/responses -H "Content-Type: application/json" -d '{"messages": [{"role": "system", "content": "hello"}], "temperature": 0.9, "max_tokens": 1000, "stream": true, "model": "openai/gpt-oss-20b"}'
```

Cursorやその他のツールとの`transformers serve`の統合など、追加の使用例については、[ドキュメント](https://huggingface.co/docs/transformers/main/serving)で詳しく説明されています。

## パイプラインでのクイック推論

gpt-ossモデルを実行する最も簡単な方法は、Transformersの高レベル`pipeline` APIを使用することです：

```py
from transformers import pipeline

generator = pipeline(
    "text-generation",
    model="openai/gpt-oss-20b",
    torch_dtype="auto",
    device_map="auto"  # 利用可能なGPUに自動配置
)

messages = [
    {"role": "user", "content": "MXFP4量子化とは何かを説明してください。"},
]

result = generator(
    messages,
    max_new_tokens=200,
    temperature=1.0,
)

print(result[0]["generated_text"])
```

## `.generate()`を使用した高度な推論

より多くの制御が必要な場合は、モデルとトークナイザーを手動で読み込んで`.generate()`メソッドを呼び出すことができます：

```py
from transformers import AutoModelForCausalLM, AutoTokenizer

model_name = "openai/gpt-oss-20b"

tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(
    model_name,
    torch_dtype="auto",
    device_map="auto"
)

messages = [
    {"role": "user", "content": "MXFP4量子化とは何かを説明してください。"},
]

inputs = tokenizer.apply_chat_template(
    messages,
    add_generation_prompt=True,
    return_tensors="pt",
    return_dict=True,
).to(model.device)

outputs = model.generate(
    **inputs,
    max_new_tokens=200,
    temperature=0.7
)

print(tokenizer.decode(outputs[0]))
```

## チャットテンプレートとツール呼び出し

OpenAI gpt-ossモデルは、推論やツール呼び出しを含むメッセージの構造化に[harmony response format](https://cookbook.openai.com/article/harmony)を使用します。

プロンプトを構築するには、Transformersの組み込みチャットテンプレートを使用できます。または、より多くの制御のために[openai-harmony library](https://github.com/openai/harmony)をインストールして使用することもできます。

チャットテンプレートを使用するには：

```py
from transformers import AutoModelForCausalLM, AutoTokenizer

model_name = "openai/gpt-oss-20b"

tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(
    model_name,
    device_map="auto",
    torch_dtype="auto",
)

messages = [
    {"role": "system", "content": "常に謎かけで答えてください"},
    {"role": "user", "content": "マドリードの天気はどうですか？"},
]

inputs = tokenizer.apply_chat_template(
    messages,
    add_generation_prompt=True,
    return_tensors="pt",
    return_dict=True,
).to(model.device)

generated = model.generate(**inputs, max_new_tokens=100)
print(tokenizer.decode(generated[0][inputs["input_ids"].shape[-1] :]))
```

[`openai-harmony`](https://github.com/openai/harmony)ライブラリを統合してプロンプトを準備し、レスポンスを解析するには、まず次のようにインストールします：

```bash
pip install openai-harmony
```

ライブラリを使用してプロンプトを構築し、トークンにエンコードする方法の例は次のとおりです：

```py
import json
from openai_harmony import (
    HarmonyEncodingName,
    load_harmony_encoding,
    Conversation,
    Message,
    Role,
    SystemContent,
    DeveloperContent
)
from transformers import AutoModelForCausalLM, AutoTokenizer

encoding = load_harmony_encoding(HarmonyEncodingName.HARMONY_GPT_OSS)

# 会話を構築
convo = Conversation.from_messages([
    Message.from_role_and_content(Role.SYSTEM, SystemContent.new()),
    Message.from_role_and_content(
        Role.DEVELOPER,
        DeveloperContent.new().with_instructions("常に謎かけで答えてください")
    ),
    Message.from_role_and_content(Role.USER, "サンフランシスコの天気はどうですか？")
])

# プロンプトをレンダリング
prefill_ids = encoding.render_conversation_for_completion(convo, Role.ASSISTANT)
stop_token_ids = encoding.stop_tokens_for_assistant_actions()

# モデルを読み込み
model_name = "openai/gpt-oss-20b"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(model_name, torch_dtype="auto", device_map="auto")

# 生成
outputs = model.generate(
    input_ids=[prefill_ids],
    max_new_tokens=128,
    eos_token_id=stop_token_ids
)

# 完了トークンを解析
completion_ids = outputs[0][len(prefill_ids):]
entries = encoding.parse_messages_from_completion_tokens(completion_ids, Role.ASSISTANT)

for message in entries:
    print(json.dumps(message.to_dict(), indent=2))
```

HarmonyのDeveloperロールはチャットテンプレートの`system`プロンプトにマップされることに注意してください。

## マルチGPUと分散推論

大規模なgpt-oss-120bは、MXFP4を使用する場合、単一のH100 GPUに収まります。複数のGPUで実行したい場合は、次のことができます：

- 自動配置とテンソル並列化のために`tp_plan="auto"`を使用
- 分散セットアップのために`accelerate launch`または`torchrun`で起動
- Expert Parallelismを活用
- より高速な推論のために特殊なFlash attentionカーネルを使用

```py
from transformers import AutoModelForCausalLM, AutoTokenizer
from transformers.distributed import DistributedConfig
import torch

model_path = "openai/gpt-oss-120b"
tokenizer = AutoTokenizer.from_pretrained(model_path, padding_side="left")

device_map = {
    # Expert Parallelismを有効化
    "distributed_config": DistributedConfig(enable_expert_parallel=1),
    # Tensor Parallelismを有効化
    "tp_plan": "auto",
}

model = AutoModelForCausalLM.from_pretrained(
    model_path,
    torch_dtype="auto",
    attn_implementation="kernels-community/vllm-flash-attn3",
    **device_map,
)

messages = [
     {"role": "user", "content": "大規模言語モデルにおけるexpert parallelismの仕組みを説明してください。"}
]

inputs = tokenizer.apply_chat_template(
    messages,
    add_generation_prompt=True,
    return_tensors="pt",
    return_dict=True,
).to(model.device)

outputs = model.generate(**inputs, max_new_tokens=1000)

# デコードして出力
response = tokenizer.decode(outputs[0])
print("モデルの応答:", response.split("<|channel|>final<|message|>")[-1].strip())
```

その後、4つのGPUを持つノードで次のように実行できます：

```bash
torchrun --nproc_per_node=4 generate.py
```