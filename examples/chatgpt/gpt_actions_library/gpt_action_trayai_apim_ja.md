# GPT Action Library: Tray.ai API管理操作

## はじめに

このページは、複数のアプリケーションにわたってGPT Actionsのセットを構築する開発者向けの説明とガイドを提供します。進める前に、まず以下の情報をよく理解してください：
- [GPT Actionsの紹介](https://platform.openai.com/docs/actions)
- [GPT Actions Libraryの紹介](https://platform.openai.com/docs/actions/actions-library)
- [GPT Actionをゼロから構築する例](https://platform.openai.com/docs/actions/getting-started)

この特定のGPT Action(s)は、**Tray.ai API管理操作**に接続する方法の概要を提供します。

### 価値 + ビジネス利用例

**価値**: ユーザーは、ChatGPTの自然言語機能を活用して、Tray.aiのAPI管理で作成されたAPIに直接接続できるようになります。

**利用例**: 
- Tray.aiは、ワークフローを構成し、ワークフローアクションのスケーリングを処理し、数百のサードパーティAPIとインターフェースするミドルウェアです
- Tray.aiワークフローで実行されているカスタム操作をGPTに組み込みたい場合
- 組織/チーム向けのアクションへのアクセスを単一のAPIインターフェースで管理したい場合

## アプリケーション情報

### アプリケーションの主要リンク

開始前に、アプリケーションの以下のリンクを確認してください：
- アプリケーションWebサイト: https://tray.ai/universal-automation-cloud/api-management
- アプリケーションAPIドキュメント: https://tray.ai/documentation/tray-uac/api-management/api-management-overview/

### アプリケーションの前提条件

開始前に、Tray.ai環境で以下の手順を実行してください：
- Tray.aiアカウントの設定
- シンプルなAPI管理操作のセットを含むプロジェクトの作成

### アプリケーションワークフローの手順

以下は、基本的なAPI管理操作のセットを構築・拡張する例です：\
![Tray.ai APIM Create Operation Gif](../../../images/gptactions_trayai_createoperation.gif)

## ChatGPTの手順

### カスタムGPTの指示

カスタムGPTを作成したら、GPTの役割と実行可能なアクションについてのコンテキストを提供する指示をGPTに追加する必要があります。質問がありますか？この手順の詳細については、[開始例](https://platform.openai.com/docs/actions/getting-started)を確認してください。

### OpenAPIスキーマ

カスタムGPTを作成したら、Tray.aiプロジェクトからAPI仕様をダウンロードし、内容をコピーして、カスタムGPTアクションスキーマに貼り付けます。貼り付け後、スキーマの`openapi`プロパティをバージョン`3.1.0`に更新してください。

以下は、このサードパーティアプリケーションでの認証設定の手順です。質問がありますか？この手順の詳細については、[開始例](https://platform.openai.com/docs/actions/getting-started)を確認してください。

### アクション前の手順

ChatGPTで認証を設定する前に、アプリケーションで以下の手順を実行してください：
- `full`という名前の新しいロールを作成
- 名前、許可する操作、および`"Authentication" == True`とロールが`full`のポリシールールを指定した新しいポリシーを作成
- ロールを`full`に設定した新しいクライアントを作成
- 今後の手順のためにAPIトークンを保存

![Tray.ai APIM Create Operation Gif](../../../images/gptactions_trayai_createclientcredential.gif)

### ChatGPTでの設定

ChatGPTで「認証」をクリックし、**「APIキー」**を選択します。以下の情報を入力してください。

- **APIキー**: （Tray.ai API管理クライアントから提供されたAPIキーを貼り付け）
- **認証タイプ**: Bearer

### FAQ & トラブルシューティング

- *認証/禁止エラー:* APIキーを正しく入力し、`認証タイプ`を`Bearer`に設定していることを確認してください。
- *Tray.ai内部エラー:* エラーハンドリングを設定し、エラーメッセージで応答するようにカスタムGPTへの応答を設定できます。