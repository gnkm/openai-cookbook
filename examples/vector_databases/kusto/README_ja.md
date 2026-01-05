# Kustoをベクターデータベースとして使用する



[Azure Data Explorer（別名Kusto）](https://azure.microsoft.com/en-us/products/data-explorer)は、ユーザーが大規模なデータセットに対してリアルタイムで高度な分析を実行できるクラウドベースのデータ分析サービスです。大量のデータの処理に特に適しており、ベクターの保存と検索に優れた選択肢となります。

Kustoは、配列やプロパティバッグなどの非構造化データを格納できるdynamicという特別なデータ型をサポートしています。[Dynamic データ型](https://learn.microsoft.com/en-us/azure/data-explorer/kusto/query/scalar-data-types/dynamic)は、ベクター値の保存に最適です。さらに、元のオブジェクトに関連するメタデータをテーブルの別の列として保存することで、ベクター値を拡張できます。  
Kustoは、ベクター類似度検索を実行するための組み込み関数[series_cosine_similarity_fl](https://learn.microsoft.com/en-us/azure/data-explorer/kusto/functions-library/series-cosine-similarity-fl)もサポートしています。

Kustoを無料で[始める](https://aka.ms/kustofree)ことができます。

![Kusto_Vector](./images/kusto_vector_db.png)



## KustoとOpen AI埋め込みの開始方法

### デモシナリオ

![Wiki_embeddings](./images/wiki_embeddings.png)

![semantic_search_flow](./images/semantic_search_user_flow.png)

このデモを試したい場合は、[Notebook](Getting_started_with_kusto_and_openai_embeddings.ipynb)の手順に従ってください。

これにより以下のことが可能になります：

1. OpenAI APIによって作成された事前計算済み埋め込みを使用する。

2. 埋め込みをKustoに保存する。

3. OpenAI APIを使用して生のテキストクエリを埋め込みに変換する。

4. Kustoを使用して保存された埋め込みでコサイン類似度検索を実行する。