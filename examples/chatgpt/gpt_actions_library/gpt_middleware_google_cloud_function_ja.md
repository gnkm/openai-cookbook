# GPT Action Library (Middleware): Google Cloud Function

## はじめに

このページでは、GPT ActionとGoogle Cloud Functionを接続するためのミドルウェアを構築する開発者向けの手順とガイドを提供します。進める前に、まず以下の情報を理解しておくことを確認してください：
- [GPT Actionsの紹介](https://platform.openai.com/docs/actions)
- [GPT Actions Libraryの紹介](https://platform.openai.com/docs/actions/actions-library)
- [GPT Actionをゼロから構築する例](https://platform.openai.com/docs/actions/getting-started)

この特定のGPT Actionでは、Googleのクラウドベース関数ビルダーである**Google Cloud Function**の構築方法の概要を提供します。このドキュメントは、ユーザーがOAuth保護されたGoogle Cloud FunctionをGPT Actionとサンプルアプリケーションに接続するためのセットアップを支援します。

### 価値 + ビジネス利用例

**価値**: ユーザーはChatGPTの自然言語機能を活用して、Google Cloud Functionに直接接続できるようになります。これは以下のような方法で実現できます：

- GPT Actionsの10万文字制限：ユーザーはミドルウェアを使用してAPIからのテキストレスポンスを前処理できます。例えば、ミドルウェアでOpenAIのAPIを使用してテキストを要約してからChatGPTに送り返すことができます。
- 通常、アクションではユーザーはSaaS APIがテキストを返すことに依存しています。ベンダーAPIからのレスポンスを消化しやすいテキストに変換でき、構造化データや非構造化データなどの異なるデータタイプを処理できます。
- テキストだけでなくファイルを返すことができます。これは、データ分析用のCSVファイルを表示したり、PDFファイルを取得してChatGPTがアップロードとして扱うのに便利です。

**利用例**:
- ユーザーがGoogle Cloud SQLにクエリを実行する必要があるが、ChatGPTとGoogle Cloud SQLの間にミドルウェアアプリが必要な場合
- ユーザーがGoogle Cloud Function内で複数のステップを連続して構築しており、ChatGPTを使用してそのプロセスを開始できるようにする必要がある場合

## アプリケーション情報

### アプリケーションの主要リンク

開始前に、アプリケーションの以下のリンクを確認してください：
- アプリケーションWebサイト: https://cloud.google.com/functions/docs
- アプリケーションAPIドキュメント: https://cloud.google.com/functions/docs/writing/write-http-functions

### アプリケーションの前提条件

開始前に、アプリケーション環境で以下の手順を実行していることを確認してください：
- Google Cloud FunctionとGoogle Cloud APIを作成するアクセス権限を持つGoogle Cloud Console（OAuthクライアントのセットアップに必要）

## アプリケーションのセットアップ

### アプリのインストール

Google Cloud Functionsを作成・デプロイするには3つのオプションがあります：

*   IDE - お気に入りのIDE（例：VS Code）を使用して作成
*   Google Cloud Console - ブラウザを使用して作成
*   Google Cloud CLI (gcloud) - コマンドラインを通じて作成

サポートされているランタイムについては[こちら](https://cloud.google.com/functions/docs/concepts/execution-environment)で確認できます。

#### オプション1: IDE（VSCode）を使用

VSCodeを使用したデプロイ方法については、Googleのドキュメント[こちら](https://cloud.google.com/functions/docs/create-deploy-ide)を参照してください。このアプローチに慣れている場合は、自由に使用してください。

#### オプション2: Google Cloud Consoleで直接

Google Cloud Consoleを使用したデプロイ方法については、ドキュメント[こちら](https://cloud.google.com/functions/docs/console-quickstart)を参照してください。

#### オプション3: Google Cloud CLI（`gcloud`）を使用

Google Cloud Consoleを使用したデプロイ方法については、ドキュメント[こちら](https://cloud.google.com/functions/docs/create-deploy-gcloud)を参照してください。ここでは例を段階的に説明します。

##### パート1: Google Cloud CLI（`gcloud`）のインストールと初期化
実行しているOSに関連する手順[こちら](https://cloud.google.com/sdk/docs/install)に従ってください。このプロセスの最後のステップは、`gcloud init`を実行してGoogleアカウントにサインインすることです。

##### パート2: ローカル開発環境のセットアップ
この例では、Node.js環境をセットアップします。

```
mkdir <directory_name>
cd <directory_name>
```

Node.jsプロジェクトを初期化

```
npm init
```
`npm init`のデフォルト値を受け入れます

##### パート3: 関数の作成
`index.js`ファイルを作成

```
const functions = require('@google-cloud/functions-framework');
const axios = require('axios');

const TOKENINFO_URL = 'https://oauth2.googleapis.com/tokeninfo';

// Register an HTTP function with the Functions Framework that will be executed
// when you make an HTTP request to the deployed function's endpoint.
functions.http('executeGCPFunction', async (req, res) => {
  const authHeader = req.headers.authorization;

  if (!authHeader) {
    return res.status(401).send('Unauthorized: No token provided');
  }

  const token = authHeader.split(' ')[1];
  if (!token) {
    return res.status(401).send('Unauthorized: No token provided');
  }

  try {
    const tokenInfo = await validateAccessToken(token);            
    res.json("You have connected as an authenticated user to Google Functions");
  } catch (error) {
    res.status(401).send('Unauthorized: Invalid token');
  }  
});

async function validateAccessToken(token) {
  try {
    const response = await axios.get(TOKENINFO_URL, {
      params: {
        access_token: token,
      },
    });
    return response.data;
  } catch (error) {
    throw new Error('Invalid token');
  }
}
```
##### パート4: 関数のデプロイ

以下のステップで、`package.json`ファイルに必要な依存関係をインストールして追加します

```
npm install @google-cloud/functions-framework
npm install axios
```

```
npx @google-cloud/functions-framework --target=executeGCPFunction
```

```
gcloud functions deploy gcp-function-for-chatgpt \
  --gen2 \
  --runtime=nodejs20 \
  --region=us-central1 \
  --source=. \
  --entry-point=executeGCPFunction \
  --trigger-http \
  --allow-unauthenticated
```

## ChatGPTの手順

### カスタムGPTの指示

カスタムGPTを作成したら、以下のテキストを指示パネルにコピーしてください。質問がありますか？この手順の詳細については[入門例](https://platform.openai.com/docs/actions/getting-started)を確認してください。

```
When the user asks you to test the integration, you will make a call to the custom action and display the results
```

### OpenAPIスキーマ

カスタムGPTを作成したら、以下のテキストをActionsパネルにコピーしてください。質問がありますか？この手順の詳細については[入門例](https://platform.openai.com/docs/actions/getting-started)を確認してください。

以下は、このミドルウェアへの接続がどのようになるかの例です。このセクションにアプリケーションと関数の情報を挿入する必要があります。

```javascript
openapi: 3.1.0
info:
  title: {insert title}
  description: {insert description}
  version: 1.0.0
servers:
  - url: {url of your Google Cloud Function}
    description: {insert description}
paths:
  /{your_function_name}:
    get:
      operationId: {create an operationID}
      summary: {insert summary}
      responses:
        '200':
          description: {insert description}
          content:
            text/plain:
              schema:
                type: string
                example: {example of response}
```

## 認証手順

以下は、このサードパーティアプリケーションとの認証をセットアップする手順です。質問がありますか？この手順の詳細については[入門例](https://platform.openai.com/docs/actions/getting-started)を確認してください。

### Google Cloud Consoleで
Google Cloud Consoleで、OAuthクライアントID認証情報を作成する必要があります。正しいページに移動するには、Google Cloud Consoleで「Credentials」を検索するか、ブラウザで`https://console.cloud.google.com/apis/credentials?project=<your_project_id>`を入力してください。詳細については[こちら](https://developers.google.com/workspace/guides/create-credentials)で確認できます。

「CREATE CREDENTIALS」をクリックして「Oauth client ID」を選択します。「Application type」で「Web Application」を選択し、アプリケーションの名前を入力します（下記参照）。

![](../../../images/gcp-function-middleware-oauthclient.png)

「OAuth client created」モーダルダイアログで、以下を記録してください：

* Client ID
* Client secret

### ChatGPTで（入門例のステップ2を参照）

ChatGPTで「Authentication」をクリックし、**「OAuth」**を選択します。以下の情報を入力してください。

- **Client ID**: *上記のステップを参照*
- **Client Secret**: *上記のステップを参照*
- **Authorization URL**: `https://accounts.google.com/o/oauth2/auth`
- **Token URL**: `https://oauth2.googleapis.com/token`
- **Scope**: `https://www.googleapis.com/auth/userinfo.email`

### Google Cloud Consoleに戻る（入門例のステップ4を参照しながら）

先ほどGoogle Cloudで作成したOAuth 2.0 Client IDを編集し、カスタムアクションを作成した後に受け取ったコールバックURLを追加します。

![](../../../images/gcp-function-middleware-oauthcallback.png)

### GPTのテスト

これでGPTをテストする準備が整いました。「Test Integration」のような簡単なプロンプトを入力すると、以下が期待されます：

1. Googleへのサインインリクエスト
2. Google Functionへのリクエストの許可
3. 関数からのレスポンスを示すChatGPTからのレスポンス - 例：「You have connected as an authenticated user to Google Functions」

*優先してほしい統合はありますか？統合にエラーはありますか？githubでPRやissueを提出していただければ、確認いたします。*