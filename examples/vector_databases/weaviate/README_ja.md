# Weaviate <> OpenAI

[​Weaviate](https://weaviate.io)は、OpenAIエンベディング_と_データオブジェクトを保存・検索できるオープンソースのベクトル検索エンジンです（[ドキュメント](https://weaviate.io/developers/weaviate) - [Github](https://github.com/weaviate/weaviate)）。このデータベースでは、類似性検索、ハイブリッド検索（キーワードベースとベクトル検索などの複数の検索技術の組み合わせ）、生成検索（Q&Aなど）を実行できます。Weaviateは、様々なOpenAIベースのモジュール（例：[`text2vec-openai`](https://weaviate.io/developers/weaviate/modules/retriever-vectorizer-modules/text2vec-openai)、[`qna-openai`](https://weaviate.io/developers/weaviate/modules/reader-generator-modules/qna-openai)）もサポートしており、データを高速かつ効率的にベクトル化・クエリできます。

Weaviate（必要に応じてOpenAIモジュールも含む）は3つの方法で実行できます：

1. Dockerコンテナ内でのオープンソース（[例](./docker-compose.yml)）
2. Weaviate Cloud Serviceの使用（[始め方](https://weaviate.io/developers/weaviate/quickstart/installation#weaviate-cloud-service)）
3. Kubernetesクラスター内（[詳細](https://weaviate.io/developers/weaviate/installation/kubernetes)）

### 例

このフォルダには、WeaviateとOpenAIの様々な例が含まれています。

| 名前 | 説明 | 言語 | Google Colab |
| --- | --- | --- | --- |
| [WeaviateとOpenAIの入門](./getting-started-with-weaviate-and-openai.ipynb) | WeaviateのOpenAIベクトル化モジュール（`text2vec-openai`）を使用した*セマンティックベクトル検索*のシンプルな入門 | Python Notebook | [リンク](https://colab.research.google.com/drive/1RxpDE_ruCnoBB3TfwAZqdjYgHJhtdwhK) |
| [WeaviateとOpenAIによるハイブリッド検索](./hybrid-search-with-weaviate-and-openai.ipynb) | WeaviateのOpenAIベクトル化モジュール（`text2vec-openai`）を使用した*ハイブリッド検索*のシンプルな入門 | Python Notebook | [リンク](https://colab.research.google.com/drive/1E75BALWoKrOjvUhaznJKQO0A-B1QUPZ4) |
| [WeaviateとOpenAIによる質問応答](./question-answering-with-weaviate-and-openai.ipynb) | WeaviateのOpenAI Q&Aモジュール（`qna-openai`）を使用した*質問応答（Q&A）*のシンプルな入門 | Python Notebook | [リンク](https://colab.research.google.com/drive/1pUerUZrJaknEboDxDxsuf3giCK0MJJgm) |
| [Docker-composeの例](./docker-compose.yml) | すべてのOpenAIモジュールが有効化されたDocker-composeファイル | Docker |