# 信頼性を向上させるテクニック

GPT-3がタスクで失敗した場合、どうすべきでしょうか？

- より信頼性の高い回答を引き出すより良いプロンプトを探すべきでしょうか？
- カスタムモデルをファインチューニングするために数千の例に投資すべきでしょうか？
- モデルがそのタスクを実行できないと仮定して、次に進むべきでしょうか？

簡単な答えはありません - それは状況によります。しかし、あなたのタスクが論理的推論や複雑さを含む場合は、この記事のテクニックを試して、より信頼性が高く、高性能なプロンプトを構築することを検討してください。

## GPT-3が複雑なタスクで失敗する理由

13に17を掛けるように求められた場合、答えがすぐに頭に浮かぶでしょうか？ほとんどの人にとって、おそらくそうではないでしょう。しかし、それは人間が2桁の掛け算ができないということを意味するわけではありません。数秒と紙とペンがあれば、13 × 17 = 130 + 70 + 21 = 221であることを計算するのはそれほど困難ではありません。

同様に、GPT-3に次のトークンを計算するのにかかる時間内で実行するには複雑すぎるタスクを与えると、間違った推測を作り上げる可能性があります。しかし、人間と同じように、それは必ずしもモデルがそのタスクを実行できないことを意味するわけではありません。物事を推論する時間と空間があれば、モデルは依然として信頼性を持って答えることができる可能性があります。

例として、`gpt-3.5-turbo-instruct`にジャグリングボールに関する以下の数学問題を尋ねると、間違って答えます：

```gpt-3.5-turbo-instruct
Q: A juggler has 16 balls. Half of the balls are golf balls and half of the golf balls are blue. How many blue golf balls are there?
A:
```

```gpt-3.5-turbo-instruct
There are 8 blue golf balls.
```

これはGPT-3が簡単な数学問題を解けないことを意味するのでしょうか？いいえ。実際、`Let's think step by step`でモデルにプロンプトを与えることで、モデルは問題を確実に解決します：

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

もちろん、単一の例だけでは、この`Let's think step by step`トリックが実際に一般的に機能するのか、それともこの特定の問題でたまたま運が良かっただけなのかを判断するのは困難です。しかし、これは本当に機能します。単語数学問題のベンチマークでは、`Let's think step by step`トリックがGPT-3の解決率を無価値な18%から適切な79%へと大幅に向上させました！

## モデルの能力はコンテキストに依存する

GPT-3を使って作業することを学ぶ際の一般的な概念的間違いは、その能力がすべてのコンテキストで固定されていると信じることです。例えば、GPT-3が簡単な論理問題を間違えた場合、それは簡単な論理ができないに違いないと考えることです。

しかし、`Let's think step by step`の例が示すように、GPT-3の見かけ上の失敗は、モデルが正しい出力に向かって自分自身を導くのに役立つより良いプロンプトで時々改善できます。

## 複雑なタスクでの信頼性を向上させる方法

この記事の残りの部分では、複雑なタスクにおける大規模言語モデルの信頼性を向上させるテクニックを共有します。これらのテクニックの一部は特定のタイプの問題に特化していますが、多くは幅広いタスクに適用できる一般的な原則に基づいて構築されています。例えば：

- より明確な指示を与える
- 複雑なタスクをより簡単なサブタスクに分割する
- モデルをタスクに集中させるために指示を構造化する
- 答える前に説明するようにモデルにプロンプトを与える
- 多くの可能な答えの正当化を求め、それらを統合する
- 多くの出力を生成し、その後モデルを使って最良のものを選ぶ
- パフォーマンスを最大化するためにカスタムモデルをファインチューニングする

## 複雑なタスクをより簡単なタスクに分割する

モデルに考える時間と空間をより多く与える一つの方法は、タスクをより簡単な部分に分解することです。

例として、テキスト（この場合はクルードのゲーム）について多肢選択問題をモデルに尋ねるタスクを考えてみましょう。直接尋ねられた場合、`gpt-3.5-turbo-instruct`は手がかり3と5を組み合わせることができず、間違って答えます：

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

手がかり3と5がマスタード大佐が天文台にいた唯一の人物であり、天文台にいた人物が燭台を持っていたことを確立しているにもかかわらず、モデルはそれらを組み合わせて正しい答え(a) Yesにすることができません。

しかし、直接答えを求める代わりに、タスクを3つの部分に分割できます：

- 最初に、手がかりを一つずつ確認し、その手がかりが潜在的に関連しているかどうかを検討する
- 次に、関連する手がかりを組み合わせて質問の答えを推論する
- 第三に、最終的な答えを書く：(a)、(b)、または(c)のいずれか

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

モデルにより多くの考える時間と空間を与え、推論計画に沿って導くことで、正しい答え(a) Yesを見つけることができます。

複雑な指示をより小さなサブタスクに分割することのもう一つの利点は、モデルが各サブタスクに集中し続けるのに役立つことです。

例えば、`gpt-3.5-turbo-instruct`にテキストを元の言語で要約するように求めると、モデルは英語に戻ってしまうことがあります：

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

しかし、最初にモデルにテキストの言語を特定してもらい、その後テキストを要約してもらうと、より信頼性が高くなります：

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

## 答える前に説明するようにモデルにプロンプトを与える

答えの信頼性を向上させるもう一つの強力なテクニックは、最終的な答えにすぐに飛び移るのではなく、答えを段階的に推論するようにモデルにプロンプトを与えることです。「声に出して考える」ことで、モデルは正しい答えに到達する可能性がはるかに高くなります。

### ゼロショット

#### 方法

[Takeshi Kojima et al.によって2022年に発表された](https://arxiv.org/abs/2205.11916)、モデルに答えを推論させる最も簡単な方法は、単純に答えの前に`Let's think step by step.`を付けることです。図2に例を示します：

[![ゼロショット推論の例](/images/zero-shot_reasoners_fig2.png)
<br>出典：Takeshi Kojima et al. (2022)による_Large Language Models are Zero-Shot Reasoners_](https://arxiv.org/abs/2205.11916)

#### 結果

MultiArith数学データセットにこの簡単なトリックを適用すると、著者らは`Let's think step by step`が精度を18%から79%へと4倍に向上させることを発見しました！

[![ゼロショット推論の例](/images/zero-shot_reasoners_tab5.png)
<br>出典：Takeshi Kojima et al. (2022)による_Large Language Models are Zero-Shot Reasoners_](https://arxiv.org/abs/2205.11916)

#### 含意

`Let's think step by step`トリックは数学問題では良く機能しますが、すべてのタスクで効果的ではありません。著者らは、これが多段階の算術問題、記号的推論問題、戦略問題、その他の推論問題で最も役立つことを発見しました。簡単な数学問題や常識問題には役立たず、おそらく他の多くの非推論タスクにも役立たないでしょう。

[![ゼロショット推論の例](/images/zero-shot_reasoners_tab1.png)
<br>出典：Takeshi Kojima et al. (2022)による_Large Language Models are Zero-Shot Reasoners_](https://arxiv.org/abs/2205.11916)

詳細については、[完全な論文](https://arxiv.org/abs/2205.11916)をお読みください。

このテクニックを自分のタスクに適用する場合は、指示をカスタマイズすることを恐れないでください。`Let's think step by step`はかなり一般的なので、あなたの使用例にカスタマイズされたより厳密な形式に従う指示でより良いパフォーマンスを見つけるかもしれません。例えば、`First, think step by step about why X might be true. Second, think step by step about why Y might be true. Third, think step by step about whether X or Y makes more sense.`のようなより構造化されたバリエーションを試すことができます。また、モデルが軌道を維持するのに役立つ例の形式を与えることもできます。例えば：

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

### 少数ショットの例

#### 方法

モデルに答えを推論させることは多くの方法で行うことができます。一つの方法は、[GoogleのJason WeiとDenny Zhou et al.](https://ai.googleblog.com/2022/05/language-models-perform-reasoning-via.html)によって研究されたように、いくつかの例（「少数ショット」）で実演することです。以下は少数ショットの思考連鎖プロンプトの例です：

[![思考連鎖の例](/images/chain_of_thought_fig1.png)
<br>出典：Jason Wei and Denny Zhou et al. (2022)による_Chain of Thought Prompting Elicits Reasoning in Large Language Models_](https://ai.googleblog.com/2022/05/language-models-perform-reasoning-via.html)

人間のラベラーによって書かれた推論連鎖のより多くの実演：

[![思考連鎖の例](/images/chain_of_thought_fig3.png)
<br>出典：Jason Wei and Denny Zhou et al. (2022)による_Chain of Thought Prompting Elicits Reasoning in Large Language Models_](https://ai.googleblog.com/2022/05/language-models-perform-reasoning-via.html)

[（梨が実際に浮くかどうかは疑問視されていることに注意）](https://twitter.com/Meaningness/status/1561062170074370048?s=20&t=mpHt8f3RRboztXxdhLFnWQ)

#### 結果

小学校の数学問題でテストした結果、著者らは思考連鎖プロンプティングが解決率を18%から57%へと3倍に向上させることを発見しました。

[![思考連鎖の例](/images/chain_of_thought_fig5.png)
<br>出典：Jason Wei and Denny Zhou et al. (2022)による_Chain of Thought Prompting Elicits Reasoning in Large Language Models_](https://ai.googleblog.com/2022/05/language-models-perform-reasoning-via.html)

数学問題に加えて、思考連鎖プロンプティングはスポーツ理解、コイン投げ追跡、最後の文字連結に関する質問でもパフォーマンスを向上させました。ほとんどの場合、パフォーマンスの向上を飽和させるのに多くの例は必要ありませんでした（8個程度以下）。

[![思考連鎖の例](/images/chain_of_thought_fig11.png)
<br>出典：Jason Wei and Denny Zhou et al. (2022)による_Chain of Thought Prompting Elicits Reasoning in Large Language Models_](https://ai.googleblog.com/2022/05/language-models-perform-reasoning-via.html)

詳細については、[完全な論文](https://arxiv.org/abs/2201.11903)をお読みください。

#### 含意

`Let's think step by step`テクニックと比較した少数ショット例ベースのアプローチの一つの利点は、最終的な答えに到達する前にモデルに実行してもらいたい推論の形式、長さ、スタイルをより簡単に指定できることです。これは、モデルが最初に正しい方法や深さで推論していない場合に特に役立ちます。

### ファインチューニング

#### 方法

一般的に、タスクで最大のパフォーマンスを引き出すには、カスタムモデルをファインチューニングする必要があります。しかし、説明を使ってモデルをファインチューニングするには、数千の例の説明が必要になる場合があり、これらを書くのは費用がかかります。

2022年に、Eric ZelikmanとYuhuai Wu et al.は、少数ショットプロンプトを使って説明のデータセットを生成し、それをモデルのファインチューニングに使用できる巧妙な手順を発表しました。アイデアは、少数ショットプロンプトを使って候補の説明を生成し、正しい答えを生成する説明のみを保持することです。次に、間違った答えのいくつかに対して追加の説明を得るために、正しい答えが質問の一部として与えられた少数ショットプロンプトを再試行します。著者らはこの手順をSTaR（Self-taught Reasoner）と呼びました：

[![STaR手順](/images/star_fig1.png)
<br>出典：Eric Zelikman and Yujuai Wu et al. (2022)による_STaR: Bootstrapping Reasoning With Reasoning_](https://arxiv.org/abs/2203.14465)

このテクニックにより、数千の例の説明を書く必要なしに、ファインチューニングの利点と思考連鎖プロンプティングの利点を組み合わせることができます。

#### 結果

著者らがこのテクニックをCommon Sense Q&Aデータセットに適用したところ、STaRは思考連鎖プロンプティング単体（73% > 37%）とファインチューニング単体（73% > 60%）の両方を上回ることを発見しました：

[![STaR結果](/images/star_tab1.png)
<br>出典：Eric Zelikman and Yujuai Wu et al. (2022)による_STaR: Bootstrapping Reasoning With Reasoning_](https://arxiv.org/abs/2203.14465)

詳細については、[完全な論文](https://arxiv.org/abs/2203.14465)をお読みください。

#### 含意

少数ショットプロンプトを使ってファインチューニングデータセットを拡張または修正するというアイデアは、説明の作成を超えて一般化できます。例えば、トレーニングしたい大量の非構造化テキストがある場合、プロンプトを使って非構造化テキストから構造化データセットを抽出し、その構造化データセットでカスタムモデルをファインチューニングする機会を見つけるかもしれません。

## 思考連鎖プロンプティングの拡張

思考連鎖プロンプティングの多くの拡張も発表されています。

### 選択-推論プロンプティング

#### 方法

Antonia Creswell et al.によって発表された、思考連鎖テクニックの一つの拡張は、説明と答えを生成する単一のプロンプトをより小さな部分に分割することです。最初に、プロンプトがテキストから関連する事実のサブセットを選択します（「選択プロンプト」）。次に、2番目のプロンプトが選択された事実から結論を推論します（「推論プロンプト」）。これらのプロンプトはループで交互に実行され、複数の推論ステップを生成し、最終的に最終的な答えに到達します。著者らは以下の図でアイデアを説明しています：

[![選択-推論プロンプティング](/images/selection-inference_fig1.png)
<br>出典：Antonia Creswell et al. (2022)による_Selection-Inference: Exploiting Large Language Models for Interpretable Logical Reasoning_](https://arxiv.org/abs/2205.09712)

#### 結果

7Bパラメータモデルに適用した場合、著者らは選択-推論プロンプティングがbAbiとProof Writerベンチマークタスク（どちらもより長い推論ステップのシーケンスを必要とする）で思考連鎖プロンプティングと比較して大幅にパフォーマンスを向上させることを発見しました。彼らが達成した最高のパフォーマンスは、選択-推論プロンプティングとファインチューニングの両方を組み合わせたものでした。

[![選択-推論プロンプティング](/images/selection-inference_fig4.png)
<br>出典：Antonia Creswell et al. (2022)による_Selection-Inference: Exploiting Large Language Models for Interpretable Logical Reasoning_](https://arxiv.org/abs/2205.09712)

#### 含意

これらのベンチマークでの向上は大きかったものの、これらのベンチマークはより長い推論シーケンスを必要とするために特別に選ばれました。多くのステップでの推論を必要としない問題では、向上はおそらくより小さいでしょう。

結果は、大規模言語モデルを扱う際のいくつかの一般的な教訓を強調しています。一つは、複雑なタスクをより小さなタスクに分割することは、信頼性とパフォーマンスを向上させる素晴らしい方法であるということです。タスクがより原子的であるほど、モデルがエラーを犯す余地が少なくなります。二つ目は、最大のパフォーマンスを得るには、しばしばファインチューニングを選択したアプローチと組み合わせることが必要だということです。

詳細については、[完全な論文](https://arxiv.org/abs/2205.09712)をお読みください。

### 忠実な推論アーキテクチャ

選択-推論プロンプティングテクニックを発表してから数ヶ月後、著者らはフォローアップ論文でテクニックを拡張し、以下のアイデアを提案しました：

- 選択-推論サイクルをいつ停止または継続すべきかを把握する
- 複数の推論パスを検索するのに役立つ価値関数を追加する
- 文自体を書き出すのではなく、文ラベル（例：sen1）について推論するようにモデルをファインチューニングすることで、偽の事実の幻覚を減らす

#### 方法

元の選択-推論テクニックでは、特化した「選択」と「推論」プロンプトが交互に実行され、事実を選択し、それらの事実から推論を行い、推論ステップのシーケンスを生成します。

著者らは、2つの追加コンポーネントでこのテクニックを拡張しました。

最初に、著者らは各推論ステップの後で、これまでの推論が質問に答えるのに十分かどうかを尋ねられる「停止」モデルを追加しました。十分であれば、モデルは最終的な答えを生成します。

停止モデルはいくつかの利点をもたらします：

- 選択-推論プロセスに停止または継続を指示できます
- プロセスが停止しない場合、答えが得られませんが、これはしばしば幻覚的な推測よりも好ましいです

[![忠実な推論](/images/faithful-reasoning_fig3.png)
<br>出典：Antonia Creswell et al. (2022)による_Faithful Reasoning Using Large Language Models_](https://arxiv.org/abs/2208.14271)

[![忠実な推論](/images/faithful-reasoning_fig5.png)
<br>出典：Antonia Creswell et al. (2022)による_Faithful Reasoning Using Large Language Models_](https://arxiv.org/abs/2208.14271)

次に、著者らは推論ステップの品質を評価し、複数の推論軌跡を検索するために使用される価値関数を追加しました。これは信頼性を高めるための共通のテーマを反映しています。モデルから単一の答えを生成するのではなく、答えのセットを生成し、何らかの価値関数/判別器/検証器モデルを使って最良のものを選ぶのです。

[![忠実な推論](/images/faithful-reasoning_fig7.png)
<br>出典：Antonia Creswell et al. (2022)による_Faithful Reasoning Using Large Language Models_](https://arxiv.org/abs/2208.14271)

これら2つの拡張に加えて、著者らは偽の事実の幻覚を減らすトリックも使用しました。モデルに事実の文を書き出すように求めるのではなく、代わりに文ラベル（例：sen1）で作業するようにモデルをファインチューニングしました。これにより、プロンプトコンテキストで言及されていない偽の事実をモデルが幻覚するのを防ぐのに役立ちます。

[![忠実な推論](/images/faithful-reasoning_fig4.png)
<br>出典：Antonia Creswell et al. (2022)による_Faithful Reasoning Using Large Language Models_](https://arxiv.org/abs/2208.14271)

#### 結果

著者らは、ProofWriterタスク（図示せず）と[EntailmentBankQA](https://allenai.org/data/entailmentbank)（図示）の2つのベンチマークでテクニックを評価しました。このテクニックは、特により困難な推論問題で精度を大幅に向上させました。

![忠実な推論](/images/faithful-reasoning_tab2.png)
<br>出典：Antonia Creswell et al. (2022)による_Faithful Reasoning Using Large Language Models_](https://arxiv.org/abs/2208.14271)

さらに、彼らの文ラベル操作トリックは幻覚を本質的に排除しました！

![忠実な推論](/images/faithful-reasoning_tab5.png)
<br>出典：Antonia Creswell et al. (2022)による_Faithful Reasoning Using Large Language Models_](https://arxiv.org/abs/2208.14271)

#### 含意

この論文は、大規模言語モデルの信頼性を向上させるための多くの有用な教訓を示しています：

- 複雑なタスクをより小さく、より信頼性の高いサブタスクに分割する
- 段階的に答えを生成し、途中で評価する
- 多くの可能な答えを生成し、別のモデルまたは関数を使って最良に見えるものを選ぶ
- モデルが言えることを制約することで幻覚を減らす（例：文の代わりに文ラベルを使用）
- 特化したタスクでモデルをファインチューニングすることでモデルのパフォーマンスを最大化する

詳細については、[完全な論文](https://arxiv.org/abs/2205.09712)をお読みください。

### 最小から最大へのプロンプティング

長い推論チェーンで不十分なパフォーマンス（選択-推論が輝く場面）に加えて、思考連鎖プロンプティングは例が短いがタスクが長い場合に特に苦労することがあります。

#### 方法

最小から最大へのプロンプティングは、推論タスクをより小さく、より信頼性の高いサブタスクに分割するもう一つのテクニックです。アイデアは、`To solve {question}, we need to first solve: "`のようなプロンプトでモデルからサブタスクを引き出すことです。そのサブタスクを手に入れたら、モデルは解決策を生成できます。解決策は元の質問に追加され、最終的な答えが生成されるまでプロセスが繰り返されます。

[![最小から最大へのプロンプティング](/images/least-to-most_fig1.png)
<br>出典：Denny Zhou et al. (2022)による_Least-to-most Prompting Enables Complex Reasoning in Large Language Models_](https://arxiv.org/abs/2205.10625)

#### 結果

`code-davinci-002`（コード用に最適化されているがテキストも理解できる）を使って長い推論チェーンを含むベンチマークに適用した場合、著者らは16% -> 99.7%という大きな向上を測定しました！

[
![最後の文字連結タスクでの最小から最大へのプロンプティング結果](/images/least-to-most_tab4.png)
![SCANでの最小から最大へのプロンプティング結果](/images/least-to-most_tab9.png)
![DROP数値推論での最小から最大へのプロンプティング結果](/images/least-to-most_tab11.png)
<br>出典：Denny Zhou et al. (2022)による_Least-to-most Prompting Enables Complex Reasoning in Large Language Models_](https://arxiv.org/abs/2205.10625)

#### 含意

上記の最小から最大へのプロンプティングからの向上は印象的ですが、これらは長い推論チェーンを必要とする非常に狭いタスクセットで測定されています。

それでも、これらは共通のテーマを示しています：(a) 複雑なタスクをより小さなサブタスクに分解し、(b) モデルに答えを考え出すためのより多くの時間と空間を与えることで信頼性を向上させる。

詳細については、[完全な論文](https://arxiv.org/abs/2205.10625)をお読みください。

## 関連アイデア

### 産婆術プロンプティング

#### 方法

正しい答えの可能性を最大化しようとする前のテクニックとは対照的に、もう一つのアプローチは、GPT-3を使って可能な説明の木（正しい_および間違った_両方）を生成し、それらの関係を分析してどのセットが正しいかを推測することです。このテクニックは、[2022年5月にJaehun Jung et al.](https://arxiv.org/abs/2205.11822)によって産婆術プロンプティングと名付けられました（産婆術は質問をして考えを引き出すソクラテス式方法に関連します）。

この方法は複雑で、以下のように動作します：

- 最初に、各ノードが真または偽である可能性のある文である産婆術の木を構築します：
  - 多肢選択問題または真偽文から始めます（例：`War cannot have a tie`）
  - 質問への各可能な答えについて、モデルを使って対応する説明を生成します（`War cannot have a tie? True, because`のようなプロンプトで）
  - 次に、質問と生成された説明でモデルにプロンプトを与え、答えを生成するように求めます。説明を逆転させる（`It is wrong to say that {explanation}`のような接頭辞で）ことで答えが逆転する場合、その説明は「論理的に不可欠」と見なされます。
  - 説明が論理的に不可欠でない場合、上記のプロセスを再帰的に繰り返し、各説明を真偽問題に変換し、各新しい質問に対してより多くの説明を生成します。
  - すべての再帰的説明が完了した後、説明の木が得られ、木の各葉は説明を逆転させると モデルの答えが逆転するという性質を持ちます。
- 次に、木を関係のグラフに変換します：
  - 木の各ノードについて、各ノードに対するモデルの相対的信念を計算します（説明が与えられた場合に`True`の答えを得る確率から推測）
  - 木の各ノードペアについて、モデルを使ってそれらが含意（暗示）されているか矛盾しているかを特定します
- 第三に、最も一貫した信念のセットを見つけ、それらを真実として取ります：
  - 具体的には、各ノードの信念の強さとそれらの間の論理的関係を使って、問題を重み付き最大充足可能性問題（MAX-SAT）として定式化します
  - ソルバーを使って最も自己一貫した信念のセットを見つけ、それらを真実として取ります

[
![産婆術プロンプティング](/images/maieutic_fig2.png)
![産婆術プロンプティング](/images/maieutic_fig6.png)
<br>出典：Jaehun Jung et al. (2022)による_Maieutic Prompting: Logically Consistent Reasoning with Recursive Explanations_](https://arxiv.org/abs/2205.11822)

#### 結果

[![産婆術プロンプティング結果](/images/maieutic_tab1.png)
<br>出典：Jaehun Jung et al. (2022)による_Maieutic Prompting: Logically Consistent Reasoning with Recursive Explanations_](https://arxiv.org/abs/2205.11822)

#### 含意

複雑さを超えて、この方法の一つの制限は、多肢選択として提起できる質問にのみ適用されるように見えることです。

詳細については、[完全な論文](https://arxiv.org/abs/2205.11822)をお読みください。

## 拡張

### 自己一貫性

#### 方法

答えの離散的なセットを持つタスクの場合、信頼性を向上させる一つの簡単な方法は、モデルから複数の説明と答えをサンプリングし（正の温度を使用）、最も頻繁に現れる最終的な答えを選ぶことです。

[![自己一貫性方法](/images/self-consistency_fig1.png)
<br>出典：Xuezhi Wang et al. (2022)による_Self-Consistency Improves Chain of Thought Reasoning in Language Models_](https://arxiv.org/abs/2203.11171)

#### 結果

このテクニックは、数学と推論ベンチマークのスイートで精度を1から24パーセントポイント向上させました。（以下にプロットされているのはGoogleのLaMDAモデルからの結果です。Googleのより大きなPaLMモデルを使用した場合、ベースラインはより高かったが、向上はやや小さかった。）

[![自己一貫性結果](/images/self-consistency_fig3.png)
<br>出典：Xuezhi Wang et al. (2022)による_Self-Consistency Improves Chain of Thought Reasoning in Language Models_](https://arxiv.org/abs/2203.11171)

#### 含意

このテクニックは実装が簡単ですが、費用がかかる可能性があります。10個の答えのセットを生成すると、コストが10倍になります。

また、これらのテクニックの多くと同様に、限られた答えのセットを持つタスクにのみ適用されます。各答えがユニークなオープンエンドタスク（詩を書くなど）の場合、最も一般的な答えを選ぶことが何を意味するかは明らかではありません。

最後に、このテクニックは答えに到達する複数のパスや表現がある場合に最も有益であるはずです。パスが一つしかない場合、テクニックはまったく役立たない可能性があります。極端な例：タスクが単一のトークン答えを生成することだった場合、100回の生成から最も一般的なトークンを取ることは、最も高いlogprobsを持つトークンを取ること（temperature=0で単一の生成で得られる）と変わらないでしょう。

### 検証器

タスクのパフォーマンスを向上させるもう一つの重要なテクニックは、メインの生成モデルの出力を評価するために検証器または判別器モデルを訓練することです。判別器が出力を拒否した場合、受け入れ可能な出力が得られるまで生成モデルを再サンプリングできます。多くの場合、答えを作成するよりも答えを判断する方が簡単であり、これがこの方法の力を説明するのに役立ちます。

#### 方法

2021年に、OpenAIの研究者たちは以下の手順を使って小学校の数学問題にこのテクニックを適用しました：

- 最初に、質問と解答でモデルをファインチューニングしました
- 訓練セットの各問題について、100個の解答を生成しました
- それらの100個の解答のそれぞれは、最終的な答えが正しいかどうかに基づいて、正しいまたは間違いとして自動的にラベル付けされました
- 一部が正しく、一部が間違いとしてラベル付けされたそれらの解答を使って、質問と候補解答が正しいか間違いかを分類する検証器モデルをファインチューニングしました
- 最後に、テスト時に、生成モデルは各問題に対して100個の解答を作成し、検証器モデルによる最高スコアを持つものが最終的な答えとして選ばれます

[![検証器方法](/images/verifiers_fig3.png)
<br>出典：Karl Cobbe et al. (2021)による_Training Verifiers to Solve Math Word Problems_](https://arxiv.org/abs/2110.14168)

#### 結果

175B GPT-3モデルと8,000の訓練例で、このテクニックは小学校数学の精度を約33%から約55%へと大幅に向上させました。

[![検証器結果](/images/verifiers_fig5.png)
<br>出典：Karl Cobbe et al. (2021)による_Training Verifiers to Solve Math Word Problems_](https://arxiv.org/abs/2110.14168)

#### 含意

自己一貫性テクニックと同様に、この方法は高価になる可能性があります。タスクごとに100個の解答を生成することは、コストを約100倍増加させるからです。

## 信頼性の理論

上記のテクニックはアプローチが異なりますが、すべて複雑なタスクでの信頼性を向上させるという目標を共有しています。主に以下の方法でこれを行います：

- 信頼性の低い操作をより小さく、より信頼性の高い操作に分解する（例：選択-推論プロンプティング）
- システムの信頼性を個々のコンポーネントよりも高くするために複数のステップまたは複数の関係を使用する（例：産婆術プロンプティング）

### 確率的グラフィカルモデル

信頼性の低いコンポーネントから信頼性の高いシステムを構築しようとするこのパラダイムは、確率的プログラミングを思い起こさせ、その分野の多くの分析テクニックをこの分野に適用できます。

論文_Language Model Cascades_で、David Dohan et al.は上記のテクニックを確率的グラフィカルモデルのパラダイムで解釈しています：

#### 思考連鎖プロンプティング

[![思考連鎖プロンプティングのグラフィカルモデル](/images/lm_cascades_fig1.png)
<br>出典：David Dohan et al. (2022)による_Language Model Cascades_](https://arxiv.org/abs/2207.10342)

#### ファインチューニングされた思考連鎖プロンプティング / 自己教示推論器

[![ファインチューニングされた思考連鎖プロンプティングのグラフィカルモデル](/images/lm_cascades_fig3.png)
<br>出典：David Dohan et al. (2022)による_Language Model Cascades_](https://arxiv.org/abs/2207.10342)

#### 選択-推論プロンプティング

[![選択-推論プロンプティングのグラフィカルモデル](/images/lm_cascades_fig4.png)
<br>出典：David Dohan et al. (2022)による_Language Model Cascades_](https://arxiv.org/abs/2207.10342)

#### 検証器

[![検証器のグラフィカルモデル](/images/lm_cascades_fig5.png)
<br>出典：David Dohan et al. (2022)による_Language Model Cascades_](https://arxiv.org/abs/2207.10342)

#### 含意

これらのテクニックを確率的グラフィカルモデルとして定式化することは、特定の問題を解決するのにすぐに有用ではないかもしれませんが、フレームワークは新しいテクニックの選択、組み合わせ、発見に役立つ可能性があります。

## 最後の考察

大規模言語モデルの研究は非常に活発で、急速に進化しています。研究者たちはモデルを改善し続けるだけでなく、モデルを最適に活用する方法についての理解も改善し続けています。これらの発展のペースを強調するために、上記で共有されたすべての論文が過去12ヶ月以内に発表されたことに注意してください（2022年9月に執筆時点）。

将来的には、より良いモデルとより良いテクニックが発表されることが期待されます。ここでの特定のテクニックが将来のベストプラクティスに取って代わられたとしても、それらの背後にある一般的な原則は、おそらく専門ユーザーのツールキットの重要な部分であり続けるでしょう。

## 参考文献

| 教訓                                                                                                                         | 論文                                                                                                                                     | 日付     |
| ------------------------------------------------------------------------------------------------------------------------------ | ----------------------------------------------------------------------------------------------------------------------------------------- | -------- |
| 複雑なタスクをより簡単なサブタスクに分解する（中間出力をユーザーに公開することを検討する）                            | [AI Chains: Transparent and Controllable Human-AI Interaction by Chaining Large Language Model Prompts](https://arxiv.org/abs/2110.01691) | 2021年10月 |
| 多くの候補を生成し、最も良く見えるものを選ぶことで出力を改善できる                                 | [Training Verifiers to Solve Math Word Problems](https://arxiv.org/abs/2110.14168)                                                        | 2021年10月 |
| 推論タスクでは、答える前に段階的に推論するとモデルの性能が向上する                                            | [Chain of Thought Prompting Elicits Reasoning in Large Language Models](https://arxiv.org/abs/2201.11903)                                 | 2022年1月 |
| 多くの説明-答え出力を生成し、最も人気のある答えを選ぶことで段階的推論を改善できる      | [Self-Consistency Improves Chain of Thought Reasoning in Language Models](https://arxiv.org/abs/2203.11171)                               | 2022年3月 |
| 段階的推論器をファインチューニングしたい場合、多肢選択問題と答えのデータだけで実行できる              | [STaR: Bootstrapping Reasoning With Reasoning](https://arxiv.org/abs/2203.14465)                                                          | 2022年3月 |
| 段階的推論方法はゼロ例でも素晴らしく機能する                                                          | [Large Language Models are Zero-Shot Reasoners](https://arxiv.org/abs/2205.11916)                                                         | 2022年5月 |
| 「選択」プロンプトと「推論」プロンプトを交互に使うことで段階的推論よりも良い結果を得られる                    | [Selection-Inference: Exploiting Large Language Models for Interpretable Logical Reasoning](https://arxiv.org/abs/2205.09712)             | 2022年5月 |
| 長い推論問題では、問題を段階的に解決する部分に分割することで段階的推論を改善できる | [Least-to-most Prompting Enables Complex Reasoning in Large Language Models](https://arxiv.org/abs/2205.10625)                            | 2022年5月 |
| モデルに良い説明と偽の説明の両方を分析させ、どの説明のセットが最も一貫しているかを把握させることができる    | [Maieutic Prompting: Logically Consistent Reasoning with Recursive Explanations](https://arxiv.org/abs/2205.11822)                        | 2022年5月 |
| これらのテクニックを、システムが信頼性の低いコンポーネントから構成される確率的プログラミングの観点で考えることができる       | [Language Model Cascades](https://arxiv.org/abs/2207.10342)                                                                               | 2022年7月 |
| 文ラベル操作で幻覚を排除でき、「停止」プロンプトで間違った答えを減らすことができる      | [Faithful Reasoning Using Large Language Models](https://arxiv.org/abs/2208.14271)                                                        | 2022年8月 |