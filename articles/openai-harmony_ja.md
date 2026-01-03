# OpenAI harmony レスポンス形式

[`gpt-oss` モデル](https://openai.com/open-models)は、会話構造の定義、推論出力の生成、関数呼び出しの構造化のために harmony レスポンス形式で訓練されました。`gpt-oss` を直接使用するのではなく、API や Ollama などのプロバイダーを通じて使用している場合は、推論ソリューションがフォーマットを処理するため、これについて心配する必要はありません。独自の推論ソリューションを構築している場合、このガイドはプロンプト形式を説明します。この形式は OpenAI Responses API を模倣するように設計されているため、その API を使用したことがある場合は、この形式は馴染みがあるはずです。`gpt-oss` は harmony 形式を使用せずに使用すべきではありません。正しく動作しません。

## 概念

### ロール

モデルが処理するすべてのメッセージには、関連付けられたロールがあります。モデルは5種類のロールについて知っています：

| ロール        | 目的                                                                                                                                                                                 |
| :---------- | :-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `system`    | システムメッセージは、推論努力、知識カットオフや組み込みツールなどのメタ情報を指定するために使用されます                                                                         |
| `developer` | 開発者メッセージは、モデルの指示（通常「システムプロンプト」と見なされるもの）と利用可能な関数ツールに関する情報を提供するために使用されます                |
| `user`      | 通常、モデルへの入力を表します                                                                                                                                           |
| `assistant` | モデルによって出力され、ツール呼び出しまたはメッセージ出力のいずれかになります。出力は、メッセージの意図を識別する特定の「チャネル」に関連付けられる場合もあります。 |
| `tool`      | ツール呼び出しの出力を表すメッセージ。特定のツール名がメッセージ内のロールとして使用されます。                                                                      |

これらのロールは、指示の競合がある場合にモデルが適用する情報階層も表します：`system` \> `developer` \> `user` \> `assistant` \> `tool`

#### チャネル

アシスタントメッセージは、3つの異なる「チャネル」で出力できます。これらは、ユーザー向けレスポンスと内部向けメッセージを分離するために使用されています。

| チャネル      | 目的                                                                                                                                                                                                                                                                                                                                                            |
| :----------- | :----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `final`      | final チャネルでタグ付けされたメッセージは、エンドユーザーに表示されることを意図したメッセージであり、モデルからの応答を表します。                                                                                                                                                                                                                                 |
| `analysis`   | これらは、モデルが思考の連鎖（CoT）に使用しているメッセージです。**重要：** analysis チャネルのメッセージは、final メッセージと同じ安全基準に準拠していません。これらをエンドユーザーに表示することは避けてください。                                                                                                                             |
| `commentary` | 関数ツール呼び出しは通常 `commentary` チャネルでトリガーされますが、組み込みツールは通常 `analysis` チャネルでトリガーされます。ただし、組み込みツールが `commentary` に出力されることもあります。時折、このチャネルは、複数の関数を呼び出すための[プリアンブル](#preambles)を生成するためにモデルによって使用されることもあります。 |

## Harmony レンダラーライブラリ

可能な限り、[PyPI](https://pypi.org/project/openai-harmony/) または [crates.io](https://crates.io/crates/openai-harmony) を通じて harmony レンダラーを使用することをお勧めします。これにより、メッセージを正しい形式でレンダリングし、モデルによる処理のためにトークンに変換することが自動的に処理されます。

以下は、レンダラーを使用してシステムプロンプトと短い会話を構築する例です。

```py
from openai_harmony import (
    Author,
    Conversation,
    DeveloperContent,
    HarmonyEncodingName,
    Message,
    Role,
    SystemContent,
    ToolDescription,
    load_harmony_encoding,
    ReasoningEffort
)

encoding = load_harmony_encoding(HarmonyEncodingName.HARMONY_GPT_OSS)

system_message = (
    SystemContent.new()
        .with_reasoning_effort(ReasoningEffort.HIGH)
        .with_conversation_start_date("2025-06-28")
)

developer_message = (
    DeveloperContent.new()
        .with_instructions("Always respond in riddles")
        .with_function_tools(
            [
                ToolDescription.new(
                    "get_current_weather",
                    "Gets the current weather in the provided location.",
                    parameters={
                        "type": "object",
                        "properties": {
                            "location": {
                                "type": "string",
                                "description": "The city and state, e.g. San Francisco, CA",
                            },
                            "format": {
                                "type": "string",
                                "enum": ["celsius", "fahrenheit"],
                                "default": "celsius",
                            },
                        },
                        "required": ["location"],
                    },
                ),
            ]
	)
)

convo = Conversation.from_messages(
    [
        Message.from_role_and_content(Role.SYSTEM, system_message),
        Message.from_role_and_content(Role.DEVELOPER, developer_message),
        Message.from_role_and_content(Role.USER, "What is the weather in Tokyo?"),
        Message.from_role_and_content(
            Role.ASSISTANT,
            'User asks: "What is the weather in Tokyo?" We need to use get_current_weather tool.',
        ).with_channel("analysis"),
        Message.from_role_and_content(Role.ASSISTANT, '{"location": "Tokyo"}')
        .with_channel("commentary")
        .with_recipient("functions.get_current_weather")
        .with_content_type("<|constrain|> json"),
        Message.from_author_and_content(
            Author.new(Role.TOOL, "functions.get_current_weather"),
            '{ "temperature": 20, "sunny": true }',
        ).with_channel("commentary"),
    ]
)

tokens = encoding.render_conversation_for_completion(convo, Role.ASSISTANT)

# After receiving a token response
# Do not pass in the stop token
parsed_response = encoding.parse_messages_from_completion_tokens(new_tokens, Role.ASSISTANT)
```

さらに、openai_harmony ライブラリには、モデルが新しいトークンを生成している間に解析とデコードを行うための StreamableParser も含まれています。これは、たとえば、出力をストリーミングし、デコード中に Unicode 文字を処理するのに役立ちます。

```py
from openai_harmony import (
    load_harmony_encoding,
    Role,
    StreamableParser,
    HarmonyEncodingName
)

encoding = load_harmony_encoding(HarmonyEncodingName.HARMONY_GPT_OSS)
stream = StreamableParser(encoding, role=Role.ASSISTANT)

tokens = [
    200005,35644,200008,1844,31064,25,392,4827,382,220,17,659,220,17,16842,12295,81645,
    13,51441,6052,13,200007,200006,173781,200005,17196,200008,17,659,220,17,314,220,19,
    13,200002
]

for token in tokens:
    stream.process(token)
    print("--------------------------------")
    print("current_role", stream.current_role)
    print("current_channel", stream.current_channel)
    print("last_content_delta", stream.last_content_delta)
    print("current_content_type", stream.current_content_type)
    print("current_recipient", stream.current_recipient)
    print("current_content", stream.current_content)
```

## プロンプト形式

独自のレンダラーを構築する場合は、以下の形式に従う必要があります。

### 特殊トークン

モデルは、入力の構造を識別するために一連の特殊トークンを使用します。[tiktoken](https://github.com/openai/tiktoken) を使用している場合、これらのトークンは `o200k_harmony` エンコーディングでエンコードされます。すべての特殊トークンは `<|type|>` の形式に従います。

| 特殊トークン           | 目的                                                                                                                                     | トークン ID |
| :---------------------- | :------------------------------------------------------------------------------------------------------------------------------------------ | :------- |
| <&#124;start&#124;>     | [メッセージ](#message-format)の開始を示します。[ロール](#roles)から始まるメッセージの「ヘッダー」情報が続きます | `200006` |
| <&#124;end&#124;>       | [メッセージ](#message-format)の終了を示します                                                                                           | `200007` |
| <&#124;message&#124;>   | メッセージ「ヘッダー」から実際のコンテンツへの移行を示します                                                                    | `200008` |
| <&#124;channel&#124;>   | ヘッダーの[チャネル](#channels)情報への移行を示します                                                              | `200005` |
| <&#124;constrain&#124;> | [ツール呼び出し](#receiving-tool-calls)のデータ型定義への移行を示します                                                | `200003` |
| <&#124;return&#124;>    | モデルが応答メッセージのサンプリングを完了したことを示します。推論を停止すべきことを示す有効な「停止トークン」です。             | `200002` |
| <&#124;call&#124;>      | モデルがツールを呼び出したいことを示します。推論を停止すべきことを示す有効な「停止トークン」です。                   | `200012` |

### メッセージ形式

harmony レスポンス形式は「メッセージ」で構成され、モデルは一度に複数のメッセージを生成する可能性があります。メッセージの一般的な構造は次のとおりです：

```
<|start|>{header}<|message|>{content}<|end|>
```

`{header}` には、[ロール](#roles)を含む一連のメタ情報が含まれます。`<|end|>` は完全に完了したメッセージの終わりを表しますが、モデルはツール呼び出しのための `<|call|>` や、モデルが補完を完了したことを示す `<|return|>` などの他の停止トークンも使用する場合があります。

### チャット会話形式

上記のメッセージ形式に従って、最も基本的なチャット形式は、`user` メッセージと `assistant` メッセージの開始で構成されます。

#### 入力例

```
<|start|>user<|message|>What is 2 + 2?<|end|>
<|start|>assistant
```

出力は `channel` を指定することから始まります。たとえば、思考の連鎖を出力するための `analysis` です。モデルは複数のメッセージ（主に思考の連鎖メッセージ）を出力する場合があり、それらを分離するために `<|end|>` トークンを使用します。

生成が完了すると、最終的な答えの生成が完了したことを示す `<|return|>` トークン、またはツール呼び出しを実行する必要があることを示す `<|call|>` のいずれかで停止します。いずれの場合も、これは推論を停止すべきことを示します。

#### 出力例

```
<|channel|>analysis<|message|>User asks: "What is 2 + 2?" Simple arithmetic. Provide answer.<|end|>
<|start|>assistant<|channel|>final<|message|>2 + 2 = 4.<|return|>
```

`final` チャネルには、ユーザーのリクエストへの答えが含まれます。思考の連鎖の詳細については、[推論セクション](#reasoning)をご覧ください。

**実装上の注意：** `<|return|>` はデコード時の停止トークンのみです。次のターンのために会話履歴にアシスタントの生成された返信を追加する場合は、末尾の `<|return|>` を `<|end|>` に置き換えて、保存されたメッセージが `<|start|>{header}<|message|>{content}<|end|>` として完全に形成されるようにします。したがって、プロンプト内の以前のメッセージは `<|end|>` で終わる必要があります。教師あり対象/トレーニング例の場合、`<|return|>` で終わることが適切です。永続化された履歴の場合は、`<|end|>` に正規化します。

### システムメッセージ形式

システムメッセージは、システムに一般的な情報を提供するために使用されます。これは、他のプロンプト形式で「システムプロンプト」と見なされるものとは異なります。それについては、[開発者メッセージ形式](#developer-message-format)をご覧ください。

システムメッセージを使用して以下を定義します：

1. モデルの**アイデンティティ** — これは常に `You are ChatGPT, a large language model trained by OpenAI.` のままにしておく必要があります。モデルのアイデンティティを変更したい場合は、[開発者メッセージ](#developer-message-format)の指示を使用してください。
2. メタ**日付** — 具体的には `Knowledge cutoff:` と `Current date:`
3. **推論努力** — `high`、`medium`、`low` のレベルで指定されます
4. 利用可能なチャネル — 最高のパフォーマンスのために、これは `analysis`、`commentary`、`final` にマッピングする必要があります。
5. 組み込みツール — モデルは `python` と `browser` ツールの両方で訓練されています。詳細については、[組み込みツールセクション](#built-in-tools)をご覧ください。

**関数を定義している場合**、すべての関数ツール呼び出しが `commentary` チャネルに行く必要があるという注記も含める必要があります。

最高のパフォーマンスのために、この形式にできるだけ忠実に従ってください。

#### システムメッセージの例

使用すべき最も基本的なシステムメッセージは次のとおりです：

```
<|start|>system<|message|>You are ChatGPT, a large language model trained by OpenAI.
Knowledge cutoff: 2024-06
Current date: 2025-06-28

Reasoning: high

# Valid channels: analysis, commentary, final. Channel must be included for every message.<|end|>
```

関数呼び出しが開発者メッセージセクションに存在する場合は、次を使用します：

```
<|start|>system<|message|>You are ChatGPT, a large language model trained by OpenAI.
Knowledge cutoff: 2024-06
Current date: 2025-06-28

Reasoning: high

# Valid channels: analysis, commentary, final. Channel must be included for every message.
Calls to these tools must go to the commentary channel: 'functions'.<|end|>
```

### 開発者メッセージ形式

開発者メッセージは、一般的に「システムプロンプト」と見なされるものを表します。これには、モデルに提供される指示と、オプションで使用可能な[関数ツール](#function-calling)のリストまたは[構造化出力](#structured-output)のためにモデルが準拠すべき出力形式が含まれます。

関数ツール呼び出しを使用していない場合、開発者メッセージは次のようになります：

```
<|start|>developer<|message|># Instructions

{instructions}<|end|>
```

ここで、`{instructions}` は「システムプロンプト」に置き換えられます。

関数呼び出しツールの定義については、[専用セクション](#function-calling)をご覧ください。  
構造化出力で使用される出力形式の定義については、[ガイドのこのセクション](#structured-output)をご覧ください。

### 推論

gpt-oss モデルは推論モデルです。デフォルトでは、モデルは中程度のレベルの推論を行います。推論を制御するには、[システムメッセージ](#system-message-format)で推論レベルを `low`、`medium`、または `high` として指定できます。推奨される形式は次のとおりです：

```
Reasoning: high
```

モデルは、生の思考の連鎖（CoT）をアシスタントメッセージとして `analysis` チャネルに出力し、最終的な応答は `final` として出力されます。

たとえば、質問 `What is 2 + 2?` の場合、モデルの出力は次のようになる場合があります：

```
<|channel|>analysis<|message|>User asks: "What is 2 + 2?" Simple arithmetic. Provide answer.<|end|>
<|start|>assistant<|channel|>final<|message|>2 + 2 = 4.<|return|>
```

この場合、CoT は次のとおりです：

```
User asks: "What is 2 + 2?" Simple arithmetic. Provide answer.
```

そして、実際の答えは次のとおりです：

```
2 + 2 = 4
```

**重要：**  
モデルは、最終出力と同じ安全基準で思考の連鎖を訓練されていません。ユーザーに思考の連鎖を表示すべきではありません。有害なコンテンツが含まれている可能性があります。[モデルカードで詳細をご覧ください](https://openai.com/index/gpt-oss-model-card/)。

#### 後続のサンプリングでの推論出力の処理

一般的に、アシスタントによる応答が `final` チャネルへのメッセージで終了した場合、後続のサンプリングで以前の CoT コンテンツをドロップする必要があります。つまり、最初の入力が次の場合：

```
<|start|>user<|message|>What is 2 + 2?<|end|>
<|start|>assistant
```

そして、次の出力が得られた場合：

```
<|channel|>analysis<|message|>User asks: "What is 2 + 2?" Simple arithmetic. Provide answer.<|end|>
<|start|>assistant<|channel|>final<|message|>2 + 2 = 4.<|return|>
```

モデルが正しく動作するためには、次のサンプリングの入力は次のようになる必要があります：

```
<|start|>user<|message|>What is 2 + 2?<|end|>
<|start|>assistant<|channel|>final<|message|>2 + 2 = 4.<|end|>
<|start|>user<|message|>What about 9 / 2?<|end|>
<|start|>assistant
```

これの例外は、ツール/関数呼び出しです。モデルは思考の連鎖の一部としてツールを呼び出すことができるため、後続のサンプリングの入力として以前の思考の連鎖を渡す必要があります。完全な例については、[関数呼び出しセクション](#function-calling)をご覧ください。

### 関数呼び出し

#### 利用可能なツールの定義

モデルが利用できるすべての関数は、専用の `Tools` セクションで[開発者メッセージ](#developer-message-format)に定義する必要があります。

関数を定義するには、TypeScript のような型構文を使用し、関数を専用の `functions` 名前空間にラップします。関数呼び出しの精度を向上させるために、この形式に忠実に従うことが重要です。引数の JSON スキーマ定義をこの形式に変換する方法の詳細については、harmony レンダラーのコードベースを確認できますが、一般的なフォーマットの慣行は次のとおりです：

- 引数を受け取らない場合は、すべての関数を `type {function_name} = () => any` として定義します
- 引数を受け取る関数の場合は、引数に `_` という名前を付け、型定義をインライン化します
- フィールド定義の上の行に説明のコメントを追加します
- 常に戻り値の型として `any` を使用します
- 各関数定義の後に空行を保持します
- 関数を名前空間にラップします。一般的に `functions` は、モデルが訓練された可能性のある[他のツール](#built-in-tools)と競合しないように使用すべき名前空間です。

以下は、2つの関数の定義を含む完全な入力例です：

```
<|start|>system<|message|>You are ChatGPT, a large language model trained by OpenAI.
Knowledge cutoff: 2024-06
Current date: 2025-06-28

Reasoning: high

# Valid channels: analysis, commentary, final. Channel must be included for every message.
Calls to these tools must go to the commentary channel: 'functions'.<|end|><|start|>developer<|message|># Instructions

Use a friendly tone.

# Tools

## functions

namespace functions {

// Gets the location of the user.
type get_location = () => any;

// Gets the current weather in the provided location.
type get_current_weather = (_: {
// The city and state, e.g. San Francisco, CA
location: string,
format?: "celsius" | "fahrenheit", // default: celsius
}) => any;

// Gets the current weather in the provided list of locations.
type get_multiple_weathers = (_: {
// List of city and state, e.g. ["San Francisco, CA", "New York, NY"]
locations: string[],
format?: "celsius" | "fahrenheit", // default: celsius
}) => any;

} // namespace functions<|end|><|start|>user<|message|>What is the weather like in SF?<|end|><|start|>assistant
```

#### ツール呼び出しの受信

モデルがツールを呼び出すことを決定した場合、メッセージのヘッダーで `to={name}` 形式を使用して `recipient` を定義します。たとえば、上記の `get_current_weather` 関数をトリガーすることを決定した場合、ヘッダーで `to=functions.get_current_weather` を指定し、[システムメッセージ](#system-message-format)で指定されているように、チャネルとして `commentary` を指定します。**recipient は、ヘッダーのロールまたはチャネルセクションで定義される場合があります。**

モデルは、ツール呼び出しの入力の型を示すために `<|constrain|>` トークンを指定する場合もあります。この場合、JSON として渡されるため、`<|constrain|>` は `json` に設定されます。

```
<|channel|>analysis<|message|>Need to use function get_current_weather.<|end|><|start|>assistant<|channel|>commentary to=functions.get_current_weather <|constrain|>json<|message|>{"location":"San Francisco"}<|call|>
```

#### ツール呼び出しの処理

関数呼び出しが処理された後、呼び出しメッセージの後に出力を含む新しいツールメッセージを指定して、モデルに出力を提供する必要があります。

ツールメッセージの形式は次のとおりです：

```
<|start|>{toolname} to=assistant<|channel|>commentary<|message|>{output}<|end|>
```

したがって、上記の例では次のようになります：

```
<|start|>functions.get_current_weather to=assistant<|channel|>commentary<|message|>{"sunny": true, "temperature": 20}<|end|>
```

ツール呼び出しの出力を収集したら、完全なコンテンツで推論を実行できます：

```
<|start|>system<|message|>You are ChatGPT, a large language model trained by OpenAI.
Knowledge cutoff: 2024-06
Current date: 2025-06-28

Reasoning: high

# Valid channels: analysis, commentary, final. Channel must be included for every message.
Calls to these tools must go to the commentary channel: 'functions'.<|end|><|start|>developer<|message|># Instructions

Use a friendly tone.

# Tools

## functions

namespace functions {

// Gets the location of the user.
type get_location = () => any;

// Gets the current weather in the provided location.
type get_current_weather = (_: {
// The city and state, e.g. San Francisco, CA
location: string,
format?: "celsius" | "fahrenheit", // default: celsius
}) => any;

// Gets the current weather in the provided list of locations.
type get_multiple_weathers = (_: {
// List of city and state, e.g. ["San Francisco, CA", "New York, NY"]
locations: string[],
format?: "celsius" | "fahrenheit", // default: celsius
}) => any;

} // namespace functions<|end|><|start|>user<|message|>What is the weather like in SF?<|end|><|start|>assistant<|channel|>analysis<|message|>Need to use function get_current_weather.<|end|><|start|>assistant<|channel|>commentary to=functions.get_current_weather <|constrain|>json<|message|>{"location":"San Francisco"}<|call|><|start|>functions.get_current_weather to=assistant<|channel|>commentary<|message|>{"sunny": true, "temperature": 20}<|end|><|start|>assistant
```

上記のように、さらなるサンプリングのためにモデルに関数出力を渡すだけでなく、以前の思考の連鎖（「Need to use function get_current_weather.」）も渡して、モデルが思考の連鎖を続けるか、最終的な答えを提供するために必要な情報を提供します。

#### プリアンブル

時々、モデルは、呼び出そうとしているツールについてユーザーに通知するための「プリアンブル」を生成することを選択する場合があります。たとえば、複数のツールを呼び出す予定がある場合です。この場合、思考の連鎖とは異なり、エンドユーザーに表示されることを意図した `commentary` チャネルでアシスタントメッセージを生成します。

```
<|channel|>analysis<|message|>{long chain of thought}<|end|><|start|>assistant<|channel|>commentary<|message|>**Action plan**:
1. Generate an HTML file
2. Generate a JavaScript for the Node.js server
3. Start the server
---
Will start executing the plan step by step<|end|><|start|>assistant<|channel|>commentary to=functions.generate_file<|constrain|>json<|message|>{"template": "basic_html", "path": "index.html"}<|call|>
```

この場合、モデルは、実行しようとしている複数のステップについてユーザーに通知するためのアクションプランを生成しました。

### 構造化出力

モデルの出力動作を制御するには、次の構造で[開発者メッセージ](#developer-message-format)の最後にレスポンス形式を定義できます：

```
# Response Formats

## {format name}

// {description or context}
{schema}<|end|>
```

形式名は、[Responses API](https://platform.openai.com/docs/guides/structured-outputs?api-mode=responses#how-to-use) でスキーマに指定できる名前と同様に機能し、スキーマは JSON Schema です。

例として、以下は買い物リストのスキーマを定義する開発者メッセージです：

```
<|start|>developer<|message|># Instructions

You are a helpful shopping assistant

# Response Formats

## shopping_list

{"properties":{"items":{"type":"array","description":"entries on the shopping list","items":{"type":"string"}}},"type":"object"}<|end|><|start|>user<|message|>I need to buy coffee, soda and eggs<|end|><|start|>assistant

```

ただし、このプロンプトだけでは、モデルの動作に影響を与えますが、スキーマへの完全な準拠を保証するものではありません。これには、独自の文法を構築し、サンプリング中にスキーマを強制する必要があります。

### 組み込みツール

`gpt-oss` モデルのトレーニング中、情報を閲覧し、Python コードを実行して結果を改善するための2つの一般的なツールで訓練されました。

この機能を構築しようとしている場合は、信頼性と精度を向上させるために以下の形式を使用する必要があります。

これらのツールは、開発者メッセージではなく、`# Tools` セクションを追加することで[システムメッセージ](#system-message-format)に定義する必要があります。

#### ブラウザツール

ブラウザツールを定義するには、システムプロンプトセクションに追加します：

```
<|start|>system<|message|>You are ChatGPT, a large language model trained by OpenAI.
Knowledge cutoff: 2024-06
Current date: 2025-06-28

Reasoning: high

# Tools

## browser

// Tool for browsing.
// The `cursor` appears in brackets before each browsing display: `[{cursor}]`.
// Cite information from the tool using the following format:
// `【{cursor}†L{line_start}(-L{line_end})?】`, for example: `【6†L9-L11】` or `【8†L3】`.
// Do not quote more than 10 words directly from the tool output.
// sources=web (default: web)
namespace browser {

// Searches for information related to `query` and displays `topn` results.
type search = (_: {
query: string,
topn?: number, // default: 10
source?: string,
}) => any;

// Opens the link `id` from the page indicated by `cursor` starting at line number `loc`, showing `num_lines` lines.
// Valid link ids are displayed with the formatting: `【{id}†.*】`.
// If `cursor` is not provided, the most recent page is implied.
// If `id` is a string, it is treated as a fully qualified URL associated with `source`.
// If `loc` is not provided, the viewport will be positioned at the beginning of the document or centered on the most relevant passage, if available.
// Use this function without `id` to scroll to a new location of an opened page.
type open = (_: {
id?: number | string, // default: -1
cursor?: number, // default: -1
loc?: number, // default: -1
num_lines?: number, // default: -1
view_source?: boolean, // default: false
source?: string,
}) => any;

// Finds exact matches of `pattern` in the current page, or the page given by `cursor`.
type find = (_: {
pattern: string,
cursor?: number, // default: -1
}) => any;

} // namespace browser

# Valid channels: analysis, commentary, final. Channel must be included for every message.<|end|>
```

モデルがブラウザでアクションを呼び出すことを決定した場合、2つの注目すべき例外を除いて、[関数呼び出し](#function-calling)と同じ形式を使用します：

1. リクエストは `analysis` チャネルに対して行われます
2. recipient は、それぞれ `browser.search`、`browser.open`、`browser.find` になります

#### Python ツール

```
<|start|>system<|message|>You are ChatGPT, a large language model trained by OpenAI.
Knowledge cutoff: 2024-06
Current date: 2025-06-28

Reasoning: high

# Tools

## python

Use this tool to execute Python code in your chain of thought. The code will not be shown to the user. This tool should be used for internal reasoning, but not for code that is intended to be visible to the user (e.g. when creating plots, tables, or files).

When you send a message containing Python code to python, it will be executed in a stateful Jupyter notebook environment. python will respond with the output of the execution or time out after 120.0 seconds. The drive at '/mnt/data' can be used to save and persist user files. Internet access for this session is UNKNOWN. Depends on the cluster.

# Valid channels: analysis, commentary, final. Channel must be included for every message.<|end|>
```

モデルが Python コードを実行することを決定した場合、2つの注目すべき例外を除いて、[関数呼び出し](#function-calling)と同じ形式を使用します：

3. リクエストは `analysis` チャネルに対して行われます
4. recipient は常に `python` になります

