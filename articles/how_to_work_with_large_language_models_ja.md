# 大規模言語モデルの使い方

## 大規模言語モデルの仕組み

[大規模言語モデル][Large language models Blog Post]は、テキストをテキストにマッピングする関数です。入力されたテキスト文字列が与えられると、大規模言語モデルは次に来るべきテキストを予測します。

大規模言語モデルの魔法は、膨大な量のテキストに対してこの予測誤差を最小化するように訓練されることで、モデルがこれらの予測に有用な概念を学習することです。たとえば、次のことを学習します：

- スペルの仕方
- 文法の仕組み
- 言い換えの方法
- 質問への答え方
- 会話の持ち方
- 多くの言語での書き方
- コードの書き方
- など

モデルは、大量の既存のテキストを「読む」ことで、単語が他の単語とのコンテキストでどのように現れる傾向があるかを学習し、学習したことを使用して、ユーザーのリクエストに応答して現れる可能性が最も高い次の単語と、その後の各単語を予測します。

GPT-3 と GPT-4 は、生産性アプリ、教育アプリ、ゲームなど、[多くのソフトウェア製品][OpenAI Customer Stories]を支えています。

## 大規模言語モデルの制御方法

大規模言語モデルへのすべての入力の中で、最も影響力があるのはテキストプロンプトです。

大規模言語モデルは、いくつかの方法で出力を生成するようにプロンプトできます：

- **指示（Instruction）**：モデルに何をしてほしいかを伝える
- **補完（Completion）**：モデルに、あなたが望むものの始まりを補完させる
- **シナリオ（Scenario）**：モデルに演じる状況を与える
- **デモンストレーション（Demonstration）**：モデルに何をしてほしいかを示す：
  - プロンプト内のいくつかの例
  - ファインチューニング訓練データセット内の数百または数千の例

それぞれの例を以下に示します。

### 指示プロンプト

プロンプトの上部（または下部、または両方）に指示を書くと、モデルは指示に従い、その後停止するように最善を尽くします。指示は詳細にできるため、出力を明示的に詳述する段落を書くことを恐れないでください。ただし、モデルが処理できる[トークン](https://help.openai.com/en/articles/4936856-what-are-tokens-and-how-to-count-them)の数に注意してください。

指示プロンプトの例：

```text
Extract the name of the author from the quotation below.

"Some humans theorize that intelligent species go extinct before they can expand into outer space. If they're correct, then the hush of the night sky is the silence of the graveyard."
― Ted Chiang, Exhalation
```

出力：

```text
Ted Chiang
```

### 補完プロンプトの例

補完スタイルのプロンプトは、大規模言語モデルが次に来る可能性が最も高いと思われるテキストを書こうとする方法を利用します。モデルを誘導するには、見たい出力によって補完されるパターンや文を始めてみてください。直接的な指示と比較して、このモードで大規模言語モデルを誘導するには、より多くの注意と実験が必要になる場合があります。さらに、モデルは必ずしもどこで停止すべきかを知らないため、望ましい出力を超えて生成されたテキストを切り取るために、停止シーケンスまたは後処理が必要になることがよくあります。

補完プロンプトの例：

```text
"Some humans theorize that intelligent species go extinct before they can expand into outer space. If they're correct, then the hush of the night sky is the silence of the graveyard."
― Ted Chiang, Exhalation

The author of this quote is
```

出力：

```text
 Ted Chiang
```

### シナリオプロンプトの例

モデルに従うシナリオや演じる役割を与えることは、複雑なクエリや想像力豊かな応答を求める場合に役立ちます。仮定のプロンプトを使用する場合、状況、問題、またはストーリーを設定し、そのシナリオのキャラクターまたはトピックの専門家であるかのようにモデルに応答を求めます。

シナリオプロンプトの例：

```text
Your role is to extract the name of the author from any given text

"Some humans theorize that intelligent species go extinct before they can expand into outer space. If they're correct, then the hush of the night sky is the silence of the graveyard."
― Ted Chiang, Exhalation
```

出力：

```text
 Ted Chiang
```

### デモンストレーションプロンプトの例（few-shot learning）

補完スタイルのプロンプトと同様に、デモンストレーションはモデルに何をしてほしいかを示すことができます。このアプローチは、プロンプトで提供されるいくつかの例からモデルが学習するため、few-shot learning と呼ばれることがあります。

デモンストレーションプロンプトの例：

```text
Quote:
"When the reasoning mind is forced to confront the impossible again and again, it has no choice but to adapt."
― N.K. Jemisin, The Fifth Season
Author: N.K. Jemisin

Quote:
"Some humans theorize that intelligent species go extinct before they can expand into outer space. If they're correct, then the hush of the night sky is the silence of the graveyard."
― Ted Chiang, Exhalation
Author:
```

出力：

```text
 Ted Chiang
```

### ファインチューニングされたプロンプトの例

十分な訓練例があれば、[ファインチューニング][Fine Tuning Docs]でカスタムモデルを作成できます。この場合、モデルは提供された訓練データからタスクを学習できるため、指示は不要になります。ただし、プロンプトが終了し、出力が開始されるべきタイミングをモデルに伝えるために、セパレーターシーケンス（例：`->`、`###`、または入力に一般的に現れない文字列）を含めると役立つ場合があります。セパレーターシーケンスがないと、モデルが見たい答えを開始するのではなく、入力テキストの詳細を続ける危険性があります。

ファインチューニングされたプロンプトの例（同様のプロンプト-補完ペアでカスタム訓練されたモデルの場合）：

```text
"Some humans theorize that intelligent species go extinct before they can expand into outer space. If they're correct, then the hush of the night sky is the silence of the graveyard."
― Ted Chiang, Exhalation

###


```

出力：

```text
 Ted Chiang
```

## コード機能

大規模言語モデルはテキストだけでなく、コードでも優れています。OpenAI の [GPT-4][GPT-4 and GPT-4 Turbo] モデルはその代表例です。

GPT-4 は、以下を含む[多くの革新的な製品][OpenAI Customer Stories]を支えています：

- [GitHub Copilot]（Visual Studio やその他の IDE でコードを自動補完）
- [Replit](https://replit.com/)（コードの補完、説明、編集、生成が可能）
- [Cursor](https://cursor.sh/)（AI とのペアプログラミング用に設計されたエディターでソフトウェアをより速く構築）

GPT-4 は、`gpt-3.5-turbo-instruct` のような以前のモデルよりも高度です。ただし、コーディングタスクで GPT-4 から最高のものを引き出すには、明確で具体的な指示を与えることが依然として重要です。その結果、優れたプロンプトの設計には、より多くの注意が必要になる場合があります。

### その他のプロンプトアドバイス

プロンプトの例については、[OpenAI Examples][OpenAI Examples] をご覧ください。

一般的に、入力プロンプトはモデル出力を改善するための最良のレバーです。次のようなトリックを試すことができます：

- **より具体的にする** 例：出力をカンマ区切りリストにしたい場合は、カンマ区切りリストを返すように依頼します。答えがわからないときに「わかりません」と言ってほしい場合は、「答えがわからない場合は『わかりません』と言ってください」と伝えます。指示が具体的であればあるほど、モデルはより良く応答できます。
- **コンテキストを提供する**：リクエストの全体像をモデルが理解できるようにします。これには、背景情報、望むものの例/デモンストレーション、またはタスクの目的の説明が含まれます。
- **モデルに専門家であるかのように答えるように依頼する。** モデルに高品質の出力を生成するように、または専門家が書いたかのように出力するように明示的に依頼すると、モデルは専門家が書くと思われるより高品質な答えを提供するように誘導できます。「詳細に説明する」や「ステップバイステップで説明する」などのフレーズが効果的です。
- **モデルに推論を説明する一連のステップを書き留めるようにプロンプトする。** 答えの背後にある「なぜ」を理解することが重要な場合は、モデルに推論を含めるようにプロンプトします。これは、各答えの前に「[Let's think step by step](https://arxiv.org/abs/2205.11916)」のような行を追加するだけで実行できます。

[Fine Tuning Docs]: https://platform.openai.com/docs/guides/fine-tuning
[OpenAI Customer Stories]: https://openai.com/customer-stories
[Large language models Blog Post]: https://openai.com/research/better-language-models
[GitHub Copilot]: https://github.com/features/copilot/
[GPT-4 and GPT-4 Turbo]: https://platform.openai.com/docs/models/gpt-4-and-gpt-4-turbo
[GPT3 Apps Blog Post]: https://openai.com/blog/gpt-3-apps/
[OpenAI Examples]: https://platform.openai.com/examples

