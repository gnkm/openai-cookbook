**[SingleStoreDB](https://singlestore.com)** は、[Vector Functions](https://docs.singlestore.com/managed-service/en/reference/sql-reference/vector-functions.html)を通じてベクトル検索を第一級でサポートしています。2017年に初めて利用可能になり、その後強化された私たちのベクトルデータベースサブシステムは、SQLを使って簡単に、意味的に類似したオブジェクトを見つけるための極めて高速な最近傍検索を可能にします。

SingleStoreDBは、dot_product（コサイン類似度用）およびeuclidean_distance関数を使用してベクトルとベクトル類似度検索をサポートしています。これらの関数は、顔認識、視覚的商品写真検索、テキストベースのセマンティック検索などのアプリケーションで私たちの顧客によって使用されています。生成AI技術の爆発的な普及により、これらの機能はテキストベースのAIチャットボットの確固たる基盤を形成しています。

しかし、SingleStoreDBは構造化データ、JSONベースの半構造化データ、時系列、全文検索、空間、キーバリュー、そしてもちろんベクトルデータを含む複数のデータモデルをサポートする高性能でスケーラブルな最新のSQL DBMSであることを忘れないでください。今すぐSingleStoreDBで次のインテリジェントアプリケーションを強化しましょう！

![SingleStore Open AI](https://user-images.githubusercontent.com/8846480/236985121-48980956-fdc5-49c8-b006-f3a412142676.png)

## 例

このフォルダには、SingleStoreDBとOpenAIを組み合わせて使用する例が含まれています。より多くのシナリオを追加し続けるので、お楽しみに！

| 名前 | 説明 |
| --- | --- |
| [OpenAI wikipedia semantic search](./OpenAI_wikipedia_semantic_search.ipynb) | QAにおけるSingleStoreDBセマンティック検索を通じたChatGPTの精度向上 |