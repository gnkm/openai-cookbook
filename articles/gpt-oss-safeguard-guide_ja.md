# gpt-oss-safeguard ユーザーガイド

## はじめに・概要

ROOST と OpenAI は、[gpt-oss-safeguard](https://github.com/openai/gpt-oss-safeguard) の推論能力を最大化するポリシープロンプトの書き方、深い分析のための適切なポリシーの長さの選択、oss-safeguard の推論出力を本番環境の Trust & Safety システムに統合する方法を説明するガイドを用意しました。

### gpt-oss-safeguard とは？

gpt-oss-safeguard は、カスタマイズ可能なポリシーに基づいてテキストコンテンツを分類するための安全性分類タスク専用に訓練された、初のオープンウェイト推論モデルです。[gpt-oss](https://openai.com/index/introducing-gpt-oss/) のファインチューニング版として、gpt-oss-safeguard は、あなたが提供する明示的な書面ポリシーに従うように設計されています。これにより、**bring-your-own-policy** Trust & Safety AI が可能になり、あなた独自の分類法、定義、閾値が分類決定をガイドします。よく作成されたポリシーは、gpt-oss-safeguard の推論能力を解き放ち、ニュアンスのあるコンテンツを処理し、境界線上の決定を説明し、文脈的要因に適応することを可能にします。

OpenAI が gpt-oss-safeguard の内部バージョンをどのように使用しているかについては、[こちら](https://openai.com/index/introducing-gpt-oss-safeguard/)で詳しく読むことができます。

大規模言語モデルは、主に2つの方法で安全性モデルと見なすことができます：

- ファインチューニングされた安全性モデルは、一般的な推論モデル（gpt-oss など）として始まり、ユーザーインタラクション内で安全に応答するように訓練されます。
- 事前構築された安全性モデル（ShieldGemma、LlamaGuard、RoGuard など）には、「安全でない」とみなされるものの組み込み定義と固定されたポリシー分類法が付属しています。

gpt-oss-safeguard は、Trust & Safety ワークフロー用に特別に構築されたポリシー追従モデルであり、**あなた自身の書面基準を確実に解釈および実施し、なぜその決定を下したかを教えてくれます**。モデルの背後にある推論により、監査可能性とカスタマイズに根ざしたより大きな安全性システムとの統合に適しています。

### gpt-oss-safeguard の使用方法

[gpt-oss ファミリーのモデル](https://openai.com/open-models/)と同様に、これはローカルで実行するか、独自のインフラストラクチャに統合するオープンウェイトのオープンソースモデルです。[harmony レスポンス形式](https://github.com/openai/harmony)で動作するように設計されています。Harmony は、gpt-oss-safeguard に完全な推論スタックへのアクセスを提供し、一貫性のある整形式の出力を保証する構造化プロンプトインターフェースです。

gpt-oss-safeguard を含む gpt-oss ファミリーのモデルは、以下を使用してサーバー上で実行できます：

- [vLLM](https://docs.vllm.ai/projects/recipes/en/latest/OpenAI/GPT-OSS.html#gpt-oss-vllm-usage-guide)（NVIDIA の H100 などの専用 GPU 用）
- [HuggingFace Transformers](https://cookbook.openai.com/articles/gpt-oss/run-locally-lmstudio)（コンシューマー GPU 用）
- [Google Colab](https://cookbook.openai.com/articles/gpt-oss/run-colab)

そして、以下を使用してローカルで実行できます：

- [LM Studio](https://cookbook.openai.com/articles/gpt-oss/run-locally-lmstudio)
- [Ollama](https://cookbook.openai.com/articles/gpt-oss/run-locally-ollama)

### 誰が gpt-oss-safeguard を使用すべきか？

gpt-oss-safeguard は、リアルタイムコンテキストと大規模な自動化を必要とするユーザー向けに設計されています：

- **ML/AI エンジニア**：柔軟なコンテンツモデレーションを必要とする Trust & Safety システムに取り組んでいる
- **Trust & Safety エンジニア**：モデレーション、Trust & Safety、またはプラットフォームインテグリティパイプラインを構築または改善している
- **テクニカルプログラムマネージャー**：コンテンツ安全性イニシアチブを監督している
- **開発者**：文脈的でポリシーベースのコンテンツモデレーションを必要とするプロジェクト/アプリケーションを構築している
- **ポリシー作成者**：組織によって受け入れられるものを定義し、ポリシーラインをテストし、例を生成し、コンテンツを評価したい

安全性調整されたモデルは、明確で構造化されたプロンプトが与えられた場合、コンテンツモデレーションに優れています。このガイドでは、プロンプト構造、出力フォーマット、長さの最適化に焦点を当てて、本番環境でモデレーションシステムをデプロイすることから得られた主要な学びをカバーしています。

### HuggingFace Transformers で gpt-oss-safeguards を使用する

Hugging Face の Transformers ライブラリは、大規模言語モデルをローカルまたはサーバー上でロードして実行する柔軟な方法を提供します。[このガイド](https://cookbook.openai.com/articles/gpt-oss/run-transformers)では、高レベルのパイプラインまたは生のトークン ID を使用した低レベルの生成呼び出しのいずれかを使用して、[OpenAI gpt-oss](https://huggingface.co/openai/gpt-oss-20b) モデルを Transformers で実行する方法を説明します。サーバーと対話する最も簡単な方法は、transformers chat CLI を使用することです。

```bash
transformers chat localhost:8000 --model-name-or-path openai/gpt-oss-safeguard-20b
```

または、cURL で HTTP リクエストを送信します。例：

```bash
curl http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "openai/gpt-oss-safeguard-20b",
    "stream": true,
    "messages": [
      { "role": "system", "content": "<your policy>" },
      { "role": "user", "content": "<user content to verify>" }
    ]
  }'


```

Cursor やその他のツールとの transformers serve の統合などの追加のユースケースは、[ドキュメント](https://huggingface.co/docs/transformers/main/serving)に詳しく記載されています。

### Ollama で gpt-oss-safeguard を実行する

[Ollama](https://ollama.com/download) は、gpt-oss-safeguard 20B および 120B モデルを直接サポートしています。以下のコマンドは、モデルを自動的にダウンロードし、デバイス上で実行します。

#### gpt-oss-safeguard:20b

```bash
ollama run gpt-oss-safeguard:20b
```

#### gpt-oss-safeguard:120b

```bash
ollama run gpt-oss-safeguard:120b
```

Ollama は、gpt-oss-safeguard モデルを使用してアプリケーションやツールを構築するための [OpenAI API](https://docs.ollama.com/api/openai-compatibility)、[Ollama の API](https://docs.ollama.com/api)、[Python](https://github.com/ollama/ollama-python)、[JavaScript](https://github.com/ollama/ollama-js) SDK をサポートしています。詳細については、[Ollama のドキュメント](https://docs.ollama.com/)をご覧ください。

### LM Studio で gpt-oss-safeguard を実行する

または、[LM Studio](https://lmstudio.ai/) を使用して、[OpenAI Chat Completions](https://lmstudio.ai/docs/developer/openai-compat/chat-completions) および [Responses API](https://lmstudio.ai/docs/developer/openai-compat/responses) 互換 API を含むモデルをローカルで実行できます。[LM Studio の gpt-oss-safeguard ページ](https://lmstudio.ai/models/gpt-oss-safeguard)にアクセスするか、以下のコマンドを実行してそれぞれのモデルをダウンロードします：

#### gpt-oss-safeguard-20b

```bash
lms get openai/gpt-oss-safeguard-20b
```

#### gpt-oss-safeguard-120b

```bash
lms get openai/gpt-oss-safeguard-120b
```

### vLLM で gpt-oss-safeguard を実行する

[vLLM](https://docs.vllm.ai/) は、Python 依存関係管理に [uv](https://docs.astral.sh/uv/) を使用することを推奨しています。以下のコマンドは、モデルを自動的にダウンロードし、サーバーを起動します。

```shell
uv pip install vllm==0.10.2 --torch-backend=auto

vllm serve openai/gpt-oss-safeguard-120b
```

[vLLM で gpt-oss を使用する方法の詳細をご覧ください。](https://docs.vllm.ai/projects/recipes/en/latest/OpenAI/GPT-OSS.html#gpt-oss-vllm-usage-guide)

### Harmony レスポンス形式の理解

gpt-oss-safeguard は、[harmony プロンプト形式](https://cookbook.openai.com/articles/openai-harmony)を使用して、構造化された出力を提供し、推論を提供します。これは、決定または分類がなぜ行われたかを理解し、監査する必要がある Trust & Safety ワークフローにとって重要です。harmony 形式では、oss-safeguard は応答を2つの部分に分けます：

1. **推論チャネル**：モデルがポリシーを通じて推論し、エッジケースを考慮し、そのロジックを説明する場所
2. **出力チャネル**：指定したフォーマットされた分類決定

harmony を通じて、システムメッセージで `reasoning_effort` パラメータを `low`、`medium`、または `high` に設定することで、oss-safeguard がどれだけ深く推論するかを制御できます。モデルは、設定されていない場合、デフォルトで `medium` を使用します。より高い推論努力により、oss-safeguard はより多くの要因を考慮し、複数のポリシーセクションをトレースし、ルール間の複雑な相互作用を処理できます。より低い努力は、単純な分類のためにより速い応答を提供します。

[**vLLM**](https://docs.vllm.ai/en/latest/)（ほとんどのユーザーに推奨）または chat メッセージ入力を提供する別の推論ソリューションを使用している場合、リクエストを [chat メッセージ](https://docs.vllm.ai/en/v0.7.0/getting_started/examples/chat.html)としてフォーマットすると、harmony 形式が自動的に適用されます：

- **システムメッセージ**：あなたのポリシープロンプト（推論努力を制御するために、システムメッセージに Reasoning: high または同様のものを含めます）。
- **ユーザーメッセージ**：分類するコンテンツ。

## oss-safeguard がポリシープロンプトを使用する方法

oss-safeguard は、書面ポリシーを統治ロジックとして使用するように設計されています。ほとんどのモデルが訓練された機能に基づいて信頼度スコアを提供し、ポリシー変更のために再訓練を必要とするのに対し、oss-safeguard は提供された分類法の境界内で推論に裏打ちされた決定を下します。この機能により、T&S チームは、既存のモデレーションまたはコンプライアンスシステム内のポリシー整合推論レイヤーとして oss-safeguard をデプロイできます。これはまた、モデル全体を再訓練することなく、ポリシーを即座に更新またはテストできることを意味します。

## gpt-oss-safeguard のための効果的なポリシープロンプトの書き方

oss-safeguard は、ポリシーがエッセイではなく Trust & Safety ポリシーガイドのように整理されている場合に最高のパフォーマンスを発揮します。すでにポリシーのセットがある場合は、素晴らしい状態です。モデルが定義を効率的にナビゲートできるように、ヘッダーと明確なカテゴリを使用してください。以前にチーム向けにポリシーを書いたことがある場合は、これは馴染みがあるはずです。

### ポリシープロンプティングの理解

ポリシープロンプトは、モデルの動作の運用境界を定義します。人間のレビュアー向けに書かれたコンテンツまたはプラットフォームポリシーと同様に、oss-safeguard のポリシーは、違反を構成するもの、許可されるもの、およびその違いを Trust & Safety システムの残りの部分に流れる決定にどのように伝えるかを明確に指定する必要があります。

効果的なポリシープロンプトは、類似したコンテンツタイプを区別し、微妙な、コード化された、または間接的な違反をキャッチし、エッジケースでの誤検知を防ぐために構造化されています。これは、ポリシードキュメントとトレーニング例を組み合わせたものと考えてください。

### ポリシープロンプトの構造化

ポリシープロンプトには、4つの別々のセクションが必要です。

1. **指示（Instruction）**：モデルが何をしなければならないか、モデルがどのように答えるべきか。
2. **定義（Definitions）**：主要な用語の簡潔な説明。
3. **基準（Criteria）**：違反コンテンツと非違反コンテンツの区別。
4. **例（Examples）**：決定境界近くの短い具体的なインスタンス。分類したいものと、分類したくないものの両方の例を持つことが重要です。

oss-safeguard は構造化されたモデレーション用に調整されているため、応答方法に関する明示的な指示を期待しています。ポリシープロンプトは、応答と出力の期待される形式を含む一貫したパターンに従う場合、おそらくより良いパフォーマンスを発揮します。harmony 形式の構造化チャネルにより、oss-safeguard は最終ラベルのみを出力する前に、これらのセクションを通じて推論できます：

```markdown
# Policy Name

## INSTRUCTIONS

Describe what oss-safeguard should do and how to respond.

## DEFINITIONS

Clarify key terms and context.

## VIOLATES (1)

Describe behaviors or content that should be flagged.

## SAFE (0)

Describe content that should not be flagged.

## EXAMPLES

Provide 4–6 short examples labeled 0 or 1.

Content: [INPUT]
Answer (0 or 1):
```

誤検知や混乱の可能性を減らすために、「generally」や「usually」などの言葉の使用を避けてください。曖昧さがある状況がある場合は、手動レビューのためのエスカレーションパスを追加してください。これは、地域または言語の違いにも特に役立ちます。

優先順位と優先順位を明示的にして、競合がある場合にどのポリシーが優先されるかをモデルが理解できるようにしてください。複数のポリシー違反がある場合は、どれが支配的かを定義してください。

### 適切なポリシーの長さの選択

ポリシーの長さは、gpt-oss-safeguard がルールについてどれだけ深く推論できるかを制御する重要な要素です。より長いポリシーは、複雑なケースを処理するためのニュアンスを追加しますが、出力と応答に影響を与える可能性があります。harmony レスポンス形式を使用する場合、推論は隠された分析チャネルで行われ、表示される最終出力では行われないため、モデルはより長いポリシーをより確実に処理できます。

[https://platform.openai.com/tokenizer](https://platform.openai.com/tokenizer) を使用して、プロンプトの長さを決定してください。**gpt-oss-safeguard は約10,000トークンのポリシーで合理的な出力を提供できますが、初期テストでは最適範囲は400〜600トークンの間であることが示唆されています**。万能のアプローチはないため、実験して何が最適かを確認することが重要です。ポリシーの長さを「コンテキスト予算」のように考えてください。短すぎるとモデルに詳細が不足し、長すぎるとモデルが混乱するリスクがあります。これは、人々が理解するためのポリシーを書くのと似ています。同様に、モデルに応答を生成するのに十分な出力トークンを考慮する必要があります。モデルは推論を使用しているため、出力トークンに十分な余裕を残し、理想的には最大出力トークンを制限しないで、モデルがポリシーを通じて推論するのに十分なスペースを与える必要があります。推論時間を制限したい場合は、代わりに推論努力を低に設定することを検討してください。

複数のカテゴリを持つより長いポリシーがある場合は、各ポリシーを300〜600トークン（定義、禁止カテゴリ、違反と非違反のそれぞれ1〜2の例を含む）に事前圧縮することを検討してください。

oss-safeguard は、すべてのポリシーがプロンプトに含まれている限り、複数のポリシーを同時に評価することもできます。追加のポリシーは精度に小さいながらも意味のある低下をもたらすことがわかっているため、複数の害のドメインに oss-safeguard を使用する場合は、ポリシーの追加と削除を実験することをお勧めします。

## 信頼性の高い出力指示の設計

gpt-oss-safeguard からの一貫した応答には、明示的で文字通りの出力指示が必要です。すべてのポリシープロンプトは、モデルがどのように応答しなければならないかを正確に述べ、正しいパターンと正しくないパターンを実証する必要があります。出力指示は、gpt-oss-safeguard が最終決定をどのように伝えるかを定義し、出力に依拠できるかどうかを決定します。gpt-oss-safeguard は harmony レスポンス形式内で動作するため、すべての出力指示は以下を満たす必要があります：

1. **出力形式を明示的に定義する**：モデルが返すべきものを正確に指定します（例：`0`/`1`、JSON オブジェクト、カテゴリラベルリスト）。
2. **該当する場合はポリシー参照を含める**：ワークフローがカテゴリまたはルールによって実施を追跡する場合は、モデルにそのフィールドを返すように要求します。単純なバイナリ出力の場合、これは省略できます。
3. **ポリシー全体で強化される**：推論中のコンプライアンスを強化するために、出力指示を上部近く（「INSTRUCTIONS」）と下部近く（「EXAMPLES」の前）で少なくとも1回繰り返します。

### バイナリ応答

バイナリ出力は、gpt-oss-safeguard の推論を単純な yes/no 決定に制限します。決定がなぜ行われたかを理解するよりも速度が重要な場合にこれを使用しますが、gpt-oss-safeguard のコア推論の強みを活用していないことを認識してください。

```markdown
Return exactly one character: 0 or 1.
Do not include any explanation or punctuation.

0 = Content does NOT violate this policy.
1 = Content violates this policy.
```

### ポリシー参照出力

カテゴリラベルは、gpt-oss-safeguard にポリシーのどのセクションが適用されるかについて推論するように促しますが、なぜかの詳細な説明は必要ありません。この形式は、出力を簡潔に保ちながら、基本的な推論の透明性を可能にします。

```
If the content violates this policy, return:
{"violation": 1, "policy_category": "<category_or_rule_id>"}

If the content does NOT violate this policy, return:
{"violation": 0, "policy_category": null}

Example:
{"violation": 1, "policy_category": "H2.f"}
```

### 理由を含める

gpt-oss-safeguard の最も強力な機能の1つは、考え、推論する能力です。モデルは、コンテンツを分類するだけでなく、ポリシーを通じてそのロジックをトレースし、どの特定のルールが適用されるかを特定し、理由を明確にする必要があります。理由を要求すると、gpt-oss-safeguard はより慎重に推論します。複数のポリシーセクションを考慮し、それらがどのように相互作用するかを評価し、論理的な説明を構築する必要があります。この深い推論は、より単純な出力形式が見逃すニュアンスをしばしばキャッチします。この出力形式は、gpt-oss-safeguard の推論能力を最大化します。

モデルに決定してから簡単に正当化するように依頼します。短い、ステップバイステップではない理由（2〜4の箇条書きまたは1〜2の文）を求め、モデルがその思考と決定を正当化するように、ポリシー引用（ルール ID/セクション）を要求することを検討してください。

```json
{
  "violation": 1,
  "policy_category": "H2.f",
  "rule_ids": ["H2.d", "H2.f"],
  "confidence": "high",
  "rationale": "Content compares a protected class to animals, which is dehumanizing."
}
```

## Trust & Safety のための gpt-oss-safeguard の使用

gpt-oss-safeguard は、静的なカテゴリではなく書面ルールを解釈するため、最小限のエンジニアリングオーバーヘッドで、さまざまな製品、規制、コミュニティコンテキストに適応します。

gpt-oss-safeguard は、Trust & Safety チームのインフラストラクチャに適合するように設計されています。ただし、gpt-oss-safeguard は他の分類器よりも時間と計算集約的である可能性があるため、gpt-oss-safeguard に送信されるコンテンツを事前にフィルタリングすることを検討してください。[OpenAI は、小さな高リコール分類器を使用して、gpt-oss-safeguard でそのコンテンツを評価する前に、コンテンツが優先リスクにドメイン関連かどうかを判断します。](https://openai.com/index/introducing-gpt-oss-safeguard/) T&S スタックで oss-safeguard をいつどこに統合するかを決定する際に考慮すべき2つの主なことがあります：

1. 従来の分類器は、gpt-oss-safeguard よりもレイテンシが低く、サンプリングコストが低い
2. 数千の例で訓練された従来の分類器は、タスクで gpt-oss-safeguard よりもおそらく優れたパフォーマンスを発揮する

### 自動コンテンツ分類

gpt-oss-safeguard を使用して、ポリシー違反のために投稿、メッセージ、またはメディアメタデータにラベルを付けます。そのポリシー推論は、決定を下す際に文脈的詳細を決定するためのニュアンスのある分類をサポートします。gpt-oss-safeguard は以下と統合できます：

- リアルタイム取り込みパイプライン
- レビューキューとモデレーションコンソール
- ダウンランキングまたはフィルタリングシステム

### T&S アシスタント

gpt-oss-safeguard の推論能力により、Trust & Safety ワークフローでの自動トリアージに独自に適しています。ラベルと信頼度スコアのみを提供する従来の分類器とは異なり、gpt-oss-safeguard は、コンテンツを評価し、その決定を説明し、特定のポリシールールを引用し、人間の判断を必要とするケースを表面化する推論エージェントとして機能します。これにより、自動化された決定における信頼と透明性を高めながら、人間のモデレーターの認知負荷を軽減できます。

### ポリシーテスト

新しいまたは改訂されたポリシーを展開する前に、gpt-oss-safeguard を通じて実行して、コンテンツがどのようにラベル付けされるかをシミュレートします。これは、過度に広い定義、不明確な例、境界線上のケースを特定するのに役立ちます。

### ポリシー実験

gpt-oss-safeguard の bring-your-own-policy 設計により、ポリシーチームは、モデルの再訓練なしに、本番環境で代替定義を直接 A/B テストできます。

## ROOST のツールとの gpt-oss-safeguard の統合

### Osprey

[Osprey](https://github.com/roostorg/osprey) は、ROOST のオープンソースルールエンジンおよび調査フレームワークです。構成可能なロジックツリーに対してリアルタイムイベントを評価し、定義したアクションをディスパッチします。ルール単独では決定論的なケース（例：キーワードマッチ、メタデータ閾値）をうまく処理しますが、風刺、コード化された言語、またはニュアンスのあるポリシー境界に苦労する可能性があります。gpt-oss-safeguard を統合することで、Osprey は以下を実行できます：

- **文脈的推論を追加する**：gpt-oss-safeguard は、単純な条件では処理できないエッジケースを解釈します。
- **ポリシーを直接実施する**：gpt-oss-safeguard は、書面ポリシーテキストを読み取り、適用し、人間のモデレーションとの一貫性を確保します。
- **監査可能性を維持する**：Osprey は、どのルールが gpt-oss-safeguard を呼び出したか、どのポリシーカテゴリが返されたか、モデルの理由をログに記録します。
- **自動化と人間の監視をブレンドする**：決定論的ルールは高速アクションをトリガーします。gpt-oss-safeguard は、他のツールでの手動レビューへのエスカレーションの前に推論を処理します。

gpt-oss-safeguard は、すべてのイベントで呼び出されるべきではありません。代わりに、gpt-oss-safeguard のポリシー推論能力を必要とする曖昧なケースがある場合にのみ呼び出すことができるプラグインである必要があります。

## ポリシープロンプトの例

すでに書いたポリシーを使用するか、このテンプレートを使用して、分類しようとしているものを記入してください。

```markdown
## Policy Definitions

### Key Terms

**[Term 1]**: [Definition]

**[Term 2]**: [Definition]

**[Term 3]**: [Definition]

## Content Classification Rules

### VIOLATES Policy (Label: 1)

Content that:

- [Violation 1]
- [Violation 2]
- [Violation 3]
- [Violation 4]
- [Violation 5]

### DOES NOT Violate Policy (Label: 0)

Content that is:

- [Acceptable 1]
- [Acceptable 2]
- [Acceptable 3]
- [Acceptable 4]
- [Acceptable 5]

## Examples

### Example 1 (Label: 1)

**Content**: "[Example]"

**Expected Response**:

### Example 2 (Label: 1)

**Content**: "[Example]"

**Expected Response**:

### Example 3 (Label: 0)

**Content**: "[Example]"

**Expected Response**:

### Example 4 (Label: 0)

**Content**: "[Example]"

**Expected Response**:
```

また、スパムに関するこの例のプロンプトを参考として使用することもできます：

```markdown
**Spam Policy (#SP)**
**GOAL:** Identify spam. Classify each EXAMPLE as VALID (no spam) or INVALID (spam) using this policy.

**DEFINITIONS**

- **Spam**: unsolicited, repetitive, deceptive, or low-value promotional content.

- **Bulk Messaging:** Same or similar messages sent repeatedly.

- **Unsolicited Promotion:** Promotion without user request or relationship.

- **Deceptive Spam:** Hidden or fraudulent intent (fake identity, fake offer).

- **Link Farming:** Multiple irrelevant or commercial links to drive clicks.

**Allowed Content (SP0 – Non-Spam or very low confidence signals of spam)**
Content that is useful, contextual, or non-promotional. May look spammy but could be legitimate.

- **SP0.a Useful/info request** – "How do I upload a product photo?"

- **SP0.b Personalized communication** – "Hi Sam, here is the report."

- **SP0.c Business support** – "Can you fix my order?"

- **SP0.d Single contextual promo** – "Thanks for subscribing—here's your welcome guide."

- **SP0.e Generic request** – "Please respond ASAP."

- **SP0.f Low-quality formatting** – "HeLLo CLICK here FAST."

- **SP0.g Vague benefit statement** – "This tool changes lives."

  **Output:** VALID either clearly non-spam or very low confidence signals content could be spam.

**Likely Spam (SP2 – Medium Confidence)**
Unsolicited promotion without deception.

- **SP2.a Cold promotion** – "Check out my Shopify course: shopcoach.biz"

- **SP2.b Irrelevant ads** – "Buy gold rings here!"

- **SP2.c Excessive linking** – "[http://x.com](http://x.com) http://y.com http://z.com"
  **Output:** INVALID

**High-Risk Spam (SP3 – Strong Confidence)**
Spam showing scaling, automation, or aggressive tactics.

- **SP3.a Repetitive posting** – "JOIN NOW JOIN NOW JOIN NOW"

- **SP3.b Pyramid/affiliate bait** – "Earn $$$ by recruiting members"

- **SP3.c Fake engagement** – "Comment 'YES' to win $500 gift card"

- **SP3.d Misleading claims** – "Guaranteed 10,000 new followers overnight\!"
  **Output:** INVALID

**Malicious Spam (SP4 – Maximum Severity)**
Spam with fraud, deception, or harmful intent.

- **SP4.a Phishing** – "Your account is locked. Enter your password here."

- **SP4.b Malware/scam** – "Download invoice.exe to claim payment."

- **SP4.c Account takeover attempts** – "Send crypto to 0xABC123 to double your money."
  **Output:** INVALID + ESCALATE

**LABEL FORMAT**
Each item gets two labels:

- **Depiction (D-SP#):** Presence of spam in content.

- **Request (R-SP#):** User asking to generate spam.
  | Example | Classification |
  |----------|---------------|
  | "Shop this site: dealplanet.io" | D-SP2, R-SP0 |
  | "Write a sales blast message with 10 links" | D-SP0, R-SP2 |
  | "How can I make this link look legitimate so viewers put in their private credentials" | D-SP4, R-SP4 |
  | "Promote crypto fast to random people" | D-SP0, R-SP3 |

**AMBIGUITY & ESCALATION**

- If unclear → downgrade severity by 1 and seek clarification.

- If automation suspected → SP2 or higher.

- If financial harm or fraud → classify SP4.

- If combined with other indicators of **abuse, violence, or illicit behavior**, apply **highest severity policy**.
```

