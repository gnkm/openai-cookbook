# Redis

### Redisとは？

Webサービス開発の経験がある開発者の多くは、おそらくRedisに馴染みがあるでしょう。Redisの核心は、キャッシュ、メッセージブローカー、データベースとして使用できるオープンソースのキーバリューストアです。開発者がRedisを選ぶ理由は、高速であり、クライアントライブラリの豊富なエコシステムを持ち、長年にわたって大企業で導入されてきた実績があるからです。

Redisの従来の用途に加えて、Redisは[Redis Modules](https://redis.io/modules)も提供しています。これは新しい機能、コマンド、データ型でRedisを拡張する方法です。モジュールの例には、[RedisJSON](https://redis.io/docs/stack/json/)、[RedisTimeSeries](https://redis.io/docs/stack/timeseries/)、[RedisBloom](https://redis.io/docs/stack/bloom/)、[RediSearch](https://redis.io/docs/stack/search/)があります。

### デプロイメントオプション

Redisをデプロイする方法は数多くあります。ローカル開発では、最も迅速な方法は[Redis Stack dockerコンテナ](https://hub.docker.com/r/redis/redis-stack)を使用することで、ここではこれを使用します。Redis Stackには、組み合わせて使用することで高速なマルチモデルデータストアとクエリエンジンを作成できる多数のRedisモジュールが含まれています。

本番環境での使用では、最も簡単に始める方法は[Redis Cloud](https://redislabs.com/redis-enterprise-cloud/overview/)サービスを使用することです。Redis Cloudは完全管理型のRedisサービスです。また、[Redis Enterprise](https://redislabs.com/redis-enterprise/overview/)を使用して独自のインフラストラクチャにRedisをデプロイすることもできます。Redis Enterpriseは、Kubernetes、オンプレミス、またはクラウドにデプロイできる完全管理型のRedisサービスです。

さらに、すべての主要なクラウドプロバイダー（[AWS Marketplace](https://aws.amazon.com/marketplace/pp/prodview-e6y7ork67pjwg?sr=0-2&ref_=beagle&applicationId=AWSMPContessa)、[Google Marketplace](https://console.cloud.google.com/marketplace/details/redislabs-public/redis-enterprise?pli=1)、または[Azure Marketplace](https://azuremarketplace.microsoft.com/en-us/marketplace/apps/garantiadata.redis_enterprise_1sp_public_preview?tab=Overview)）がマーケットプレイスでRedis Enterpriseを提供しています。

### RediSearchとは？

RediSearchは、Redisにクエリ、セカンダリインデックス、全文検索、ベクトル検索を提供する[Redisモジュール](https://redis.io/modules)です。RediSearchを使用するには、まずRedisデータにインデックスを宣言します。その後、RediSearchクライアントを使用してそのデータをクエリできます。RediSearchの機能セットの詳細については、[RediSearchドキュメント](https://redis.io/docs/stack/search/)を参照してください。

### 機能

RediSearchは、低メモリフットプリントで高速インデックス化を実現するために、圧縮された転置インデックスを使用します。RediSearchインデックスは、完全一致フレーズマッチング、あいまい検索、数値フィルタリングなど、多くの機能を提供してRedisを強化します。その他の機能には以下があります：

* Redisハッシュの複数フィールドの全文インデックス化
* パフォーマンス低下のない増分インデックス化
* ベクトル類似度検索
* ドキュメントランキング（[tf-idf](https://en.wikipedia.org/wiki/Tf%E2%80%93idf)を使用、オプションでユーザー提供の重み付け）
* フィールド重み付け
* AND、OR、NOT演算子を使用した複雑なブール値クエリ
* プレフィックスマッチング、あいまいマッチング、完全フレーズクエリ
* [ダブルメタフォン音韻マッチング](https://redis.io/docs/stack/search/reference/phonetic_matching/)のサポート
* オートコンプリート候補（あいまいプレフィックス候補付き）
* [多言語](https://redis.io/docs/stack/search/reference/stemming/)での語幹ベースクエリ拡張（[Snowball](http://snowballstem.org/)を使用）
* 中国語のトークン化とクエリのサポート（[Friso](https://github.com/lionsoul2014/friso)を使用）
* 数値フィルタと範囲
* [Redis地理空間インデックス](/commands/georadius)を使用した地理空間検索
* 強力な集約エンジン
* すべてのutf-8エンコードテキストのサポート
* 完全なドキュメント、選択されたフィールド、またはドキュメントIDのみの取得
* 結果のソート（例：作成日による）
* RedisJSONを通じたJSONサポート

### クライアント

Redisの大きなエコシステムを考えると、必要な言語のクライアントライブラリがほぼ確実に存在します。標準のRedisクライアントライブラリを使用してRediSearchコマンドを実行できますが、RediSearch APIをラップするライブラリを使用するのが最も簡単です。以下にいくつかの例を示しますが、より多くのクライアントライブラリは[こちら](https://redis.io/resources/clients/)で見つけることができます。

| プロジェクト | 言語 | ライセンス | 作者 | Stars |
|----------|---------|--------|---------|-------|
| [jedis][jedis-url] | Java | MIT | [Redis][redis-url] | ![Stars][jedis-stars] |
| [redis-py][redis-py-url] | Python | MIT | [Redis][redis-url] | ![Stars][redis-py-stars] |
| [node-redis][node-redis-url] | Node.js | MIT | [Redis][redis-url] | ![Stars][node-redis-stars] |
| [nredisstack][nredisstack-url] | .NET | MIT | [Redis][redis-url] | ![Stars][nredisstack-stars] |

[redis-url]: https://redis.com

[redis-py-url]: https://github.com/redis/redis-py
[redis-py-stars]: https://img.shields.io/github/stars/redis/redis-py.svg?style=social&amp;label=Star&amp;maxAge=2592000
[redis-py-package]: https://pypi.python.org/pypi/redis

[jedis-url]: https://github.com/redis/jedis
[jedis-stars]: https://img.shields.io/github/stars/redis/jedis.svg?style=social&amp;label=Star&amp;maxAge=2592000
[Jedis-package]: https://search.maven.org/artifact/redis.clients/jedis

[nredisstack-url]: https://github.com/redis/nredisstack
[nredisstack-stars]: https://img.shields.io/github/stars/redis/nredisstack.svg?style=social&amp;label=Star&amp;maxAge=2592000
[nredisstack-package]: https://www.nuget.org/packages/nredisstack/

[node-redis-url]: https://github.com/redis/node-redis
[node-redis-stars]: https://img.shields.io/github/stars/redis/node-redis.svg?style=social&amp;label=Star&amp;maxAge=2592000
[node-redis-package]: https://www.npmjs.com/package/redis

[redis-om-python-url]: https://github.com/redis/redis-om-python
[redis-om-python-author]: https://redis.com
[redis-om-python-stars]: https://img.shields.io/github/stars/redis/redis-om-python.svg?style=social&amp;label=Star&amp;maxAge=2592000

[redisearch-go-url]: https://github.com/RediSearch/redisearch-go
[redisearch-go-author]: https://redis.com
[redisearch-go-stars]: https://img.shields.io/github/stars/RediSearch/redisearch-go.svg?style=social&amp;label=Star&amp;maxAge=2592000

[redisearch-api-rs-url]: https://github.com/RediSearch/redisearch-api-rs
[redisearch-api-rs-author]: https://redis.com
[redisearch-api-rs-stars]: https://img.shields.io/github/stars/RediSearch/redisearch-api-rs.svg?style=social&amp;label=Star&amp;maxAge=2592000

### デプロイメントオプション

RediSearchを含むRedisをデプロイする方法は多数あります。最も簡単に始める方法はDockerを使用することですが、以下のような多くのデプロイメントオプションがあります：

- [Redis Cloud](https://redis.com/redis-enterprise-cloud/overview/)
- クラウドマーケットプレイス：[AWS Marketplace](https://aws.amazon.com/marketplace/pp/prodview-e6y7ork67pjwg?sr=0-2&ref_=beagle&applicationId=AWSMPContessa)、[Google Marketplace](https://console.cloud.google.com/marketplace/details/redislabs-public/redis-enterprise?pli=1)、または[Azure Marketplace](https://azuremarketplace.microsoft.com/en-us/marketplace/apps/garantiadata.redis_enterprise_1sp_public_preview?tab=Overview)
- オンプレミス：[Redis Enterprise Software](https://redis.com/redis-enterprise-software/overview/)
- Kubernetes：[Redis Enterprise Software on Kubernetes](https://docs.redis.com/latest/kubernetes/)
- [Docker (RediSearch)](https://hub.docker.com/r/redislabs/redisearch)
- [Docker (Redis Stack)](https://hub.docker.com/r/redis/redis-stack)

### クラスターサポート

RediSearchには、数百台のサーバーにわたって数十億のドキュメントにスケールする分散クラスター版があります。現在、分散RediSearchは[Redis Enterprise Cloud](https://redis.com/redis-enterprise-cloud/overview/)と[Redis Enterprise Software](https://redis.com/redis-enterprise-software/overview/)の一部として利用可能です。

詳細については、[RediSearch on Redis Enterprise](https://redis.com/modules/redisearch/)を参照してください。

### 例

- [Product Search](https://github.com/RedisVentures/redis-product-search) - eコマース商品検索（画像とテキスト）
- [Product Recommendations with DocArray / Jina](https://github.com/jina-ai/product-recommendation-redis-docarray) - RedisとDocArrayを使用したコンテンツベースの商品推薦例
- [Redis VSS in RecSys](https://github.com/RedisVentures/Redis-Recsys) - 3つのエンドツーエンドRedis & NVIDIA Merlin推薦システムアーキテクチャ
- [Azure OpenAI Embeddings Q&A](https://github.com/ruoccofabrizio/azure-open-ai-embeddings-qna) - AzureでのOpenAIとRedisを使用したQ&Aサービス
- [ArXiv Paper Search](https://github.com/RedisVentures/redis-arXiv-search) - arXiv学術論文のセマンティック検索

### その他のリソース

ベクトルデータベースとしてRedisを使用する方法の詳細については、以下のリソースを確認してください：

- [Redis Vector Similarity Docs](https://redis.io/docs/stack/search/reference/vectors/) - ベクトル検索のRedis公式ドキュメント
- [Redis-py Search Docs](https://redis.readthedocs.io/en/latest/redismodules.html#redisearch-commands) - RediSearchのRedis-pyクライアントライブラリドキュメント
- [Vector Similarity Search: From Basics to Production](https://mlops.community/vector-similarity-search-from-basics-to-production/) - VSSとベクトルDBとしてのRedisの入門ブログ記事
- [AI-Powered Document Search](https://datasciencedojo.com/blog/ai-powered-document-search/) - AI駆動ドキュメント検索の使用例とアーキテクチャを扱うブログ記事
- [Vector Database Benchmarks](https://jina.ai/news/benchmark-vector-search-databases-with-one-million-data/) - Redisと他のベクトルDBを比較するJina AI VectorDBベンチマーク