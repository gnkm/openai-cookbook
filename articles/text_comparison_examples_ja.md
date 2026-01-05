# テキスト比較の例

[OpenAI API embeddings エンドポイント](https://beta.openai.com/docs/guides/embeddings)は、テキストの関連性や類似性を測定するために使用できます。

GPT-3のテキスト理解を活用することで、これらのembeddingsは教師なし学習と転移学習の設定において、ベンチマークで[最先端の結果を達成](https://arxiv.org/abs/2201.10005)しました。

Embeddingsは、セマンティック検索、レコメンデーション、クラスター分析、重複検出などに使用できます。

詳細については、OpenAIのブログ投稿をご覧ください：

- [Introducing Text and Code Embeddings (Jan 2022)](https://openai.com/blog/introducing-text-and-code-embeddings/)
- [New and Improved Embedding Model (Dec 2022)](https://openai.com/blog/new-and-improved-embedding-model/)

他のembeddingモデルとの比較については、[Massive Text Embedding Benchmark (MTEB) Leaderboard](https://huggingface.co/spaces/mteb/leaderboard)をご覧ください。

## セマンティック検索

Embeddingsは、単独で検索に使用することも、より大きなシステムの機能として使用することもできます。

検索にembeddingsを使用する最もシンプルな方法は以下の通りです：

- 検索前（事前計算）：
  - テキストコーパスをトークン制限より小さなチャンクに分割する（`text-embedding-3-small`の場合は8,191トークン）
  - 各テキストチャンクをembedする
  - それらのembeddingsを独自のデータベースまたは[Pinecone](https://www.pinecone.io)、[Weaviate](https://weaviate.io)、[Qdrant](https://qdrant.tech)などのベクトル検索プロバイダーに保存する
- 検索時（リアルタイム計算）：
  - 検索クエリをembedする
  - データベース内で最も近いembeddingsを見つける
  - 上位の結果を返す

検索にembeddingsを使用する方法の例は、[Semantic_text_search_using_embeddings.ipynb](../examples/Semantic_text_search_using_embeddings.ipynb)で示されています。

より高度な検索システムでは、embeddingsのコサイン類似度を検索結果のランキングにおける多くの特徴の一つとして使用できます。

## 質問応答

GPT-3から信頼性の高い正直な回答を得る最良の方法は、正しい答えを見つけることができるソース文書を提供することです。上記のセマンティック検索手順を使用して、関連情報について文書のコーパスを安価に検索し、その情報をプロンプト経由でGPT-3に提供して質問に答えることができます。これを[Question_answering_using_embeddings.ipynb](../examples/Question_answering_using_embeddings.ipynb)で実演しています。

## レコメンデーション

レコメンデーションは検索と非常に似ていますが、自由形式のテキストクエリの代わりに、入力がセット内のアイテムである点が異なります。

レコメンデーションにembeddingsを使用する方法の例は、[Recommendation_using_embeddings.ipynb](../examples/Recommendation_using_embeddings.ipynb)で示されています。

検索と同様に、これらのコサイン類似度スコアは、アイテムのランキングに単独で使用することも、より大きなランキングアルゴリズムの特徴として使用することもできます。

## Embeddingsのカスタマイズ

OpenAIのembeddingモデルの重みはファインチューニングできませんが、それでも訓練データを使用してアプリケーションに合わせてembeddingsをカスタマイズできます。

[Customizing_embeddings.ipynb](../examples/Customizing_embeddings.ipynb)では、訓練データを使用してembeddingsをカスタマイズする例示的な方法を提供しています。この方法のアイデアは、新しいカスタマイズされたembeddingsを得るために、embeddingベクトルに掛け合わせるカスタム行列を訓練することです。良い訓練データがあれば、このカスタム行列は訓練ラベルに関連する特徴を強調するのに役立ちます。行列の乗算を、(a) embeddingsの修正、または (b) embeddings間の距離を測定するために使用される距離関数の修正として同等に考えることができます。