# Astra DBとCassandraを使用したRAG

このディレクトリのデモは、Apache Cassandra®上に構築されたサーバーレスのDatabase-as-a-Serviceである**DataStax Astra DB**で現在利用可能なVector Search機能の使用方法を示しています。

これらのサンプルノートブックは、異なるライブラリとAPIを使用して同じGenAI標準のRAGワークロードの実装を実演しています。

HTTP APIインターフェースで[Astra DB](https://docs.datastax.com/en/astra/home/astra.html)を使用するには、「AstraPy」ノートブック（`astrapy`はデータベースとやり取りするためのPythonクライアントです）をご覧ください。

データベースへのCQLアクセスを希望する場合（[Astra DB](https://docs.datastax.com/en/astra-serverless/docs/vector-search/overview.html)または[ベクトル検索をサポートする](https://cassandra.apache.org/doc/trunk/cassandra/vector-search/overview.html)Cassandraクラスターのいずれか）、「CQL」または「CassIO」ノートブックをチェックしてください。これらは作業する抽象化レベルが異なります。

Astra DBとそのVector Search機能について詳しく知りたい場合は、[datastax.com](https://docs.datastax.com/en/astra/home/astra.html)をご覧ください。

### サンプルノートブック

以下の例は、OpenAIとDataStax Astra DBがベクトルベースのAIアプリケーションを強化するためにいかに簡単に連携できるかを示しています。ローカルのJupyterエンジンまたはColabノートブックとして実行できます：

| ユースケース | 対象データベース | フレームワーク | ノートブック | Google Colab |
| -------- | --------------- | --------- | -------- | ------------ |
| 名言の検索/生成 | Astra DB | AstraPy | [Notebook](./Philosophical_Quotes_AstraPy.ipynb) | [![Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/openai/openai-cookbook/blob/main/examples/vector_databases/cassandra_astradb/Philosophical_Quotes_AstraPy.ipynb) |
| 名言の検索/生成 | CQLを通じたCassandra / Astra DB | CassIO | [Notebook](./Philosophical_Quotes_cassIO.ipynb) | [![Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/openai/openai-cookbook/blob/main/examples/vector_databases/cassandra_astradb/Philosophical_Quotes_cassIO.ipynb) |
| 名言の検索/生成 | CQLを通じたCassandra / Astra DB | プレーンCassandra言語 | [Notebook](./Philosophical_Quotes_CQL.ipynb) | [![Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/openai/openai-cookbook/blob/main/examples/vector_databases/cassandra_astradb/Philosophical_Quotes_CQL.ipynb) |

### ベクトル類似性の視覚的表現

![3_vector_space](https://user-images.githubusercontent.com/14221764/262321363-c8c625c1-8be9-450e-8c68-b1ed518f990d.png)