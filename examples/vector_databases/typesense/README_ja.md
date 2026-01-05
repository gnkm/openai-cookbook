# Typesense

Typesenseは、[セルフホスト](https://typesense.org/docs/guide/install-typesense.html#option-2-local-machine-self-hosting)または[Typesense Cloud](https://cloud.typesense.org/)で実行できるオープンソースのインメモリ検索エンジンです。

## なぜTypesenseなのか？

Typesenseは、インデックス全体をRAMに保存し（ディスクにバックアップ）することでパフォーマンスに重点を置き、また利用可能なオプションを簡素化し適切なデフォルト設定を行うことで、すぐに使える開発者体験の提供に焦点を当てています。

また、属性ベースのフィルタリングとベクトルクエリを組み合わせて、最も関連性の高いドキュメントを取得することができます。

### その他の機能

ベクトルストレージと検索に加えて、Typesenseは以下の機能も提供しています：

- タイポ許容：タイプミスを優雅に処理し、すぐに使えます。
- 調整可能なランキング：検索結果を完璧に調整することが簡単にできます。
- ソート：クエリ時に特定のフィールドに基づいて結果を動的にソートします（「価格順（昇順）」などの機能に便利）。
- ファセット＆フィルタリング：結果を絞り込み、精緻化します。
- グループ化＆重複排除：類似の結果をグループ化してより多様性を表示します。
- 連合検索：単一のHTTPリクエストで複数のコレクション（インデックス）を検索します。
- スコープ付きAPIキー：マルチテナントアプリケーション向けに、特定のレコードへのアクセスのみを許可するAPIキーを生成します。
- シノニム：単語を互いの同義語として定義し、ある単語を検索すると定義されたシノニムの結果も返されるようにします。
- キュレーション＆マーチャンダイジング：特定のレコードを検索結果の固定位置にブーストして、それらを特集します。
- Raftベースのクラスタリング：高可用性の分散クラスターを設定します。
- シームレスなバージョンアップグレード：Typesenseの新しいバージョンがリリースされても、バイナリを交換してTypesenseを再起動するだけでアップグレードできます。
- ランタイム依存関係なし：Typesenseは単一のバイナリで、ローカルまたは本番環境で単一のコマンドで実行できます。

## 使い方

- OpenAI埋め込みでTypesenseを使用する方法について詳しく学ぶには、こちらのノートブックの例をご覧ください：[examples/vector_databases/Using_vector_databases_for_embeddings_search.ipynb](/examples/vector_databases/Using_vector_databases_for_embeddings_search.ipynb)
- Typesenseのベクトル検索機能について詳しく学ぶには、こちらのドキュメントをお読みください：[https://typesense.org/docs/0.24.1/api/vector-search.html](https://typesense.org/docs/0.24.1/api/vector-search.html)