# 信頼性を向上させる技術

GPT-3 がタスクで失敗した場合、どうすべきでしょうか？

- より信頼性の高い答えを引き出すより良いプロンプトを探しますか？
- 数千の例に投資してカスタムモデルをファインチューニングしますか？
- モデルがタスクを実行できないと仮定して、先に進みますか？

簡単な答えはありません - 状況によります。ただし、タスクに論理的推論や複雑さが含まれる場合は、この記事の技術を試して、より信頼性が高く、高性能なプロンプトを構築することを検討してください。

## GPT-3 が複雑なタスクで失敗する理由

13 × 17 を計算するように求められた場合、答えがすぐに頭に浮かびますか？ほとんどの人にとって、おそらくそうではありません。しかし、それは人間が2桁の掛け算ができないという意味ではありません。数秒と紙とペンがあれば、13 × 17 = 130 + 70 + 21 = 221 を計算するのはそれほど大変ではありません。

同様に、GPT-3 に次のトークンを計算するのにかかる時間で実行するには複雑すぎるタスクを与えると、誤った推測を作り話する可能性があります。しかし、人間と同様に、それは必ずしもモデルがタスクを実行できないことを意味するわけではありません。物事を推論する時間とスペースがあれば、モデルは依然として確実に答えることができる可能性があります。

例として、`gpt-3.5-turbo-instruct` にジャグリングボールに関する次の数学問題を尋ねると、誤って答えます：

```gpt-3.5-turbo-instruct
Q: A juggler has 16 balls. Half of the balls are golf balls and half of the golf balls are blue. How many blue golf balls are there?
A:
```

```gpt-3.5-turbo-instruct
There are 8 blue golf balls.
```

これは、GPT-3 が簡単な数学問題を実行できないことを意味しますか？いいえ。実際、`Let's think step by step` でモデルにプロンプトすることで、モデルは問題を確実に解決します：

```gpt-3.5-turbo-instruct
Q: A juggler has 16 balls. Half of the balls are golf balls and half of the golf balls are blue. How many blue golf balls are there?
A: Let's think step by step.
```

```gpt-3.5-turbo-instruct
There are 16 balls in total.
Half of the balls are golf balls.
That means that there are 8 golf balls.
Half of the golf balls are blue.
That means that there are 4 blue golf balls.
```

もちろん、単一の例だけから、この `Let's think step by step` トリックが一般的に機能するのか、それともこの特定の問題で幸運だっただけなのかを判断するのは困難です。しかし、これは本当に機能します。単語の数学問題のベンチマークで、`Let's think step by step` トリックは GPT-3 の解決率を、役に立たない 18% からまともな 79% に大幅に引き上げました！

## モデルの能力はコンテキストに依存する

GPT-3 を使って学習する際の一般的な概念的な誤りは、その能力がすべてのコンテキストで固定されていると信じることです。例えば、GPT-3 が簡単な論理の質問を間違えた場合、簡単な論理ができないに違いないと考えることです。

しかし、`Let's think step by step` の例が示すように、GPT-3 の見かけ上の失敗は、モデルが正しい出力に向かって自分自身を導くのを助けるより良いプロンプトで改善できる場合があります。

## 複雑なタスクでの信頼性を向上させる方法

この記事の残りの部分では、複雑なタスクで大規模言語モデルの信頼性を向上させる技術を共有します。技術の一部は特定のタイプの問題に固有ですが、多くは広範囲のタスクに適用できる一般的な原則に基づいて構築されています。例えば：

- より明確な指示を与える
- 複雑なタスクをより単純なサブタスクに分割する
- モデルをタスクに集中させるために指示を構造化する
- 答える前に説明するようにモデルにプロンプトする
- 多くの可能な答えの正当化を求め、次に統合する
- 多くの出力を生成し、次にモデルを使用して最良のものを選択する
- パフォーマンスを最大化するためにカスタムモデルをファインチューニングする

## 複雑なタスクをより単純なタスクに分割する

モデルに考える時間とスペースを与える一つの方法は、タスクをより単純な部分に分割することです。

例として、テキストに関する多肢選択問題をモデルに尋ねるタスクを考えてみましょう - この場合、Clue のゲームです。直接尋ねられた場合、`gpt-3.5-turbo-instruct` は手がかり 3 と 5 を組み合わせることができず、誤って答えます：

```gpt-3.5-turbo-instruct
Use the following clues to answer the following multiple-choice question.

Clues:
1. Miss Scarlett was the only person in the lounge.
2. The person with the pipe was in the kitchen.
3. Colonel Mustard was the only person in the observatory.
4. Professor Plum was not in the library nor the billiard room.
5. The person with the candlestick was in the observatory.

Question: Was Colonel Mustard in the observatory with the candlestick?
(a) Yes; Colonel Mustard was in the observatory with the candlestick
(b) No; Colonel Mustard was not in the observatory with the candlestick
(c) Unknown; there is not enough information to determine whether Colonel Mustard was in the observatory with the candlestick

Solution:
```

```gpt-3.5-turbo-instruct
(c) Unknown; there is not enough information to determine whether Colonel Mustard was in the observatory with the candlestick
```

手がかり 3 と 5 が Colonel Mustard が展望台に唯一の人物であり、展望台にいる人物が燭台を持っていたことを確立しているにもかかわらず、モデルはそれらを正しい答え (a) Yes に組み合わせることができません。

しかし、答えを直接尋ねるのではなく、タスクを3つの部分に分割できます：

- まず、手がかりを1つずつ見ていき、手がかりが潜在的に関連しているかどうかを検討する
- 次に、関連する手がかりを組み合わせて、質問への答えを推論する
- 第三に、最終的な答えを書く：(a)、(b)、または (c) のいずれか

```gpt-3.5-turbo-instruct
Use the following clues to answer the following multiple-choice question, using the following procedure:
(1) First, go through the clues one by one and consider whether the clue is potentially relevant
(2) Second, combine the relevant clues to reason out the answer to the question
(3) Third, map the answer to one of the multiple choice answers: either (a), (b), or (c)

Clues:
1. Miss Scarlett was the only person in the lounge.
2. The person with the pipe was in the kitchen.
3. Colonel Mustard was the only person in the observatory.
4. Professor Plum was not in the library nor the billiard room.
5. The person with the candlestick was in the observatory.

Question: Was Colonel Mustard in the observatory with the candlestick?
(a) Yes; Colonel Mustard was in the observatory with the candlestick
(b) No; Colonel Mustard was not in the observatory with the candlestick
(c) Unknown; there is not enough information to determine whether Colonel Mustard was in the observatory with the candlestick

Solution:
(1) First, go through the clues one by one and consider whether the clue is potentially relevant:
```

```gpt-3.5-turbo-instruct
Clue 1: Miss Scarlett was the only person in the lounge. This clue is not relevant.
Clue 2: The person with the pipe was in the kitchen. This clue is not relevant.
Clue 3: Colonel Mustard was the only person in the observatory. This clue is relevant.
Clue 4: Professor Plum was not in the library nor the billiard room. This clue is not relevant.
Clue 5: The person with the candlestick was in the observatory. This clue is relevant.

(2) Second, combine the relevant clues to reason out the answer to the question:
Clue 3 and Clue 5 both say that the person with the candlestick was in the observatory. Colonel Mustard was the only person in the observatory, so Colonel Mustard was the person with the candlestick.

(3) Third, write the final answer:
(a) Yes; Colonel Mustard was in the observatory with the candlestick
```

モデルに考える時間とスペースを与え、推論計画に沿って導くことで、正しい答え (a) Yes を見つけることができます。

複雑な指示をより小さなサブタスクに分割するもう一つの利点は、モデルが各サブタスクに集中し続けるのに役立つことです。

たとえば、`gpt-3.5-turbo-instruct` にテキストを元の言語で要約するように依頼すると、モデルは英語に戻る可能性があります：

```gpt-3.5-turbo-instruct
Summarize the text using the original language of the text. The summary should be one sentence long.

Text:
"""
La estadística (la forma femenina del término alemán Statistik, derivado a su vez del italiano statista, "hombre de Estado")​ es una ciencia que estudia la variabilidad, colección, organización, análisis, interpretación, y presentación de los datos, así como el proceso aleatorio que los genera siguiendo las leyes de la probabilidad.​ La estadística es una ciencia formal deductiva, con un conocimiento propio, dinámico y en continuo desarrollo obtenido a través del método científico formal. En ocasiones, las ciencias fácticas necesitan utilizar técnicas estadísticas durante su proceso de investigación factual, con el fin de obtener nuevos conocimientos basados en la experimentación y en la observación. En estos casos, la aplicación de la estadística permite el análisis de datos provenientes de una muestra representativa, que busca explicar las correlaciones y dependencias de un fenómeno físico o natural, de ocurrencia en forma aleatoria o condicional.
"""

Summary:
```

```gpt-3.5-turbo-instruct
The text explains that statistics is a science that studies the variability, collection, organization, analysis, interpretation, and presentation of data, as well as the random process that generates them following the laws of probability.
```

しかし、最初にモデルにテキストの言語を識別するように依頼し、次にテキストを要約すると、より信頼性が高くなります：

```gpt-3.5-turbo-instruct
First, identify the language of the text. Second, summarize the text using the original language of the text. The summary should be one sentence long.

Text:
"""
La estadística (la forma femenina del término alemán Statistik, derivado a su vez del italiano statista, "hombre de Estado")​ es una ciencia que estudia la variabilidad, colección, organización, análisis, interpretación, y presentación de los datos, así como el proceso aleatorio que los genera siguiendo las leyes de la probabilidad.​ La estadística es una ciencia formal deductiva, con un conocimiento propio, dinámico y en continuo desarrollo obtenido a través del método científico formal. En ocasiones, las ciencias fácticas necesitan utilizar técnicas estadísticas durante su proceso de investigación factual, con el fin de obtener nuevos conocimientos basados en la experimentación y en la observación. En estos casos, la aplicación de la estadística permite el análisis de datos provenientes de una muestra representativa, que busca explicar las correlaciones y dependencias de un fenómeno físico o natural, de ocurrencia en forma aleatoria o condicional.
"""

Language:
```

```gpt-3.5-turbo-instruct
Spanish

La estadística es una ciencia que estudia la variabilidad, colección, organización, análisis, interpretación, y presentación de los datos, así como el proceso aleatorio que los genera siguiendo las leyes de la probabilidad.
```

## 答える前に説明するようにモデルにプロンプトする

答えの信頼性を向上させるもう一つの強力な技術は、最終的な答えにすぐにジャンプするのではなく、徐々に答えを推論するようにモデルにプロンプトすることです。「声に出して考える」ことで、モデルは正しい答えに到達する可能性がはるかに高くなります。

### ゼロショット

#### 方法

[Takeshi Kojima et al. によって2022年に発表された](https://arxiv.org/abs/2205.11916)、モデルに答えを推論させる最も簡単な方法は、答えの前に単に `Let's think step by step.` を追加することです。図2は例を示しています：

[![ゼロショット推論の例](/images/zero-shot_reasoners_fig2.png)
<br>出典：_Large Language Models are Zero-Shot Reasoners_ by Takeshi Kojima et al. (2022).](https://arxiv.org/abs/2205.11916)

#### 結果

この単純なトリックを MultiArith 数学データセットに適用したところ、著者は `Let's think step by step` が精度を4倍にし、18% から 79% に上昇したことを発見しました！

[![ゼロショット推論の例](/images/zero-shot_reasoners_tab5.png)
<br>出典：_Large Language Models are Zero-Shot Reasoners_ by Takeshi Kojima et al. (2022).](https://arxiv.org/abs/2205.11916)

#### 影響

`Let's think step by step` トリックは数学問題でうまく機能しますが、すべてのタスクで効果的ではありません。著者は、複数ステップの算術問題、記号推論問題、戦略問題、その他の推論問題で最も役立つことを発見しました。単純な数学問題や常識的な質問には役立たず、おそらく他の多くの非推論タスクにも役立たないでしょう。

[![ゼロショット推論の例](/images/zero-shot_reasoners_tab1.png)
<br>出典：_Large Language Models are Zero-Shot Reasoners_ by Takeshi Kojima et al. (2022).](https://arxiv.org/abs/2205.11916)

詳細については、[完全な論文](https://arxiv.org/abs/2205.11916)をお読みください。

この技術を自分のタスクに適用する場合は、指示のカスタマイズを試すことを恐れないでください。`Let's think step by step` はかなり一般的なので、ユースケースに合わせたより厳格な形式に従う指示でより良いパフォーマンスが得られる可能性があります。たとえば、`First, think step by step about why X might be true. Second, think step by step about why Y might be true. Third, think step by step about whether X or Y makes more sense.` のようなより構造化されたバリアントを試すことができます。モデルを軌道に乗せるのに役立つ例の形式を与えることさえできます。例えば：

```gpt-3.5-turbo-instruct
Using the IRS guidance below, answer the following questions using this format:
(1) For each criterion, determine whether it is met by the vehicle purchase
- {Criterion} Let's think step by step. {explanation} {yes or no, or if the question does not apply then N/A}.
(2) After considering each criterion in turn, phrase the final answer as "Because of {reasons}, the answer is likely {yes or no}."

IRS guidance:
"""
You may be eligible for a federal tax credit under Section 30D if you purchased a car or truck that meets the following criteria:
- Does the vehicle have at least four wheels?
- Does the vehicle weigh less than 14,000 pounds?
- Does the vehicle draw energy from a battery with at least 4 kilowatt hours that may be recharged from an external source?
- Was the vehicle purchased in a year before 2022?
  - If so, has the manufacturer sold less than 200,000 qualifying vehicles? (Tesla and GM have sold more than 200,000 qualifying vehicles.)
- Was the vehicle purchased in a year after 2022?
  - If so, is the vehicle present in the following list of North American-assembled vehicles? (The only electric vehicles assembled in North America are the Audi Q5, BMW 330e, BMW X5, Chevrolet Bolt EUV, Chevrolet Bolt EV, Chrysler Pacifica PHEV, Ford Escape PHEV, Ford F Series, Ford Mustang MACH E, Ford Transit Van, GMC Hummer Pickup, GMC Hummer SUV, Jeep Grand Cherokee PHEV, Jeep Wrangler PHEV, Lincoln Aviator PHEV, Lincoln Corsair Plug-in, Lucid Air, Nissan Leaf, Rivian EDV, Rivian R1S, Rivian R1T, Tesla Model 3, Tesla Model S, Tesla Model X, Tesla Model Y, Volvo S60, BMW 330e, Bolt EV, Cadillac Lyriq, Mercedes EQS SUV, and Nissan Leaf.)
"""

Question: Can I claim a federal tax credit for my Toyota Prius Prime bought in 2021?

Solution:

(1) For each criterion, determine whether it is met by the vehicle purchase
- Does the vehicle have at least four wheels? Let's think step by step.
```

```gpt-3.5-turbo-instruct
 The Toyota Prius Prime has four wheels, so the answer is yes.
- Does the vehicle weigh less than 14,000 pounds? Let's think step by step. The Toyota Prius Prime weighs less than 14,000 pounds, so the answer is yes.
- Does the vehicle draw energy from a battery with at least 4 kilowatt hours that may be recharged from an external source? Let's think step by step. The Toyota Prius Prime has a battery with at least 4 kilowatt hours that may be recharged from an external source, so the answer is yes.
- Was the vehicle purchased in a year before 2022? Let's think step by step. The Toyota Prius Prime was purchased in 2021, which is before 2022, so the answer is yes.
- Was the vehicle purchased in a year after 2022? N/A
- If so, is the vehicle present in the following list of North American-assembled vehicles? N/A

(2) After considering each criterion in turn, phrase the final answer as "Because of {reasons}, the answer is likely {yes or no}."

Because the Toyota Prius Prime meets all of the criteria for a federal tax credit, the answer is likely yes.
```

### Few-shot 例

#### 方法

モデルに答えを推論させることは、多くの方法で実行できます。一つの方法は、[Google の Jason Wei と Denny Zhou et al. によって研究された](https://ai.googleblog.com/2022/05/language-models-perform-reasoning-via.html)ように、いくつかの例（'few-shot'）で実証することです。以下は few-shot chain-of-thought プロンプトの例です：

[![chain of thought の例](/images/chain_of_thought_fig1.png)
<br>出典：_Chain of Thought Prompting Elicits Reasoning in Large Language Models_ Jason Wei and Denny Zhou et al. (2022)](https://ai.googleblog.com/2022/05/language-models-perform-reasoning-via.html)

人間のラベラーによって書かれた推論チェーンのさらなるデモンストレーション：

[![chain of thought の例](/images/chain_of_thought_fig3.png)
<br>出典：_Chain of Thought Prompting Elicits Reasoning in Large Language Models_ Jason Wei and Denny Zhou et al. (2022)](https://ai.googleblog.com/2022/05/language-models-perform-reasoning-via.html)

[（梨が実際に浮くかどうかは疑問視されていることに注意してください）](https://twitter.com/Meaningness/status/1561062170074370048?s=20&t=mpHt8f3RRboztXxdhLFnWQ)

#### 結果

小学校の数学問題でテストしたところ、著者は chain of thought プロンプティングが解決率を3倍にし、18% から 57% に上昇したことを発見しました。

[![chain of thought の例](/images/chain_of_thought_fig5.png)
<br>出典：_Chain of Thought Prompting Elicits Reasoning in Large Language Models_ Jason Wei and Denny Zhou et al. (2022)](https://ai.googleblog.com/2022/05/language-models-perform-reasoning-via.html)

数学問題に加えて、chain of thought プロンプティングは、スポーツ理解、コインフリップ追跡、最後の文字連結に関連する質問でもパフォーマンスを向上させました。ほとんどの場合、パフォーマンスの向上を飽和させるために多くの例は必要ありませんでした（8個程度未満）。

[![chain of thought の例](/images/chain_of_thought_fig11.png)
<br>出典：_Chain of Thought Prompting Elicits Reasoning in Large Language Models_ Jason Wei and Denny Zhou et al. (2022)](https://ai.googleblog.com/2022/05/language-models-perform-reasoning-via.html)

詳細については、[完全な論文](https://arxiv.org/abs/2201.11903)をお読みください。

#### 影響

`Let's think step by step` 技術と比較した few-shot 例ベースのアプローチの一つの利点は、最終的な答えに到達する前にモデルが実行したい推論の形式、長さ、スタイルをより簡単に指定できることです。これは、モデルが最初に正しい方法や深さで推論していない場合に特に役立ちます。

### ファインチューニング

#### 方法

一般的に、タスクで最大のパフォーマンスを引き出すには、カスタムモデルをファインチューニングする必要があります。ただし、説明を使用してモデルをファインチューニングするには、書くのにコストがかかる数千の説明例が必要になる場合があります。

2022年、Eric Zelikman と Yuhuai Wu et al. は、few-shot プロンプトを使用して、モデルのファインチューニングに使用できる説明のデータセットを生成する巧妙な手順を発表しました。アイデアは、few-shot プロンプトを使用して候補説明を生成し、正しい答えを生成する説明のみを保持することです。次に、誤った答えの一部について追加の説明を取得するために、質問の一部として正しい答えが与えられた few-shot プロンプトを再試行します。著者はこの手順を STaR（Self-taught Reasoner）と呼びました：

[![STaR 手順](/images/star_fig1.png)
<br>出典：_STaR: Bootstrapping Reasoning With Reasoning_ by Eric Zelikman and Yujuai Wu et al. (2022)](https://arxiv.org/abs/2203.14465)

この技術を使用すると、数千の説明例を書く必要なく、ファインチューニングの利点と chain-of-thought プロンプティングの利点を組み合わせることができます。

#### 結果

著者がこの技術を Common Sense Q&A データセットに適用したところ、STaR が chain-of-thought プロンプティング単独（73% > 37%）とファインチューニング単独（73% > 60%）の両方を上回ったことを発見しました：

[![STaR 結果](/images/star_tab1.png)
<br>出典：_STaR: Bootstrapping Reasoning With Reasoning_ by Eric Zelikman and Yujuai Wu et al. (2022)](https://arxiv.org/abs/2203.14465)

詳細については、[完全な論文](https://arxiv.org/abs/2203.14465)をお読みください。

#### 影響

few-shot プロンプトを使用してファインチューニングデータセットを拡張または変更するというアイデアは、説明の記述を超えて一般化できます。たとえば、トレーニングしたい大量の非構造化テキストがある場合、プロンプトを使用して非構造化テキストから構造化データセットを抽出し、その構造化データセットでカスタムモデルをファインチューニングする機会が見つかる可能性があります。

## Chain-of-thought プロンプティングの拡張

Chain-of-thought プロンプティングの多くの拡張も発表されています。

### Selection-inference プロンプティング

#### 方法

Antonia Creswell et al. によって発表された、chain-of-thought 技術の一つの拡張は、説明と答えを生成するための単一のプロンプトをより小さな部分に分割することです。まず、プロンプトがテキストから関連する事実のサブセットを選択します（'selection prompt'）。次に、2番目のプロンプトが選択された事実から結論を推論します（'inference prompt'）。これらのプロンプトは、複数の推論ステップを生成し、最終的に最終的な答えに到達するためにループ内で交互に実行されます。著者は次の図でアイデアを示しています：

[![Selection-inference プロンプティング](/images/selection-inference_fig1.png)
<br>出典：_Selection-Inference: Exploiting Large Language Models for Interpretable Logical Reasoning_ by Antonia Creswell et al. (2022)](https://arxiv.org/abs/2205.09712)

#### 結果

7B パラメータモデルに適用されたとき、著者は selection-inference プロンプティングが bAbi と Proof Writer ベンチマークタスク（両方とも長い推論ステップのシーケンスを必要とする）で chain-of-thought プロンプティングと比較してパフォーマンスを大幅に向上させたことを発見しました。彼らが達成した最高のパフォーマンスは、selection-inference プロンプティングとファインチューニングの両方を組み合わせたものでした。

[![Selection-inference プロンプティング](/images/selection-inference_fig4.png)
<br>出典：_Selection-Inference: Exploiting Large Language Models for Interpretable Logical Reasoning_ by Antonia Creswell et al. (2022)](https://arxiv.org/abs/2205.09712)

#### 影響

これらのベンチマークでの向上は大きかったものの、これらのベンチマークは長い推論シーケンスを必要とするために特別に選択されました。多くのステップで推論を必要としない問題では、向上はおそらく小さいでしょう。

結果は、大規模言語モデルを使用する際の一般的な教訓をいくつか強調しています。一つ、複雑なタスクをより小さなタスクに分割することは、信頼性とパフォーマンスを向上させる素晴らしい方法です。タスクがより原子的であればあるほど、モデルが誤る余地は少なくなります。二つ、最大のパフォーマンスを得るには、選択したアプローチとファインチューニングを組み合わせることがしばしば意味します。

詳細については、[完全な論文](https://arxiv.org/abs/2205.09712)をお読みください。

### Faithful reasoning アーキテクチャ

selection-inference プロンプティング技術を発表してから数ヶ月後、著者はフォローアップ論文で技術を拡張し、以下のアイデアを提供しました：

- selection-inference サイクルをいつ停止または継続すべきかを判断する
- 複数の推論パスを検索するのに役立つ価値関数を追加する
- 文自体を書き出すのではなく、文ラベル（例：sen1）について推論するようにモデルをファインチューニングすることで、偽の事実の幻覚を減らす

#### 方法

元の selection-inference 技術では、特殊な 'selection' と 'inference' プロンプトが交互に実行されて、事実を選択し、それらの事実から推論を行い、推論ステップのシーケンスを生成します。

著者は、この技術を2つの追加コンポーネントで拡張します。

まず、著者は 'halter' モデルを追加します。これは、各推論ステップの後に、これまでの推論が質問に答えるのに十分かどうかを尋ねられます。はいの場合、モデルは最終的な答えを生成します。

halter モデルはいくつかの利点をもたらします：

- 必要に応じて selection-inference プロセスを停止または続行するように指示できます。
- プロセスが停止しない場合、答えは得られません。これは、幻覚的な推測よりもしばしば好ましいです。

[![Faithful reasoning](/images/faithful-reasoning_fig3.png)
<br>出典：_Faithful Reasoning Using Large Language Models_ by Antonia Creswell et al. (2022)](https://arxiv.org/abs/2208.14271)

[![Faithful reasoning](/images/faithful-reasoning_fig5.png)
<br>出典：_Faithful Reasoning Using Large Language Models_ by Antonia Creswell et al. (2022)](https://arxiv.org/abs/2208.14271)

次に、著者は価値関数を追加します。これは、推論ステップの品質を評価し、複数の推論軌跡を検索するために使用されます。これは、信頼性を高めるための共通のテーマを反映しています。モデルから単一の答えを生成するのではなく、答えのセットを生成し、次に何らかの価値関数/識別器/検証器モデルを使用して最良のものを選択します。

[![Faithful reasoning](/images/faithful-reasoning_fig7.png)
<br>出典：_Faithful Reasoning Using Large Language Models_ by Antonia Creswell et al. (2022)](https://arxiv.org/abs/2208.14271)

これら2つの拡張に加えて、著者は偽の事実の幻覚を減らすトリックも使用します。モデルに事実の文を書き出すように依頼するのではなく、代わりに文ラベル（例：sen1）で作業するようにモデルをファインチューニングします。これにより、プロンプトコンテキストで言及されていない偽の事実をモデルが幻覚するのを防ぐのに役立ちます。

[![Faithful reasoning](/images/faithful-reasoning_fig4.png)
<br>出典：_Faithful Reasoning Using Large Language Models_ by Antonia Creswell et al. (2022)](https://arxiv.org/abs/2208.14271)

#### 結果

著者は、2つのベンチマークで技術を評価しました：ProofWriter タスク（表示されていません）と [EntailmentBankQA](https://allenai.org/data/entailmentbank)（表示されています）。この技術は、特により困難な推論問題で、精度を大幅に向上させました。

![Faithful reasoning](/images/faithful-reasoning_tab2.png)
<br>出典：_Faithful Reasoning Using Large Language Models_ by Antonia Creswell et al. (2022)](https://arxiv.org/abs/2208.14271)

さらに、彼らの文ラベル操作トリックは、幻覚を本質的に排除しました！

![Faithful reasoning](/images/faithful-reasoning_tab5.png)
<br>出典：_Faithful Reasoning Using Large Language Models_ by Antonia Creswell et al. (2022)](https://arxiv.org/abs/2208.14271)

#### 影響

この論文は、大規模言語モデルの信頼性を向上させるための多くの役立つ教訓を示しています：

- 複雑なタスクをより小さく、より信頼性の高いサブタスクに分割する
- ステップバイステップの方法で答えを生成し、途中で評価する
- 多くの可能な答えを生成し、別のモデルまたは関数を使用して最良に見えるものを選択する
- モデルが言えることを制約することで幻覚を減らす（例：文の代わりに文ラベルを使用することによって）
- 特殊なタスクでモデルをファインチューニングすることでモデルのパフォーマンスを最大化する

詳細については、[完全な論文](https://arxiv.org/abs/2205.09712)をお読みください。

### Least-to-most プロンプティング

長い推論チェーン（selection-inference が輝く場所）でうまくいかないことに加えて、chain-of-thought プロンプティングは、例が短いがタスクが長い場合に特に苦労する可能性があります。

#### 方法

Least-to-most プロンプティングは、推論タスクをより小さく、より信頼性の高いサブタスクに分割するもう一つの技術です。アイデアは、`To solve {question}, we need to first solve: "` のようなもので促すことで、モデルからサブタスクを引き出すことです。次に、そのサブタスクを手に持って、モデルは解決策を生成できます。解決策は元の質問に追加され、最終的な答えが生成されるまでプロセスが繰り返されます。

[![Least-to-most プロンプティング](/images/least-to-most_fig1.png)
<br>出典：_Least-to-most Prompting Enables Complex Reasoning in Large Language Models_ by Denny Zhou et al. (2022)](https://arxiv.org/abs/2205.10625)

#### 結果

`code-davinci-002`（コード用に最適化されていますが、テキストも理解できる）を使用した長い推論チェーンを含むベンチマークに適用されたとき、著者は 16% -> 99.7% もの大きな向上を測定しました！

[
![Least-to-most プロンプティング結果 last-letter-concatenation タスクで](/images/least-to-most_tab4.png)
![Least-to-most プロンプティング結果 SCAN で](/images/least-to-most_tab9.png)
![Least-to-most プロンプティング結果 DROP 数値推論で](/images/least-to-most_tab11.png)
<br>出典：_Least-to-most Prompting Enables Complex Reasoning in Large Language Models_ by Denny Zhou et al. (2022)](https://arxiv.org/abs/2205.10625)

#### 影響

least-to-most プロンプティングからの上記の向上は印象的ですが、長い推論チェーンを必要とする非常に狭いタスクセットで測定されています。

それでも、共通のテーマを示しています：(a) 複雑なタスクをより小さなサブタスクに分割し、(b) モデルに答えを解決する時間とスペースを与えることで、信頼性を高めます。

詳細については、[完全な論文](https://arxiv.org/abs/2205.10625)をお読みください。

## 関連するアイデア

### Maieutic プロンプティング

#### 方法

正しい答えの可能性を最大化しようとする以前の技術とは対照的に、別のアプローチは、GPT-3 を使用して可能な説明のツリー（正しい_と誤った_両方）を生成し、次にそれらの関係を分析してどのセットが正しいかを推測することです。この技術は、[2022年5月に Jaehun Jung et al. によって](https://arxiv.org/abs/2205.11822) maieutic プロンプティングと名付けられました（maieutic はソクラテス式の質問方法に関連することを意味します）。

方法は複雑で、次のように機能します：

- まず、maieutic ツリーを構築します。ここで、各ノードは真または偽である可能性のあるステートメントです：
  - 多肢選択問題または真/偽のステートメントから始めます（例：`War cannot have a tie`）
  - 質問への各可能な答えに対して、モデルを使用して対応する説明を生成します（`War cannot have a tie? True, because` のようなプロンプトで）
  - 次に、質問と生成された説明でモデルにプロンプトし、答えを生成するように依頼します。説明を逆にする（`It is wrong to say that {explanation}` のような接頭辞で）と答えが逆になる場合、説明は「論理的に不可欠」と見なされます。
  - 説明が論理的に不可欠でない場合は、上記のプロセスを再帰的に繰り返し、各説明を True または False の質問に変換し、各新しい質問についてさらに説明を生成します。
  - すべての再帰的な説明が完了すると、説明のツリーができあがり、ツリーの各葉には、説明を逆にすると答えが逆になるというプロパティがあります。
- 次に、ツリーを関係のグラフに変換します：
  - ツリー内の各ノードについて、各ノードに対するモデルの相対的な信念を計算します（説明が与えられたときに `True` の答えを得る確率から推測）
  - ツリー内の各ノードペアについて、モデルを使用してそれらが含意（暗示）されているか矛盾しているかを識別します
- 第三に、最も一貫性のある信念のセットを見つけ、それらを真実とします：
  - 具体的には、各ノードの信念の強さとそれらの間の論理関係を使用して、問題を重み付き最大充足可能性問題（MAX-SAT）として定式化します
  - ソルバーを使用して、最も自己一貫性のある信念のセットを見つけ、それらを真実とします

[
![Maieutic プロンプティング](/images/maieutic_fig2.png)
![Maieutic プロンプティング](/images/maieutic_fig6.png)
<br>出典：_Maieutic Prompting: Logically Consistent Reasoning with Recursive Explanations_ by Jaehun Jung et al. (2022)](https://arxiv.org/abs/2205.11822)

#### 結果

[![Maieutic プロンプティング結果](/images/maieutic_tab1.png)
<br>出典：_Maieutic Prompting: Logically Consistent Reasoning with Recursive Explanations_ by Jaehun Jung et al. (2022)](https://arxiv.org/abs/2205.11822)

#### 影響

複雑さを超えて、この方法の一つの制限は、多肢選択として提起できる質問にのみ適用されるように見えることです。

詳細については、[完全な論文](https://arxiv.org/abs/2205.11822)をお読みください。

## 拡張

### Self-consistency

#### 方法

答えの離散的なセットを持つタスクの場合、信頼性を向上させる一つの簡単な方法は、モデルから複数の説明と答えをサンプリングし（正の温度を使用）、次に最も頻繁に現れる最終的な答えを選択することです。

[![Self-consistency 方法](/images/self-consistency_fig1.png)
<br>出典：_Self-Consistency Improves Chain of Thought Reasoning in Language Models_ by Xuezhi Wang et al. (2022)](https://arxiv.org/abs/2203.11171)

#### 結果

この技術は、数学と推論のベンチマークスイートで精度を1から24パーセントポイント向上させました。（以下にプロットされているのは Google の LaMDA モデルからの結果です。Google のより大きな PaLM モデルを使用すると、ベースラインは高くなりましたが、向上は少し小さくなりました。）

[![Self-consistency 結果](/images/self-consistency_fig3.png)
<br>出典：_Self-Consistency Improves Chain of Thought Reasoning in Language Models_ by Xuezhi Wang et al. (2022)](https://arxiv.org/abs/2203.11171)

#### 影響

この技術は実装が簡単ですが、コストがかかる可能性があります。10個の答えのセットを生成すると、コストが10倍になります。

また、これらの技術の多くと同様に、答えの限定されたセットを持つタスクにのみ適用されます。各答えがユニークな open-ended タスク（詩を書くなど）の場合、最も一般的な答えを選択することが何を意味するのかは明らかではありません。

最後に、この技術は、答えに到達する複数のパスまたは言い回しがある場合に最も有益であるはずです。パスが1つしかない場合、技術はまったく役立たない可能性があります。極端な例：タスクが単一のトークンの答えを生成することである場合、100個の生成から最も一般的なトークンを取ることは、最も高い logprobs を持つトークンを取ること（temperature=0 で単一の生成で取得できる）と変わりません。

### Verifiers

タスクパフォーマンスを向上させるもう一つの重要な技術は、メインの生成モデルの出力を評価するために検証器または識別器モデルをトレーニングすることです。識別器が出力を拒否した場合、許容可能な出力が得られるまで生成モデルを再サンプリングできます。多くの場合、答えを作成するよりも答えを判断する方が簡単であり、この方法の力を説明するのに役立ちます。

#### 方法

2021年、OpenAI の研究者は、次の手順を使用して、小学校の数学問題にこの技術を適用しました：

- まず、質問と解決策に対してモデルをファインチューニングしました
- トレーニングセットの各問題について、100個の解決策を生成しました
- これらの100個の解決策のそれぞれは、最終的な答えが正しいかどうかに基づいて、正しいまたは誤りとして自動的にラベル付けされました
- 正しいとラベル付けされたものと誤りとラベル付けされたものを含むこれらの解決策を使用して、質問と候補解決策が正しいか誤りかを分類するために検証器モデルをファインチューニングしました
- 最後に、テスト時に、生成モデルは各問題に対して100個の解決策を作成し、検証器モデルによると最も高いスコアを持つものが最終的な答えとして選択されます

[![Verifier 方法](/images/verifiers_fig3.png)
<br>出典：_Training Verifiers to Solve Math Word Problems_ by Karl Cobbe et al. (2021)](https://arxiv.org/abs/2110.14168)

#### 結果

175B GPT-3 モデルと8,000個のトレーニング例を使用して、この技術は小学校の数学の精度を約33%から約55%に大幅に向上させました。

[![Verifier 結果](/images/verifiers_fig5.png)
<br>出典：_Training Verifiers to Solve Math Word Problems_ by Karl Cobbe et al. (2021)](https://arxiv.org/abs/2110.14168)

#### 影響

self-consistency 技術と同様に、この方法はコストがかかる可能性があります。タスクごとに100個の解決策を生成すると、コストが約100倍になります。

## 信頼性の理論

上記の技術はアプローチが異なりますが、すべて複雑なタスクでの信頼性を向上させるという目標を共有しています。主に次のことによって行います：

- 信頼性の低い操作をより小さく、より信頼性の高い操作に分解する（例：selection-inference プロンプティング）
- 複数のステップまたは複数の関係を使用して、システムの信頼性を個々のコンポーネントよりも大きくする（例：maieutic プロンプティング）

### 確率的グラフィカルモデル

信頼性の低いコンポーネントから信頼性の高いシステムを構築しようとするこのパラダイムは、確率的プログラミングを思い起こさせ、その分野の多くの分析技術をこの分野に適用できます。

論文 _Language Model Cascades_ で、David Dohan et al. は、上記の技術を確率的グラフィカルモデルのパラダイムで解釈しています：

#### Chain of thought プロンプティング

[![chain of thought プロンプティングのグラフィカルモデル](/images/lm_cascades_fig1.png)
<br>出典：_Language Model Cascades_ by David Dohan et al. (2022)](https://arxiv.org/abs/2207.10342)

#### ファインチューニングされた chain of thought プロンプティング / Self-taught reasoner

[![ファインチューニングされた chain of thought プロンプティングのグラフィカルモデル](/images/lm_cascades_fig3.png)
<br>出典：_Language Model Cascades_ by David Dohan et al. (2022)](https://arxiv.org/abs/2207.10342)

#### Selection-inference プロンプティング

[![selection-inference プロンプティングのグラフィカルモデル](/images/lm_cascades_fig4.png)
<br>出典：_Language Model Cascades_ by David Dohan et al. (2022)](https://arxiv.org/abs/2207.10342)

#### Verifiers

[![verifiers のグラフィカルモデル](/images/lm_cascades_fig5.png)
<br>出典：_Language Model Cascades_ by David Dohan et al. (2022)](https://arxiv.org/abs/2207.10342)

#### 影響

これらの技術を確率的グラフィカルモデルとして定式化することは、特定の問題を解決するためにすぐに役立つわけではありませんが、フレームワークは技術を選択、組み合わせ、発見するのに役立つ可能性があります。

## 最後に

大規模言語モデルの研究は非常に活発で、急速に進化しています。研究者はモデルを改善し続けるだけでなく、モデルを最善に使用する方法についての理解も改善し続けています。これらの開発のペースを強調するために、上記で共有されたすべての論文は過去12ヶ月以内に発表されたことに注意してください（2022年9月に執筆時点）。

将来的には、より良いモデルとより良い技術が発表されることを期待してください。ここでの特定の技術が将来のベストプラクティスに取って代わられたとしても、それらの背後にある一般的な原則は、おそらく専門家ユーザーのツールキットの重要な部分であり続けるでしょう。

## 参考文献

| 教訓                                                                                                                         | 論文                                                                                                                                     | 日付     |
| ------------------------------------------------------------------------------------------------------------------------------ | ----------------------------------------------------------------------------------------------------------------------------------------- | -------- |
| 複雑なタスクをより単純なサブタスクに分割する（中間出力をユーザーに公開することを検討する）                            | [AI Chains: Transparent and Controllable Human-AI Interaction by Chaining Large Language Model Prompts](https://arxiv.org/abs/2110.01691) | 2021年10月 |
| 多くの候補を生成し、最良に見えるものを選択することで出力を改善できます                                 | [Training Verifiers to Solve Math Word Problems](https://arxiv.org/abs/2110.14168)                                                        | 2021年10月 |
| 推論タスクでは、答える前にステップバイステップで推論する場合、モデルはより良くなります                                            | [Chain of Thought Prompting Elicits Reasoning in Large Language Models](https://arxiv.org/abs/2201.11903)                                 | 2022年1月 |
| 多くの説明-答えの出力を生成し、最も人気のある答えを選択することで、ステップバイステップの推論を改善できます      | [Self-Consistency Improves Chain of Thought Reasoning in Language Models](https://arxiv.org/abs/2203.11171)                               | 2022年3月 |
| ステップバイステップの推論器をファインチューニングしたい場合、多肢選択問題と答えのデータだけで実行できます              | [STaR: Bootstrapping Reasoning With Reasoning](https://arxiv.org/abs/2203.14465)                                                          | 2022年3月 |
| ステップバイステップの推論方法は、ゼロ例でも素晴らしく機能します                                                          | [Large Language Models are Zero-Shot Reasoners](https://arxiv.org/abs/2205.11916)                                                         | 2022年5月 |
| 'selection' プロンプトと 'inference' プロンプトを交互に実行することで、ステップバイステップの推論よりも良くできます                    | [Selection-Inference: Exploiting Large Language Models for Interpretable Logical Reasoning](https://arxiv.org/abs/2205.09712)             | 2022年5月 |
| 長い推論問題では、問題を段階的に解決する部分に分割することで、ステップバイステップの推論を改善できます | [Least-to-most Prompting Enables Complex Reasoning in Large Language Models](https://arxiv.org/abs/2205.10625)                            | 2022年5月 |
| モデルに良い説明と偽の説明の両方を分析させて、どの説明のセットが最も一貫しているかを把握させることができます    | [Maieutic Prompting: Logically Consistent Reasoning with Recursive Explanations](https://arxiv.org/abs/2205.11822)                        | 2022年5月 |
| これらの技術を確率的プログラミングの観点から考えることができます。システムは信頼性の低いコンポーネントで構成されます       | [Language Model Cascades](https://arxiv.org/abs/2207.10342)                                                                               | 2022年7月 |
| 文ラベル操作で幻覚を排除でき、'halter' プロンプトで誤った答えを減らすことができます      | [Faithful Reasoning Using Large Language Models](https://arxiv.org/abs/2208.14271)                                                        | 2022年8月 |

