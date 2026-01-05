# Elasticsearch

Elasticsearchは人気の検索・分析エンジンであり、[ベクトルデータベース](https://www.elastic.co/elasticsearch/vector-database)です。
Elasticsearchは、大規模なベクトル埋め込みの作成、保存、検索を効率的に行う方法を提供します。

技術的な詳細については、[Elasticsearchドキュメント](https://www.elastic.co/guide/en/elasticsearch/reference/current/knn-search.html)を参照してください。

[`elasticsearch-labs`](https://github.com/elastic/elasticsearch-labs)リポジトリには、Elasticプラットフォームをテストするための実行可能なPythonノートブック、サンプルアプリ、リソースが含まれています。

## OpenAI cookbookノートブック 📒

Elasticsearchをベクトルデータベースとして使用し、OpenAIと連携するためのノートブックをこのリポジトリでご確認ください。

### [セマンティック検索](https://github.com/openai/openai-cookbook/blob/main/examples/vector_databases/elasticsearch/elasticsearch-semantic-search.ipynb)

このノートブックでは以下の方法を学習できます：

 - OpenAI WikipediaエンベディングデータセットをElasticsearchにインデックス化する
 - `openai ada-02`モデルで質問をエンコードする
 - セマンティック検索を実行する

<hr>


### [検索拡張生成](https://github.com/openai/openai-cookbook/blob/main/examples/vector_databases/elasticsearch/elasticsearch-retrieval-augmented-generation.ipynb)

このノートブックは、セマンティック検索ノートブックを基に以下の機能を追加しています：

- セマンティック検索から最上位の結果を選択する
- その結果をOpenAI [Chat Completions](https://platform.openai.com/docs/guides/gpt/chat-completions-api) APIエンドポイントに送信して検索拡張生成（RAG）を実行する