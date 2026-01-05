# 大規模言語モデルの使い方

## 大規模言語モデルの仕組み

[大規模言語モデル][Large language models Blog Post]は、テキストをテキストにマッピングする関数です。入力されたテキスト文字列に対して、大規模言語モデルは次に来るべきテキストを予測します。

大規模言語モデルの魔法は、膨大な量のテキストに対してこの予測誤差を最小化するように訓練されることで、モデルがこれらの予測に有用な概念を学習することです。例えば、以下のようなことを学習します：

- スペルの仕方
- 文法の仕組み
- 言い換えの方法
- 質問への答え方
- 会話の持ち方
- 多言語での書き方
- コーディング
- その他

これらは、大量の既存テキストを「読む」ことで、単語が他の単語とどのような文脈で現れる傾向があるかを学習し、学習した内容を使ってユーザーのリクエストに対して次に現れる可能性が最も高い単語、そしてその後に続く各単語を予測することで実現されます。

GPT-3とGPT-4は、生産性アプリ、教育アプリ、ゲームなど、[多くのソフトウェア製品][OpenAI Customer Stories]を支えています。

## 大規模言語モデルの制御方法

大規模言語モデルへのすべての入力の中で、最も影響力があるのはテキストプロンプトです。

大規模言語モデルは、いくつかの方法で出力を生成するようプロンプトできます：

- **指示**: モデルに何をしてほしいかを伝える
- **補完**: モデルに欲しいもののはじまりを補完させる
- **シナリオ**: モデルに演じてもらう状況を与える
- **実演**: モデルに欲しいものを見せる、以下のいずれかで：
  - プロンプト内のいくつかの例
  - ファインチューニング訓練データセット内の数百または数千の例

以下にそれぞれの例を示します。

### 指示プロンプト

プロンプトの上部（または下部、または両方）に指示を書くと、モデルはその指示に従うよう最善を尽くし、その後停止します。指示は詳細にできるので、欲しい出力を明示的に詳述する段落を書くことを恐れる必要はありません。ただし、モデルが処理できる[トークン](https://help.openai.com/en/articles/4936856-what-are-tokens-and-how-to-count-them)数に注意してください。

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

補完スタイルのプロンプトは、大規模言語モデルが次に来ると思われる最も可能性の高いテキストを書こうとする特性を活用します。モデルを誘導するために、見たい出力によって補完されるパターンや文を始めてみてください。直接的な指示と比較して、この大規模言語モデルの誘導方法は、より注意深い実験が必要な場合があります。さらに、モデルは必ずしもどこで停止すべきかを知らないため、停止シーケンスや後処理が必要になることが多く、望ましい出力を超えて生成されたテキストを切り取る必要があります。

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

モデルに従うべきシナリオや演じる役割を与えることは、複雑なクエリや想像力豊かな回答を求める際に役立ちます。仮想的なプロンプトを使用する場合、状況、問題、またはストーリーを設定し、そのシナリオの登場人物やそのトピックの専門家であるかのようにモデルに応答を求めます。

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

### 実演プロンプトの例（few-shot学習）

補完スタイルのプロンプトと同様に、実演はモデルに何をしてほしいかを示すことができます。このアプローチは、モデルがプロンプトで提供されたいくつかの例から学習するため、few-shot学習と呼ばれることがあります。

実演プロンプトの例：

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

十分な訓練例があれば、カスタムモデルを[ファインチューニング][Fine Tuning Docs]できます。この場合、モデルは提供された訓練データからタスクを学習できるため、指示は不要になります。ただし、プロンプトが終了し出力が開始すべき時をモデルに伝えるために、区切りシーケンス（例：`->`や`###`、または入力に一般的に現れない文字列）を含めることが役立ちます。区切りシーケンスがないと、モデルが見たい答えを開始するのではなく、入力テキストを詳しく説明し続けるリスクがあります。

ファインチューニングされたプロンプトの例（類似のプロンプト-補完ペアでカスタム訓練されたモデル用）：

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

大規模言語モデルはテキストだけでなく、コードでも優秀です。OpenAIの[GPT-4][GPT-4 and GPT-4 Turbo]モデルがその代表例です。

GPT-4は以下を含む[数多くの革新的な製品][OpenAI Customer Stories]を支えています：

- [GitHub Copilot] (Visual Studioやその他のIDEでコードを自動補完)
- [Replit](https://replit.com/) (コードの補完、説明、編集、生成が可能)
- [Cursor](https://cursor.sh/) (AIとのペアプログラミング用に設計されたエディターでソフトウェアをより速く構築)

GPT-4は`gpt-3.5-turbo-instruct`などの以前のモデルよりも高度です。しかし、コーディングタスクでGPT-4を最大限活用するには、明確で具体的な指示を与えることが依然として重要です。その結果、良いプロンプトを設計するには、より注意深い配慮が必要になる場合があります。

### プロンプトのさらなるアドバイス

より多くのプロンプト例については、[OpenAI Examples][OpenAI Examples]をご覧ください。

一般的に、入力プロンプトはモデル出力を改善するための最良の手段です。以下のようなコツを試すことができます：

- **より具体的に** 例：出力をカンマ区切りリストにしたい場合は、カンマ区切りリストを返すよう求める。答えがわからない時に「わかりません」と言ってほしい場合は、「答えがわからない場合は『わかりません』と言ってください」と伝える。指示が具体的であるほど、モデルはより良く応答できます。
- **コンテキストを提供する**: モデルがリクエストの全体像を理解できるよう支援する。これには背景情報、欲しいもののサンプル/実演、またはタスクの目的の説明が含まれます。
- **モデルに専門家であるかのように答えるよう求める。** モデルに高品質な出力や専門家が書いたような出力を生成するよう明示的に求めることで、モデルが専門家が書くと思われるより高品質な答えを提供するよう促すことができます。「詳しく説明してください」や「段階的に説明してください」などのフレーズが効果的です。
- **モデルに推論を説明する一連のステップを書き下すよう促す。** 答えの背後にある「なぜ」を理解することが重要な場合は、モデルに推論を含めるよう促してください。これは、各答えの前に「[段階的に考えてみましょう](https://arxiv.org/abs/2205.11916)」のような行を追加するだけで実現できます。

[Fine Tuning Docs]: https://platform.openai.com/docs/guides/fine-tuning
[OpenAI Customer Stories]: https://openai.com/customer-stories
[Large language models Blog Post]: https://openai.com/research/better-language-models
[GitHub Copilot]: https://github.com/features/copilot/
[GPT-4 and GPT-4 Turbo]: https://platform.openai.com/docs/models/gpt-4-and-gpt-4-turbo
[GPT3 Apps Blog Post]: https://openai.com/blog/gpt-3-apps/
[OpenAI Examples]: https://platform.openai.com/examples