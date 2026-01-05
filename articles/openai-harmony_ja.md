# OpenAI harmony レスポンス形式

[`gpt-oss` モデル](https://openai.com/open-models)は、会話構造の定義、推論出力の生成、関数呼び出しの構造化のためのharmonyレスポンス形式で訓練されました。`gpt-oss`を直接使用せず、APIやOllamaなどのプロバイダー経由で使用している場合は、推論ソリューションがフォーマットを処理するため、これについて心配する必要はありません。独自の推論ソリューションを構築している場合、このガイドではプロンプト形式について説明します。この形式はOpenAI Responses APIを模倣するように設計されているため、そのAPIを使用したことがある場合は、この形式に馴染みがあるはずです。`gpt-oss`はharmony形式を使用せずに使用すべきではありません。正しく動作しないためです。

## 概念

### ロール

モデルが処理するすべてのメッセージには、関連するロールがあります。モデルは5種類のロールについて知っています：

| ロール        | 目的                                                                                                                                                                                 |
| :---------- | :-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `system`    | システムメッセージは、推論の努力、知識カットオフや組み込みツールなどのメタ情報を指定するために使用されます                                                                         |
| `developer` | 開発者メッセージは、モデルの指示（通常「システムプロンプト」と考えられるもの）と利用可能な関数ツールに関する情報を提供するために使用されます                |
| `user`      | 通常、モデルへの入力を表します                                                                                                                                           |
| `assistant` | モデルによって出力され、ツール呼び出しまたはメッセージ出力のいずれかになります。出力は、メッセージの意図を識別する特定の「チャンネル」に関連付けられる場合もあります。 |
| `tool`      | ツール呼び出しの出力を表すメッセージ。特定のツール名がメッセージ内のロールとして使用されます。                                                                      |

これらのロールは、指示の競合がある場合にモデルが適用する情報階層も表します：`system` \> `developer` \> `user` \> `assistant` \> `tool`

#### チャンネル

アシスタントメッセージは3つの異なる「チャンネル」で出力できます。これらは、ユーザー向けレスポンスと内部向けメッセージを分離するために使用されています。

| チャンネル      | 目的                                                                                                                                                                                                                                                                                                                                                            |
| :----------- | :----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `final`      | finalチャンネルでタグ付けされたメッセージは、エンドユーザーに表示することを意図したメッセージで、モデルからのレスポンスを表します。                                                                                                                                                                                                                                 |
| `analysis`   | これらは、モデルが思考の連鎖（CoT）に使用するメッセージです。**重要：** analysisチャンネルのメッセージは、finalメッセージと同じ安全基準に準拠していません。これらをエンドユーザーに表示することは避けてください。                                                                                                                             |
| `commentary` | 関数ツール呼び出しは通常`commentary`チャンネルでトリガーされ、組み込みツールは通常`analysis`チャンネルでトリガーされます。ただし、時折組み込みツールが`commentary`に出力されることもあります。時折、このチャンネルは複数の関数を呼び出すための[前文](#preambles)を生成するためにモデルによって使用されることもあります。 |

## Harmony レンダラーライブラリ

可能な場合は、[PyPI](https://pypi.org/project/openai-harmony/)または[crates.io](https://crates.io/crates/openai-harmony)を通じてharmonyレンダラーを使用することをお勧めします。これにより、メッセージを適切な形式でレンダリングし、モデルによる処理のためにトークンに変換することが自動的に処理されます。

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

# トークンレスポンスを受信した後
# ストップトークンは渡さない
parsed_response = encoding.parse_messages_from_completion_tokens(new_tokens, Role.ASSISTANT)
```

さらに、openai_harmonyライブラリには、モデルが新しいトークンを生成している間にパースとデコードを行うためのStreamableParserも含まれています。これは、例えば出力をストリーミングし、デコード中にUnicode文字を処理するのに役立ちます。

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

独自のレンダラーを構築することを選択した場合、以下の形式に従う必要があります。

### 特殊トークン

モデルは、入力の構造を識別するために一連の特殊トークンを使用します。[tiktoken](https://github.com/openai/tiktoken)を使用している場合、これらのトークンは`o200k_harmony`エンコーディングでエンコードされます。すべての特殊トークンは`<|type|>`の形式に従います。

| 特殊トークン           | 目的                                                                                                                                     | トークンID |
| :---------------------- | :------------------------------------------------------------------------------------------------------------------------------------------ | :------- |
| <&#124;start&#124;>     | [メッセージ](#message-format)の開始を示します。[ロール](#roles)から始まるメッセージの「ヘッダー」情報が続きます | `200006` |
| <&#124;end&#124;>       | [メッセージ](#message-format)の終了を示します                                                                                           | `200007` |
| <&#124;message&#124;>   | メッセージ「ヘッダー」から実際のコンテンツへの移行を示します                                                                    | `200008` |
| <&#124;channel&#124;>   | ヘッダーの[チャンネル](#channels)情報への移行を示します                                                              | `200005` |
| <&#124;constrain&#124;> | [ツール呼び出し](#receiving-tool-calls)でのデータ型定義への移行を示します                                                | `200003` |
| <&#124;return&#124;>    | モデルがレスポンスメッセージのサンプリングを完了したことを示します。推論を停止すべきことを示す有効な「ストップトークン」です。             | `200002` |
| <&#124;call&#124;>      | モデルがツールを呼び出したいことを示します。推論を停止すべきことを示す有効な「ストップトークン」です。                                   | `200012` |

### メッセージ形式

harmonyレスポンス形式は「メッセージ」で構成され、モデルは一度に複数のメッセージを生成する可能性があります。メッセージの一般的な構造は以下の通りです：

```
<|start|>{header}<|message|>{content}<|end|>
```

`{header}`には[ロール](#roles)を含む一連のメタ情報が含まれます。`<|end|>`は完全に完了したメッセージの終了を表しますが、モデルはツール呼び出しの`<|call|>`や、モデルが完了を終了したことを示す`<|return|>`などの他のストップトークンも使用する場合があります。

### チャット会話形式

上記のメッセージ形式に従って、最も基本的なチャット形式は`user`メッセージと`assistant`メッセージの開始で構成されます。

#### 入力例

```
<|start|>user<|message|>What is 2 + 2?<|end|>
<|start|>assistant
```

出力は`channel`を指定することから始まります。例えば、思考の連鎖を出力するための`analysis`です。モデルは複数のメッセージ（主に思考の連鎖メッセージ）を出力する可能性があり、それらを分離するために`<|end|>`トークンを使用します。

生成が完了すると、最終回答の生成が完了したことを示す`<|return|>`トークン、またはツール呼び出しを実行する必要があることを示す`<|call|>`のいずれかで停止します。いずれの場合も、推論を停止すべきことを示します。

#### 出力例

```
<|channel|>analysis<|message|>User asks: "What is 2 + 2?" Simple arithmetic. Provide answer.<|end|>
<|start|>assistant<|channel|>final<|message|>2 + 2 = 4.<|return|>
```

`final`チャンネルには、ユーザーのリクエストに対する回答が含まれます。思考の連鎖の詳細については、[推論セクション](#reasoning)をご確認ください。

**実装注意：** `<|return|>`はデコード時のみのストップトークンです。次のターンの会話履歴にアシスタントの生成した返信を追加する際は、末尾の`<|return|>`を`<|end|>`に置き換えて、保存されたメッセージが`<|start|>{header}<|message|>{content}<|end|>`として完全に形成されるようにしてください。したがって、プロンプト内の以前のメッセージは`<|end|>`で終わるべきです。教師ありターゲット/訓練例では、`<|return|>`で終わることが適切です。永続化された履歴では、`<|end|>`に正規化してください。

### システムメッセージ形式

システムメッセージは、システムに一般的な情報を提供するために使用されます。これは、他のプロンプト形式で「システムプロンプト」と考えられるものとは異なります。それについては、[開発者メッセージ形式](#developer-message-format)をご確認ください。

システムメッセージを使用して以下を定義します：

1. モデルの**アイデンティティ** — これは常に`You are ChatGPT, a large language model trained by OpenAI.`のままにしておくべきです。モデルのアイデンティティを変更したい場合は、[開発者メッセージ](#developer-message-format)の指示を使用してください。
2. メタ**日付** — 具体的には`Knowledge cutoff:`と`Current date:`
3. **推論の努力** — `high`、`medium`、`low`のレベルで指定
4. 利用可能なチャンネル — 最高のパフォーマンスのために、これは`analysis`、`commentary`、`final`にマップされるべきです。
5. 組み込みツール — モデルは`python`と`browser`ツールの両方で訓練されています。詳細については[組み込みツールセクション](#built-in-tools)をご確認ください。

**関数を定義している場合、**すべての関数ツール呼び出しは`commentary`チャンネルに行く必要があるという注記も含めるべきです。

最高のパフォーマンスのために、この形式にできるだけ忠実に従ってください。

#### システムメッセージの例

使用すべき最も基本的なシステムメッセージは以下の通りです：

```
<|start|>system<|message|>You are ChatGPT, a large language model trained by OpenAI.
Knowledge cutoff: 2024-06
Current date: 2025-06-28

Reasoning: high

# Valid channels: analysis, commentary, final. Channel must be included for every message.<|end|>
```

開発者メッセージセクションに関数呼び出しが存在する場合は、以下を使用してください：

```
<|start|>system<|message|>You are ChatGPT, a large language model trained by OpenAI.
Knowledge cutoff: 2024-06
Current date: 2025-06-28

Reasoning: high

# Valid channels: analysis, commentary, final. Channel must be included for every message.
Calls to these tools must go to the commentary channel: 'functions'.<|end|>
```

### 開発者メッセージ形式

開発者メッセージは、一般的に「システムプロンプト」と考えられるものを表します。モデルに提供される指示と、使用可能な[関数ツール](#function-calling)のリスト、または[構造化出力](#structured-output)でモデルが従うべき出力形式をオプションで含みます。

関数ツール呼び出しを使用していない場合、開発者メッセージは次のようになります：

```
<|start|>developer<|message|># Instructions

{instructions}<|end|>
```

ここで`{instructions}`は「システムプロンプト」に置き換えられます。

関数呼び出しツールの定義については、[専用セクション](#function-calling)をご確認ください。  
構造化出力で使用する出力形式の定義については、[ガイドのこのセクション](#structured-output)をご確認ください。

### 推論

gpt-ossモデルは推論モデルです。デフォルトでは、モデルは中程度レベルの推論を行います。推論を制御するには、[システムメッセージ](#system-message-format)で推論レベルを`low`、`medium`、または`high`として指定できます。推奨形式は：

```
Reasoning: high
```

モデルは、生の思考の連鎖（CoT）をアシスタントメッセージとして`analysis`チャンネルに出力し、最終的なレスポンスは`final`として出力します。

例えば、`What is 2 + 2?`という質問に対して、モデルの出力は次のようになる可能性があります：

```
<|channel|>analysis<|message|>User asks: "What is 2 + 2?" Simple arithmetic. Provide answer.<|end|>
<|start|>assistant<|channel|>final<|message|>2 + 2 = 4.<|return|>
```

この場合、CoTは

```
User asks: "What is 2 + 2?" Simple arithmetic. Provide answer.
```

そして実際の回答は：

```
2 + 2 = 4
```

**重要：**  
モデルは、最終出力と同じ安全基準で思考の連鎖を訓練されていません。有害なコンテンツが含まれる可能性があるため、思考の連鎖をユーザーに表示すべきではありません。[モデルカードで詳細を確認してください](https://openai.com/index/gpt-oss-model-card/)。

#### 後続のサンプリングでの推論出力の処理

一般的に、アシスタントによるレスポンスが`final`チャンネルへのメッセージで終了した場合、後続のサンプリングでは以前のCoTコンテンツを削除すべきです。つまり、最初の入力が以下だった場合：

```
<|start|>user<|message|>What is 2 + 2?<|end|>
<|start|>assistant
```

そして以下の出力が得られた場合：

```
<|channel|>analysis<|message|>User asks: "What is 2 + 2?" Simple arithmetic. Provide answer.<|end|>
<|start|>assistant<|channel|>final<|message|>2 + 2 = 4.<|return|>
```

モデルが適切に動作するために、次のサンプリングの入力は以下のようになるべきです：

```
<|start|>user<|message|>What is 2 + 2?<|end|>
<|start|>assistant<|channel|>final<|message|>2 + 2 = 4.<|end|>
<|start|>user<|message|>What about 9 / 2?<|end|>
<|start|>assistant
```

この例外はツール/関数呼び出しです。モデルは思考の連鎖の一部としてツールを呼び出すことができるため、後続のサンプリングのために以前の思考の連鎖を入力として戻す必要があります。完全な例については、[関数呼び出しセクション](#function-calling)をご確認ください。

### 関数呼び出し

#### 利用可能なツールの定義

モデルで利用可能なすべての関数は、[開発者メッセージ](#developer-message-format)の専用`Tools`セクションで定義する必要があります。

関数を定義するために、TypeScriptのような型構文を使用し、関数を専用の`functions`名前空間にラップします。関数呼び出しの精度を向上させるために、この形式に忠実に従うことが重要です。引数のJSON スキーマ定義をこの形式に変換する方法の詳細については、harmonyレンダラーのコードベースを確認できますが、一般的なフォーマット慣行は以下の通りです：

- 引数を受け取らない場合は、すべての関数を`type {function_name} = () => any`として定義
- 引数を受け取る関数の場合、引数に`_`という名前を付けて型定義をインライン化
- フィールド定義の上の行に説明のコメントを追加
- 戻り値の型として常に`any`を使用
- 各関数定義の後に空行を保持
- 関数を名前空間にラップ。一般的に`functions`は、モデルが訓練された可能性のある[他のツール](#built-in-tools)と競合しないために使用すべき名前空間です。

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

モデルがツールを呼び出すことを決定した場合、`to={name}`形式を使用してメッセージのヘッダーで`recipient`を定義します。例えば、上記の`get_current_weather`関数をトリガーすることを決定した場合、ヘッダーで`to=functions.get_current_weather`を指定し、[システムメッセージ](#system-message-format)で指定されているように`commentary`をチャンネルとして指定します。**recipientはヘッダーのroleまたはchannelセクションで定義される場合があります。**

モデルは、ツール呼び出しの入力タイプを示すために`<|constrain|>`トークンを指定する場合もあります。この場合、JSONとして渡されるため、`<|constrain|>`は`json`に設定されます。

```
<|channel|>analysis<|message|>Need to use function get_current_weather.<|end|><|start|>assistant<|channel|>commentary to=functions.get_current_weather <|constrain|>json<|message|>{"location":"San Francisco"}<|call|>
```

#### ツール呼び出しの処理

関数呼び出しが処理された後、呼び出しメッセージの後に出力を含む新しいツールメッセージを提供することで、出力をモデルに戻す必要があります。

ツールメッセージは以下の形式です：

```
<|start|>{toolname} to=assistant<|channel|>commentary<|message|>{output}<|end|>
```

上記の例では

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

上記のように、さらなるサンプリングのためにモデルに関数出力を戻すだけでなく、以前の思考の連鎖（「Need to use function get_current_weather.」）も渡して、モデルが思考の連鎖を続けるか最終回答を提供するために必要な情報を提供しています。

#### 前文

時々、モデルは呼び出そうとしているツールについてユーザーに知らせるための「前文」を生成することを選択する場合があります。例えば、複数のツールを呼び出す予定の場合です。この場合、思考の連鎖とは異なり、エンドユーザーに表示することを意図した`commentary`チャンネルでアシスタントメッセージを生成します。

```
<|channel|>analysis<|message|>{long chain of thought}<|end|><|start|>assistant<|channel|>commentary<|message|>**Action plan**:
1. Generate an HTML file
2. Generate a JavaScript for the Node.js server
3. Start the server
---
Will start executing the plan step by step<|end|><|start|>assistant<|channel|>commentary to=functions.generate_file<|constrain|>json<|message|>{"template": "basic_html", "path": "index.html"}<|call|>
```

この場合、モデルは実行しようとしている複数のステップについてユーザーに知らせるためのアクションプランを生成しました。

### 構造化出力

モデルの出力動作を制御するために、[開発者メッセージ](#developer-message-format)の最後に以下の構造でレスポンス形式を定義できます：

```
# Response Formats

## {format name}

// {description or context}
{schema}<|end|>
```

形式名は、[Responses API](https://platform.openai.com/docs/guides/structured-outputs?api-mode=responses#how-to-use)でスキーマに指定できる名前と同様に機能し、スキーマはJSON Schemaです。

例として、ショッピングリストのスキーマを定義する開発者メッセージは以下の通りです：

```
<|start|>developer<|message|># Instructions

You are a helpful shopping assistant

# Response Formats

## shopping_list

{"properties":{"items":{"type":"array","description":"entries on the shopping list","items":{"type":"string"}}},"type":"object"}<|end|><|start|>user<|message|>I need to buy coffee, soda and eggs<|end|><|start|>assistant

```

ただし、このプロンプトだけではモデルの動作に影響を与えますが、スキーマへの完全な準拠は保証されません。これには、独自の文法を構築し、サンプリング中にスキーマを強制する必要があります。

### 組み込みツール

`gpt-oss`モデルの訓練中、情報を閲覧しPythonコードを実行して結果を改善するための2つの一般的なツールで訓練されました。

この機能を構築しようとしている場合は、信頼性と精度を向上させるために以下の形式を使用すべきです。

これらのツールは、開発者メッセージではなく[システムメッセージ](#system-message-format)で`# Tools`セクションを追加することで定義すべきです。

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

モデルがブラウザでアクションを呼び出すことを決定した場合、[関数呼び出し](#function-calling)と同じ形式を使用しますが、2つの注目すべき例外があります：

1. リクエストは`analysis`チャンネルに対して行われます
2. recipientはそれぞれ`browser.search`、`browser.open`、`browser.find`になります

#### Pythonツール

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

モデルがPythonコードを実行することを決定した場合、[関数呼び出し](#function-calling)と同じ形式を使用しますが、2つの注目すべき例外があります：

3. リクエストは`analysis`チャンネルに対して行われます
4. recipientは常に`python`になります