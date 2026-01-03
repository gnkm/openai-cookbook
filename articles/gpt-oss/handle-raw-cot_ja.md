# gpt-oss で生の思考の連鎖を処理する方法

[gpt-oss モデル](https://openai.com/open-models)は、モデル実装者による分析と安全性研究を目的とした生の思考の連鎖（CoT）へのアクセスを提供しますが、ツール呼び出しは CoT の一部として実行できるため、ツール呼び出しのパフォーマンスにも重要です。同時に、生の CoT には潜在的に有害なコンテンツが含まれている可能性があるか、モデルを実装している人が意図しない情報（モデルに与えられた指示で指定されたルールなど）をユーザーに明らかにする可能性があります。したがって、生の CoT をエンドユーザーに表示すべきではありません。

## Harmony / chat template の処理

モデルは、[harmony レスポンス形式](https://cookbook.openai.com/articles/openai-harmony)の一部として生の CoT をエンコードします。独自の chat template を作成しているか、トークンを直接処理している場合は、[まず harmony ガイドを確認してください](https://cookbook.openai.com/articles/openai-harmony)。

いくつかのことを要約すると：

1. CoT は `analysis` チャネルに発行されます
2. 後続のサンプリングターンで `final` チャネルへのメッセージの後、すべての `analysis` メッセージをドロップする必要があります。`commentary` チャネルへの関数呼び出しは残すことができます
3. アシスタントによる最後のメッセージが任意のタイプのツール呼び出しだった場合、`final` メッセージが発行されるまで、以前の `final` メッセージまでの analysis メッセージを後続のサンプリングで保持する必要があります

## Chat Completions API

Chat Completions API を実装している場合、公開されている OpenAI 仕様には思考の連鎖を処理するための公式仕様はありません。ホストされているモデルは当面この機能を提供しないためです。代わりに、[OpenRouter からの次の規約に従うことをお願いします](https://openrouter.ai/docs/use-cases/reasoning-tokens)。以下を含みます：

1. リクエストの一部として `reasoning: { exclude: true }` が指定されていない限り、生の CoT は応答の一部として返されます。[詳細はこちら](https://openrouter.ai/docs/use-cases/reasoning-tokens#legacy-parameters)
2. 生の CoT は、出力のメッセージの `reasoning` プロパティとして公開されます
3. デルタイベントの場合、デルタには `reasoning` プロパティがあります
4. 後続のターンでは、以前の推論を（`reasoning` として）受け取り、上記の chat template セクションで指定された動作に従って処理できる必要があります。

疑問がある場合は、OpenRouter 実装の規約/動作に従ってください。

## Responses API

Responses API の場合、このケースをカバーするために Responses API 仕様を拡張しました。以下は、型定義としての仕様の変更です。高レベルでは、次のことを行っています：

1. `reasoning` に新しい `content` プロパティを導入します。これにより、エンドユーザーに表示できる推論 `summary` を、生の CoT（エンドユーザーに表示すべきではありませんが、解釈可能性研究に役立つ可能性があります）と同時に返すことができます。
2. `reasoning_text` という新しいコンテンツタイプを導入します
3. 生の CoT のデルタをストリーミングするための `response.reasoning_text.delta` と、CoT のターンが完了したことを示す `response.reasoning_text.done` という2つの新しいイベントを導入します
4. 後続のターンでは、以前の推論を受け取り、上記の chat template セクションで指定された動作に従って処理できる必要があります。

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

## エンドユーザーへの生の CoT の表示

ユーザーにチャットインターフェースを提供している場合、生の CoT には潜在的に有害なコンテンツや、ユーザーに表示することを意図していない可能性のある他の情報（たとえば、開発者メッセージの指示など）が含まれている可能性があるため、生の CoT を表示すべきではありません。代わりに、API や ChatGPT での本番実装と同様に、要約された CoT を表示することをお勧めします。ここでは、要約モデルが有害なコンテンツが表示されないようにレビューおよびブロックします。

