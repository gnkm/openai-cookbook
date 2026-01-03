# テキスト比較の例

[OpenAI API embeddings エンドポイント](https://beta.openai.com/docs/guides/embeddings)は、テキストの断片間の関連性や類似性を測定するために使用できます。

GPT-3 のテキスト理解を活用することで、これらの埋め込みは、教師なし学習と転移学習の設定において、ベンチマークで[最先端の結果を達成しました](https://arxiv.org/abs/2201.10005)。

埋め込みは、セマンティック検索、レコメンデーション、クラスター分析、ほぼ重複検出などに使用できます。

詳細については、OpenAI のブログ投稿のアナウンスをお読みください：

- [Introducing Text and Code Embeddings (Jan 2022)](https://openai.com/blog/introducing-text-and-code-embeddings/)
- [New and Improved Embedding Model (Dec 2022)](https://openai.com/blog/new-and-improved-embedding-model/)

他の埋め込みモデルとの比較については、[Massive Text Embedding Benchmark (MTEB) Leaderboard](https://huggingface.co/spaces/mteb/leaderboard) を参照してください。

## セマンティック検索

埋め込みは、単独で、またはより大きなシステムの機能として検索に使用できます。

検索に埋め込みを使用する最も簡単な方法は次のとおりです：

- 検索前（事前計算）：
  - テキストコーパスをトークン制限（`text-embedding-3-small` の場合は8,191トークン）より小さいチャンクに分割する
  - 各テキストチャンクを埋め込む
  - それらの埋め込みを自分のデータベースまたは [Pinecone](https://www.pinecone.io)、[Weaviate](https://weaviate.io)、[Qdrant](https://qdrant.tech) などのベクトル検索プロバイダーに保存する
- 検索時（ライブ計算）：
  - 検索クエリを埋め込む
  - データベース内で最も近い埋め込みを見つける
  - 上位の結果を返す

検索に埋め込みを使用する方法の例は、[Semantic_text_search_using_embeddings.ipynb](../examples/Semantic_text_search_using_embeddings.ipynb) に示されています。

より高度な検索システムでは、埋め込みのコサイン類似度を、検索結果をランク付けする際の多くの機能の1つとして使用できます。

## 質問応答

GPT-3 から確実に正直な答えを得る最良の方法は、正しい答えを見つけることができるソースドキュメントを提供することです。上記のセマンティック検索手順を使用すると、ドキュメントのコーパスを安価に検索して関連情報を見つけ、その情報をプロンプトを介して GPT-3 に提供して質問に答えることができます。これを [Question_answering_using_embeddings.ipynb](../examples/Question_answering_using_embeddings.ipynb) で実証しています。

## レコメンデーション

レコメンデーションは検索と非常に似ていますが、自由形式のテキストクエリの代わりに、入力がセット内のアイテムである点が異なります。

レコメンデーションに埋め込みを使用する方法の例は、[Recommendation_using_embeddings.ipynb](../examples/Recommendation_using_embeddings.ipynb) に示されています。

検索と同様に、これらのコサイン類似度スコアは、単独でアイテムをランク付けするために使用することも、より大きなランキングアルゴリズムの機能として使用することもできます。

## 埋め込みのカスタマイズ

OpenAI の埋め込みモデルの重みはファインチューニングできませんが、それでも訓練データを使用してアプリケーションに埋め込みをカスタマイズできます。

[Customizing_embeddings.ipynb](../examples/Customizing_embeddings.ipynb) では、訓練データを使用して埋め込みをカスタマイズする例の方法を提供しています。この方法のアイデアは、埋め込みベクトルに乗算するカスタム行列を訓練して、新しいカスタマイズされた埋め込みを取得することです。優れた訓練データがあれば、このカスタム行列は訓練ラベルに関連する機能を強調するのに役立ちます。行列乗算を（a）埋め込みの変更、または（b）埋め込み間の距離を測定するために使用される距離関数の変更として同等に考えることができます。

