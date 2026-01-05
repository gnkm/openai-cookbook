# gpt-ossにおける生の思考連鎖の処理方法

[gpt-ossモデル](https://openai.com/open-models)は、モデル実装者による分析と安全性研究を目的とした生の思考連鎖（CoT）へのアクセスを提供しますが、これはツール呼び出しのパフォーマンスにも重要です。ツール呼び出しはCoTの一部として実行できるためです。同時に、生のCoTには潜在的に有害なコンテンツが含まれる可能性があり、モデルを実装する人が意図しない情報（モデルに与えられた指示で指定されたルールなど）をユーザーに明かす可能性があります。そのため、生のCoTをエンドユーザーに表示すべきではありません。

## Harmony / チャットテンプレートの処理

モデルは、[harmonyレスポンス形式](https://cookbook.openai.com/articles/openai-harmony)の一部として生のCoTをエンコードします。独自のチャットテンプレートを作成している場合や、トークンを直接処理している場合は、[まずharmonyガイドを確認してください](https://cookbook.openai.com/articles/openai-harmony)。

いくつかの要点をまとめると：

1. CoTは`analysis`チャンネルに発行されます
2. 後続のサンプリングターンで`final`チャンネルへのメッセージの後、すべての`analysis`メッセージは削除されるべきです。`commentary`チャンネルへの関数呼び出しは残すことができます
3. アシスタントによる最後のメッセージが何らかのタイプのツール呼び出しだった場合、前の`final`メッセージまでの分析メッセージは、`final`メッセージが発行されるまで後続のサンプリングで保持されるべきです

## Chat Completions API

Chat Completions APIを実装している場合、公開されているOpenAI仕様には思考連鎖を処理するための公式仕様はありません。これは、当社のホストモデルが当面この機能を提供しないためです。代わりに[OpenRouterの以下の規約に従ってください](https://openrouter.ai/docs/use-cases/reasoning-tokens)。以下を含みます：

1. リクエストの一部として`reasoning: { exclude: true }`が指定されない限り、生のCoTはレスポンスの一部として返されます。[詳細はこちら](https://openrouter.ai/docs/use-cases/reasoning-tokens#legacy-parameters)
2. 生のCoTは出力のメッセージの`reasoning`プロパティとして公開されます
3. デルタイベントの場合、デルタには`reasoning`プロパティがあります
4. 後続のターンでは、前の推論を（`reasoning`として）受け取り、上記のチャットテンプレートセクションで指定された動作に従って処理できるべきです。

疑問がある場合は、OpenRouter実装の規約/動作に従ってください。

## Responses API

Responses APIについては、このケースをカバーするためにResponses API仕様を拡張しました。以下は型定義としての仕様の変更です。高レベルでは以下を行っています：

1. `reasoning`に新しい`content`プロパティを導入。これにより、エンドユーザーに表示できる推論`summary`を、生のCoT（エンドユーザーには表示すべきではないが、解釈可能性研究には役立つ可能性がある）と同時に返すことができます。
2. `reasoning_text`という新しいコンテンツタイプを導入
3. 生のCoTのデルタをストリーミングするための`response.reasoning_text.delta`と、CoTのターンの完了を示す`response.reasoning_text.done`という2つの新しいイベントを導入
4. 後続のターンでは、前の推論を受け取り、上記のチャットテンプレートセクションで指定された動作に従って処理できるべきです。

**アイテムタイプの変更**

```typescript
type ReasoningItem = {
  id: string;
  type: "reasoning";
  summary: SummaryContent[];
  // new
  content: ReasoningTextContent[];
};

type ReasoningTextContent = {
  type: "reasoning_text";
  text: string;
};

type ReasoningTextDeltaEvent = {
  type: "response.reasoning_text.delta";
  sequence_number: number;
  item_id: string;
  output_index: number;
  content_index: number;
  delta: string;
};

type ReasoningTextDoneEvent = {
  type: "response.reasoning_text.done";
  sequence_number: number;
  item_id: string;
  output_index: number;
  content_index: number;
  text: string;
};
```

**イベントの変更**

```typescript
...
{
	type: "response.content_part.added"
	...
}
{
	type: "response.reasoning_text.delta",
	sequence_number: 14,
	item_id: "rs_67f47a642e788191aec9b5c1a35ab3c3016f2c95937d6e91",
	output_index: 0,
	content_index: 0,
	delta: "The "
}
...
{
	type: "response.reasoning_text.done",
	sequence_number: 18,
	item_id: "rs_67f47a642e788191aec9b5c1a35ab3c3016f2c95937d6e91",
	output_index: 0,
	content_index: 0,
	text: "The user asked me to think"
}
```

**レスポンス出力の例**

```typescript
"output": [
  {
    "type": "reasoning",
    "id": "rs_67f47a642e788191aec9b5c1a35ab3c3016f2c95937d6e91",
    "summary": [
      {
        "type": "summary_text",
        "text": "**Calculating volume of gold for Pluto layer**\n\nStarting with the approximation..."
      }
    ],
    "content": [
      {
        "type": "reasoning_text",
        "text": "The user asked me to think..."
      }
    ]
  }
]

```

## エンドユーザーへの生のCoTの表示

ユーザーにチャットインターフェースを提供している場合、生のCoTには潜在的に有害なコンテンツや、ユーザーに表示することを意図しない他の情報（例えば、開発者メッセージ内の指示など）が含まれる可能性があるため、表示すべきではありません。代わりに、APIやChatGPTでの本番実装と同様に、要約モデルが有害なコンテンツをレビューし、表示をブロックする要約されたCoTを表示することをお勧めします。