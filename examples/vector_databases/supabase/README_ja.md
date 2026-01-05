# Supabase Vector Database

[Supabase](https://supabase.com/docs)は、本格的なSQLデータベースである[Postgres](https://en.wikipedia.org/wiki/PostgreSQL)の上に構築されたオープンソースのFirebase代替サービスです。

[Supabase Vector](https://supabase.com/docs/guides/ai)は、[pgvector](https://github.com/pgvector/pgvector)上に構築されたベクターツールキットです。pgvectorは、アプリケーションの他のデータを保持するのと同じデータベース内に埋め込みを保存できるPostgres拡張機能です。pgvectorのインデックスアルゴリズムと組み合わせることで、ベクター検索は[大規模でも高速](https://supabase.com/blog/increase-performance-pgvector-hnsw)を維持します。

Supabaseは、アプリ開発を可能な限り迅速にするため、Postgresの上にサービスとツールのエコシステムを追加しています。これには以下が含まれます：

- [自動生成REST API](https://supabase.com/docs/guides/api)
- [自動生成GraphQL API](https://supabase.com/docs/guides/graphql)
- [リアルタイムAPI](https://supabase.com/docs/guides/realtime)
- [認証](https://supabase.com/docs/guides/auth)
- [ファイルストレージ](https://supabase.com/docs/guides/storage)
- [エッジ関数](https://supabase.com/docs/guides/functions)

これらのサービスをpgvectorと組み合わせて使用することで、Postgres内で埋め込みを保存し、クエリを実行できます。

## OpenAI Cookbook Examples

以下は、OpenAI埋め込みモデルをSupabase Vectorと組み合わせて使用する方法を説明するガイドとリソースです。

| ガイド                                    | 説明                                                |
| ---------------------------------------- | -------------------------------------------------- |
| [セマンティック検索](./semantic-search.mdx) | pgvectorを使用して大規模な埋め込みの保存、インデックス作成、クエリを行う |

## 追加リソース

- [ベクターカラム](https://supabase.com/docs/guides/ai/vector-columns)
- [ベクターインデックス](https://supabase.com/docs/guides/ai/vector-indexes)
- [権限付きRAG](https://supabase.com/docs/guides/ai/rag-with-permissions)
- [本番環境への移行](https://supabase.com/docs/guides/ai/going-to-prod)
- [コンピュートの選択](https://supabase.com/docs/guides/ai/choosing-compute-addon)