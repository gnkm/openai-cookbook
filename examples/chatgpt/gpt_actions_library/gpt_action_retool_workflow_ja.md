# GPT Action Library: Retool Workflow

## はじめに

このページでは、特定のアプリケーション向けのGPT Actionを構築する開発者向けの手順とガイドを提供します。進める前に、まず以下の情報を理解しておいてください：
- [GPT Actionsの紹介](https://platform.openai.com/docs/actions)
- [GPT Actions Libraryの紹介](https://platform.openai.com/docs/actions/actions-library)
- [GPT Actionをゼロから構築する例](https://platform.openai.com/docs/actions/getting-started)

この特定のGPT Actionは、**Retool Workflow**への接続方法の概要を提供します。このActionはユーザーの入力を受け取り、webhookトリガーを使用してRetoolのワークフローに送信します。Retoolは設定されたワークフローを実行し、JSONオブジェクトとしてChatGPTにレスポンスを返します。

### 価値 + ビジネス利用例

**価値**: ユーザーはChatGPTの自然言語機能を活用して、Retoolの任意のワークフローに直接接続できるようになります。

**利用例**: 
- GPTに組み込みたいカスタムコードがRetoolワークフローで実行されている場合
- データサイエンティストが外部VectorDB（Retool Vectorまたは他のベクターDB）を維持しており、ベクター検索の結果をChatGPTに送り返したい場合
- Retoolが内部サービスへの接続のミドルウェアとして使用されており、Retoolのwebhookを使用してChatGPTにこれらのサービスへのアクセスを提供したい場合

## アプリケーション情報

### アプリケーションの主要リンク

開始前に、アプリケーションの以下のリンクを確認してください：
- アプリケーションWebサイト: https://retool.com/products/workflows
- アプリケーションAPIドキュメント: https://docs.retool.com/workflows

### アプリケーションの前提条件

開始前に、Retool環境で以下の手順を実行してください：
- Retoolアカウントの設定
- シンプルなワークフローの作成

### アプリケーションワークフローの手順

以下は基本的なRetool Workflowの例です。このワークフローは2つの値を受け取り、それらを加算してwebhookトリガーに結果を返します。

***注意:*** ワークフローはGPTからアクセス可能になる前にデプロイされている必要があります。

<!--ARCADE EMBED START--><div style="position: relative; padding-bottom: calc(57.26681127982647% + 41px); height: 0; width: 100%;"><iframe src="https://demo.arcade.software/MG7PcF8fh3RH722eonUb?embed&embed_mobile=tab&embed_desktop=inline&show_copy_link=true" title="Retool Workflow Cookbook" frameborder="0" loading="lazy" webkitallowfullscreen mozallowfullscreen allowfullscreen allow="clipboard-write" style="position: absolute; top: 0; left: 0; width: 100%; height: 100%; color-scheme: light;" ></iframe></div><!--ARCADE EMBED END-->

## ChatGPTの手順

### カスタムGPTの指示

カスタムGPTを作成したら、GPTの役割と実行可能なアクションについてのコンテキストを提供する指示をGPTに追加する必要があります。質問がありますか？この手順の詳細については[開始例](https://platform.openai.com/docs/actions/getting-started)を確認してください。

### OpenAPIスキーマ

カスタムGPTを作成したら、以下のテキストをActionsパネルにコピーしてください。質問がありますか？この手順の詳細については[開始例](https://platform.openai.com/docs/actions/getting-started)を確認してください。

***注意:*** 以下のOpenAPI仕様の__<WORKFLOW_ID>__値を、あなたのワークフローのIDに置き換える必要があります。

```yaml
openapi: 3.1.0
info:
  title: Retool Workflow API
  description: API for interacting with Retool workflows.
  version: 1.0.0
servers:
  - url: https://api.retool.com/v1
    description: Main (production) server
paths:
  /workflows/<WORKFLOW_ID>/startTrigger:
    post:
      operationId: add_numbers
      summary: Takes 2 numbers and adds them.
      description: Initiates a workflow in Retool by triggering a specific workflow ID.
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              properties:
                first:
                  type: integer
                  description: First parameter for the workflow.
                second:
                  type: integer
                  description: Second parameter for the workflow.
      responses:
        "200":
          description: Workflow triggered successfully.
        "400":
          description: Bad Request - Invalid parameters or missing data.
        "401":
          description: Unauthorized - Invalid or missing API key.
      security:
        - apiKeyAuth: []
```

## 認証手順

以下は、このサードパーティアプリケーションとの認証設定に関する手順です。質問がありますか？この手順の詳細については[開始例](https://platform.openai.com/docs/actions/getting-started)を確認してください。

### アクション前の手順

ChatGPTで認証を設定する前に、アプリケーションで以下の手順を実行してください。
- Webhook設定パネルからAPIキーを取得

![retool_api_key.png](../../../images/retool_api_key.png)

### ChatGPTでの設定

ChatGPTで「Authentication」をクリックし、**「API Key」**を選択します。以下の情報を入力してください。

- **API Key**: （Retool Workflow Webhook Triggerから提供されたAPIキーを貼り付け）
- **Auth Type**: Custom
- **Custom Header Name**: X-Workflow-Api-Key

### FAQ & トラブルシューティング

- *認証エラー:* カスタムヘッダー名が正しく設定されていることを確認してください。
- *無効なワークフローエラー:* Retool内でワークフローがデプロイされていることを確認してください。

*優先してほしい統合はありますか？統合にエラーはありますか？githubでPRまたはissueを提出していただければ、確認いたします。*