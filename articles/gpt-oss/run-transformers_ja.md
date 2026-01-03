# Hugging Face Transformers で gpt-oss を実行する方法

Hugging Face の Transformers ライブラリは、大規模言語モデルをローカルまたはサーバー上でロードして実行する柔軟な方法を提供します。このガイドでは、高レベルのパイプラインまたは生のトークン ID を使用した低レベルの `generate` 呼び出しのいずれかを使用して、[OpenAI gpt-oss-20b](https://huggingface.co/openai/gpt-oss-20b) または [OpenAI gpt-oss-120b](https://huggingface.co/openai/gpt-oss-120b) を Transformers で実行する方法を説明します。

高レベルのパイプライン抽象化、低レベルの \`generate\` 呼び出し、および Responses API と互換性のある方法で \`transformers serve\` を使用してモデルをローカルで提供する [OpenAI gpt-oss-20b](https://huggingface.co/openai/gpt-oss-20b) または [OpenAI gpt-oss-120b](https://huggingface.co/openai/gpt-oss-120b) の使用について説明します。

このガイドでは、**Transformers を介して gpt-oss モデルを実行する**さまざまな最適化された方法を説明します。

ボーナス：transformers を介してモデルをファインチューニングすることもできます。[ファインチューニングガイドはこちら](https://cookbook.openai.com/articles/gpt-oss/fine-tune-transformers)をご覧ください。

## モデルを選択する

両方の **gpt-oss** モデルは Hugging Face で利用できます：

- **`openai/gpt-oss-20b`**
  - MXFP4 を使用する場合、約16GB の VRAM 要件
  - 単一のハイエンドコンシューマー GPU に最適
- **`openai/gpt-oss-120b`**
  - ≥60GB VRAM またはマルチ GPU セットアップが必要
  - H100 クラスのハードウェアに最適

両方ともデフォルトで **MXFP4 量子化**されています。MXFP4 は Hopper 以降のアーキテクチャでサポートされていることに注意してください。これには、H100 や GB200 などのデータセンター GPU、および最新の RTX 50xx ファミリーのコンシューマーカードが含まれます。

MXFP4 の代わりに `bfloat16` を使用する場合、メモリ消費量は大きくなります（20b パラメータモデルで約48 GB）。

## クイックセットアップ

1. **依存関係をインストール**  
   新しい Python 環境を作成することをお勧めします。transformers、accelerate、および MXFP4 互換性のための Triton カーネルをインストールします：

```bash
pip install -U transformers accelerate torch triton==3.4 kernels
```

2. **（オプション）マルチ GPU を有効にする**  
   大きなモデルを実行している場合は、Accelerate または torchrun を使用して、デバイスマッピングを自動的に処理します。

## Open AI Responses / Chat Completions エンドポイントを作成する

サーバーを起動するには、単に `transformers serve` CLI コマンドを使用します：

```bash
transformers serve
```

サーバーと対話する最も簡単な方法は、transformers chat CLI を使用することです

```bash
transformers chat localhost:8000 --model-name-or-path openai/gpt-oss-20b
```

または、cURL で HTTP リクエストを送信します。例：

```bash
curl -X POST http://localhost:8000/v1/responses -H "Content-Type: application/json" -d '{"messages": [{"role": "system", "content": "hello"}], "temperature": 0.9, "max_tokens": 1000, "stream": true, "model": "openai/gpt-oss-20b"}'
```

Cursor やその他のツールとの `transformers serve` の統合などの追加のユースケースは、[ドキュメント](https://huggingface.co/docs/transformers/main/serving)に詳しく記載されています。

## パイプラインでのクイック推論

gpt-oss モデルを実行する最も簡単な方法は、Transformers の高レベル `pipeline` API を使用することです：

```py
from transformers import pipeline

generator = pipeline(
    "text-generation",
    model="openai/gpt-oss-20b",
    torch_dtype="auto",
    device_map="auto"  # 利用可能な GPU に自動的に配置
)

messages = [
    {"role": "user", "content": "Explain what MXFP4 quantization is."},
]

result = generator(
    messages,
    max_new_tokens=200,
    temperature=1.0,
)

print(result[0]["generated_text"])
```

## `.generate()` を使用した高度な推論

より多くの制御が必要な場合は、モデルとトークナイザーを手動でロードし、`.generate()` メソッドを呼び出すことができます：

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
    {"role": "user", "content": "Explain what MXFP4 quantization is."},
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

## Chat template とツール呼び出し

OpenAI gpt-oss モデルは、推論とツール呼び出しを含むメッセージを構造化するために [harmony レスポンス形式](https://cookbook.openai.com/article/harmony)を使用します。

プロンプトを構築するには、Transformers の組み込み chat template を使用できます。または、より多くの制御のために [openai-harmony ライブラリ](https://github.com/openai/harmony)をインストールして使用できます。

chat template を使用するには：

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
    {"role": "system", "content": "Always respond in riddles"},
    {"role": "user", "content": "What is the weather like in Madrid?"},
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

プロンプトを準備し、応答を解析するために [`openai-harmony`](https://github.com/openai/harmony) ライブラリを統合するには、まず次のようにインストールします：

```bash
pip install openai-harmony
```

ライブラリを使用してプロンプトを構築し、トークンにエンコードする方法の例を次に示します：

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
        DeveloperContent.new().with_instructions("Always respond in riddles")
    ),
    Message.from_role_and_content(Role.USER, "What is the weather like in SF?")
])

# プロンプトをレンダリング
prefill_ids = encoding.render_conversation_for_completion(convo, Role.ASSISTANT)
stop_token_ids = encoding.stop_tokens_for_assistant_actions()

# モデルをロード
model_name = "openai/gpt-oss-20b"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(model_name, torch_dtype="auto", device_map="auto")

# 生成
outputs = model.generate(
    input_ids=[prefill_ids],
    max_new_tokens=128,
    eos_token_id=stop_token_ids
)

# 補完トークンを解析
completion_ids = outputs[0][len(prefill_ids):]
entries = encoding.parse_messages_from_completion_tokens(completion_ids, Role.ASSISTANT)

for message in entries:
    print(json.dumps(message.to_dict(), indent=2))
```

Harmony の `Developer` ロールは、chat template の `system` プロンプトにマッピングされることに注意してください。

## マルチ GPU と分散推論

大きな gpt-oss-120b は、MXFP4 を使用する場合、単一の H100 GPU に収まります。複数の GPU で実行したい場合は、次のことができます：

- 自動配置とテンソル並列化のために `tp_plan="auto"` を使用する
- 分散セットアップのために `accelerate launch または torchrun` で起動する
- Expert Parallelism を活用する
- より高速な推論のために特殊な Flash attention カーネルを使用する

```py
from transformers import AutoModelForCausalLM, AutoTokenizer
from transformers.distributed import DistributedConfig
import torch

model_path = "openai/gpt-oss-120b"
tokenizer = AutoTokenizer.from_pretrained(model_path, padding_side="left")

device_map = {
    # Expert Parallelism を有効にする
    "distributed_config": DistributedConfig(enable_expert_parallel=1),
    # Tensor Parallelism を有効にする
    "tp_plan": "auto",
}

model = AutoModelForCausalLM.from_pretrained(
    model_path,
    torch_dtype="auto",
    attn_implementation="kernels-community/vllm-flash-attn3",
    **device_map,
)

messages = [
     {"role": "user", "content": "Explain how expert parallelism works in large language models."}
]

inputs = tokenizer.apply_chat_template(
    messages,
    add_generation_prompt=True,
    return_tensors="pt",
    return_dict=True,
).to(model.device)

outputs = model.generate(**inputs, max_new_tokens=1000)

# デコードして印刷
response = tokenizer.decode(outputs[0])
print("Model response:", response.split("<|channel|>final<|message|>")[-1].strip())
```

次に、4つの GPU を持つノードで次のように実行できます

```bash
torchrun --nproc_per_node=4 generate.py
```

