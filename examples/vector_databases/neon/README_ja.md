# Neonとは？

[Neon](https://neon.tech/)は、クラウド向けに構築されたサーバーレスPostgresです。Neonはコンピュートとストレージを分離し、オートスケーリング、データベースブランチング、ゼロスケール機能など、モダンな開発者向け機能を提供します。

## ベクトル検索

Neonは、[pgvector](https://neon.tech/docs/extensions/pgvector)オープンソースPostgreSQL拡張機能を使用したベクトル検索をサポートしており、Postgresを埋め込みベクトルの保存とクエリのためのベクトルデータベースとして利用できます。

## OpenAI cookbookノートブック

ベクトルデータベースとしてNeon Serverless Postgresを使用するためのノートブックをこのリポジトリで確認してください。

### pgvectorとOpenAIを使用したNeon Postgresでのセマンティック検索

このノートブックでは以下の方法を学習します：

1. OpenAI APIで作成された埋め込みベクトルの使用
2. Neon Serverless Postgresデータベースでの埋め込みベクトルの保存
3. OpenAI APIを使用した生テキストクエリの埋め込みベクトルへの変換
4. `pgvector`拡張機能を使用したNeonでのベクトル類似度検索の実行

## スケーリングサポート

Neonは以下の機能でAIアプリケーションのスケーリングを可能にします：

- [オートスケーリング](https://neon.tech/docs/introduction/read-replicas)：AIアプリケーションが一日の特定の時間帯や異なるタイミングで高負荷を経験する場合、Neonは手動介入なしに自動的にコンピュートリソースをスケールできます。非アクティブ期間中は、Neonはゼロまでスケールダウンできます。
- [インスタント読み取りレプリカ](https://neon.tech/docs/introduction/read-replicas)：Neonはインスタント読み取りレプリカをサポートしており、これは読み書きコンピュートと同じデータに対して読み取り操作を実行するよう設計された独立した読み取り専用コンピュートインスタンスです。読み取りレプリカを使用することで、AIアプリケーション用の専用読み取り専用コンピュートインスタンスに読み書きコンピュートインスタンスからの読み取りをオフロードできます。
- [Neonサーバーレスドライバー](https://neon.tech/docs/serverless/serverless-driver)：Neonは、サーバーレスおよびエッジ環境からデータをクエリできるJavaScriptおよびTypeScriptアプリケーション向けの低レイテンシサーバーレスPostgreSQLドライバーをサポートしており、10ms未満のクエリを実現できます。

## その他の例

- [AI駆動のセマンティック検索アプリケーションの構築](https://github.com/neondatabase/yc-idea-matcher) - スタートアップのアイデアを送信し、YCombinatorが以前に投資した類似のアイデアのリストを取得
- [AI駆動のチャットボットの構築](https://github.com/neondatabase/ask-neon) - Postgresをベクトルデータベースとして使用するPostgres Q&Aチャットボット
- [Vercel Postgres pgvectorスターター](https://vercel.com/templates/next.js/postgres-pgvector) - Vercel Postgres（Neonによって提供）を使用したベクトル類似度検索

## 追加リソース

- [Neonを使用したAIアプリケーションの構築](https://neon.tech/ai)
- [Neon AI & 埋め込みベクトルドキュメント](https://neon.tech/docs/ai/ai-intro)
- [Vercel、OpenAI、Postgresを使用したAI駆動チャットボットの構築](neon.tech/blog/building-an-ai-powered-chatbot-using-vercel-openai-and-postgres)
- [WebベースのAI SQLプレイグラウンドとブラウザからのPostgres接続](https://neon.tech/blog/postgres-ai-playground)
- [pgvector GitHubリポジトリ](https://github.com/pgvector/pgvector)