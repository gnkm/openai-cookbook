# Azure FunctionsとOAuth、Microsoft Graph APIを使用してChatGPTからO365 / SharePointを検索する

## 概要

このソリューションは、Microsoft Graph APIの[検索機能](https://learn.microsoft.com/en-us/graph/api/resources/search-api-overview?view=graph-rest-1.0)と[ファイル取得](https://learn.microsoft.com/en-us/graph/api/driveitem-get?view=graph-rest-1.0\&tabs=http)機能を使用して、GPTアクションがSharePointやOffice365でユーザーがアクセス可能なファイルのコンテキストでユーザーの質問に答えることを可能にします。Azure Functionsを使用してGraph APIレスポンスを処理し、人間が読める形式に変換したり、ChatGPTが理解できる構造に整理したりします。このコードは方向性を示すものであり、要件に応じて修正する必要があります。

## 動作原理

以下に2つのソリューションがあり、それぞれのコードがリポジトリに含まれています。

最初のソリューション**Solution 1**は、[Actionsでファイルを取得](https://platform.openai.com/docs/actions/sending-files)する機能を使用し、会話に直接アップロードしたかのようにファイルを使用します。Azure Functionはbase64文字列を返し、ChatGPTがそれをファイルに変換し、会話に直接アップロードしたファイルと同じように扱います。このソリューションは以下の他のソリューションよりも多くの種類のファイルを処理できますが、サイズ容量の制限があります（ドキュメント[こちら](https://platform.openai.com/docs/actions/sending-files)を参照）。

2番目のソリューション**Solution 2**は、Azure Function内でファイルを前処理します。Azure Functionはbase64エンコードされたファイルではなく、テキストを返します。前処理とテキストへの変換により、このソリューションは大きな非構造化ドキュメントに最適で、最初のソリューションでサポートされるファイル数を超えて分析したい場合に適しています（ドキュメント[こちら](https://platform.openai.com/docs/actions/sending-files)を参照）。

### Solution 1: [ファイル返却](https://platform.openai.com/docs/actions/sending-files)パターンを使用してGPTにファイルを返す

![](../../../images/solution_1.gif)

このソリューションは、ログインユーザーに基づいてNode.js Azure Functionを使用します：

1. ユーザーの初期質問に基づいて、ユーザーがアクセス可能な関連ファイルを検索します。

2. 見つかった各ファイルについて、base64文字列に変換します。

3. ChatGPTが期待する構造[こちら](https://platform.openai.com/docs/actions/sending-files/inline-option)でデータをフォーマットします。

4. それをChatGPTに返します。GPTは、会話にアップロードしたかのようにそれらのファイルを使用できます。

![](../../../images/solution_1_architecture.png)

### Solution 2: Azure Function内でファイルをテキストに変換

![](../../../images/solution_2.gif)

このソリューションは、ログインユーザーに基づいてNode.js Azure Functionを使用します：

1. ユーザーの初期質問に基づいて、ユーザーがアクセス可能な関連ファイルを検索します。

2. 見つかった各ファイルについて、一貫した読み取り可能な形式に変換し、すべてのテキストを取得します。

3. GPT 3.5-turbo (gpt-3.5-turbo-0125)を使用して、ユーザーの初期質問に基づいてファイルから関連テキストを抽出します。GPT 3.5 turboの価格[こちら](https://openai.com/pricing#language-models)に注意してください - 小さなトークンチャンクを扱うため、このステップのコストは名目的です。

4. そのデータをChatGPTに返します。GPTはその情報を使用してユーザーの初期質問に応答します。

以下のアーキテクチャ図からわかるように、最初の3つのステップはSolution 1と同じです。主な違いは、このソリューションがファイルをbase64文字列ではなくテキストに変換し、GPT 3.5 Turboを使用してそのテキストを要約することです。

![](../../../images/solution_2_architecture.png)

### Microsoft APIと直接やり取りする代わりに、なぜこれが必要なのか？

- [こちら](https://learn.microsoft.com/en-us/graph/search-concept-files)のガイドに従うと、[Microsoft Graph Search API](https://learn.microsoft.com/en-us/graph/search-concept-files)は条件に合うファイルへの参照を返しますが、ファイルの内容自体は返しません。そのため、上記の2つのソリューションに対応する2つのオプションがあります：

  - **Solution 1: 互換性のためにレスポンスを再構築：**

    1. [こちら](https://platform.openai.com/docs/actions/getting-started/inline-option)で概説されている`openaiFileResponse`の期待される構造と一致するように、そのAPIからのレスポンスを再構築する必要があります。

  - **Solution 2: ファイルから直接テキストを抽出：**

    1. 返されたファイルをループし、[Download Fileエンドポイント](https://learn.microsoft.com/en-us/graph/api/driveitem-get-content?view=graph-rest-1.0\&tabs=http)または[Convert Fileエンドポイント](https://learn.microsoft.com/en-us/graph/api/driveitem-get-content-format?view=graph-rest-1.0\&tabs=http)を使用してファイルをダウンロードします

    2. そのバイナリストリームを[pdf-parse](https://www.npmjs.com/package/pdf-parse)を使用して人間が読めるテキストに変換します

    3. その後、今日Actionsに課している100,000文字制限に対応するため、関数内でgpt-3.5-turboを使用して要約することでさらに最適化できます。

## 前提条件

- Azure Function AppsとAzure Entra App Registrationsを作成するアクセス権を持つAzure Portal

- Postman（およびAPIとOAuthの知識）

- _Solution 2のみ：_ platform.openai.comからのOpenAI APIキー

## Solution 1 + Solution 2 インストール手順

以下は、認証付きAzure Functionを設定するための手順です。コードを実装する前に、これらの手順に従ってください。

> これらのインストール手順はSolution 1とSolution 2の両方に適用されます。同じFunction App内で両方のソリューションを別々の関数として設定し、どちらが最適かテストすることをお勧めします。1つの関数を設定すれば、同じFunction App内で別の関数を設定するのに数分しかかかりません。

### アプリのインストール

Azure Functionsの言語とデプロイオプションについては、ドキュメント[こちら](https://learn.microsoft.com/en-us/azure/azure-functions/functions-overview?pivots=programming-language-csharp)の左側で詳しく読むことができます。

#### オプション1: VSCodeを使用

VSCodeを使用してデプロイする方法については、Microsoftのドキュメント[こちら](https://learn.microsoft.com/en-us/azure/azure-functions/functions-develop-vs-code?tabs=node-v4,python-v2,isolated-process\&pivots=programming-language-javascript)を参照してください。このアプローチに慣れている場合は、自由に使用してください。

#### オプション2: Azure Portalで直接

Azure Portalを使用してデプロイする方法については、ドキュメント[こちら](https://learn.microsoft.com/en-us/azure/azure-functions/functions-create-function-app-portal?pivots=programming-language-javascript)を参照してください。ここでは段階的な例を説明します。

> 注意：以下のPart 1 - Part 4を使用して、Entra認証付きの任意のAzure Function Appを設定できます

##### Part 1: 関数の作成

![](../../../images/create_function_app.png)

1. [Azure Function app](https://learn.microsoft.com/en-us/azure/azure-functions/functions-overview?pivots=programming-language-csharp)を作成します。私は以下の設定を使用しましたが、快適に感じる任意の設定を使用できます。すべての言語/オペレーティングシステムがコンソールで直接関数を編集することを許可するわけではないことに注意してください - 以下で選択した組み合わせは許可します。私のウォークスルーでは、すべてをデフォルトのままにして、以下の選択を行いました

   1. 基本

      1. _コードまたはコンテナイメージをデプロイしますか？：_ **コード**

      2. _ランタイムスタック：_ **Node.js**

      3. _オペレーティングシステム：_ **Windows**

   2. ネットワーキング

      1. _パブリックアクセスを有効にする：_ **オン（GPTに接続するために必要）**

2. 上記を完了すると、「デプロイメント」ページに移動します。デプロイメントが完了したら（数分しかかからないはずです）、**「リソースに移動」**をクリックしてFunction Appに戻ります

  > 初回試行時にエラーが発生する場合がありますが、再度作成をクリックすると成功する可能性があります。

##### Part 2: 認証の設定

3. Azure Function Appの左側メニューで、**設定**メニューの下の**認証**をクリックします。

   1. IDプロバイダーを追加

   2. IDプロバイダーとして**Microsoft**を選択します。

   3. テナントタイプとして**ワークフォース**

   4. **新しいアプリケーションを作成します。** 既存のアプリケーションを使用する場合も手順はほぼ同じですが、「Easy Auth」を使用してコールバックURLとAPIが自動的に公開されるため、新しいアプリケーションを作成する方が簡単です。詳細については[**こちら**](https://learn.microsoft.com/en-us/azure/app-service/overview-authentication-authorization)をお読みください。

   5. このページの他のすべての設定はデフォルトのままにしますが、内部ガイドラインに基づいて自由に変更してください。

   6. **権限**タブで、**権限の追加**をクリックし、**Files.Read.All**と**Sites.ReadAll**を追加してから、**追加**します。これにより、このアプリケーションがファイルを読み取ることができ、Microsoft Graph Search APIを使用するために重要です。

4. 作成されたら、**作成したエンタープライズアプリケーションをクリック**します（つまり、Function Appページを離れて、作成したエンタープライズアプリケーションに移動します）**。** 今度は、アプリケーションにログインするユーザーを偽装してAzure Functionを実行するための追加の権限を与えます。詳細については[こちら](https://learn.microsoft.com/en-us/azure/app-service/configure-authentication-provider-aad?tabs=workforce-tenant)を参照してください。

   1. メインページで、**「API権限の表示」**をクリック

   2. **組織が使用するAPI**で**Microsoft Azure App Service**を検索し、**user\_impersonation**を見つけます

   3. それを追加し、Azure Portal上の管理者が**管理者の同意を付与**する必要があります。

5) **そのエンタープライズアプリケーション内で**、**管理**の下の左側メニューで**「APIの公開」**をクリックし、**クリップボードにコピー**ボタンを使用して作成された**スコープ**をコピーします。スコープは「api://\<insert-uuid>/user\_impersonation」のようになります。**後で** `SCOPE`**として保存してください。**

6) **管理**の下の左側メニューで**「認証」**をクリック

   1. **Web**セクションの下に、1つのコールバックURIが自動的に追加されていることがわかります。テスト用にPostmanリダイレクトURI（<https://oauth.pstmn.io/v1/callback>）を追加します。

7) 左側で、**概要**に移動します。**アプリケーション（クライアント）ID**と**ディレクトリ（テナント）ID**をコピーし、**後で** `CLIENT_ID` **と** `TENANT_ID`**として保存してください。**

##### Part 3: テスト関数の設定

8. ホームに移動してから**Function App**に戻ることで、ページを離れます。

9. **関数の作成**をクリックします。この例では、ポータルで開発しますが、VSCodeや他のIDEも使用できます。

   1. **HTTPトリガー**を選択

   2. **認証レベル**については、任意のキータイプを選択できます。

      1. 初回はエラーが発生する可能性がありますが、関数は作成されている可能性があります。ページを更新して確認してください。

10. 作成した関数をクリックします（表示するには更新をクリックする必要がある場合があります）。**関数URLの取得**をクリックし、Postmanでテストするために保存します。後でGPTに配置する際にOpenAPI仕様を作成するときにも使用します。

![](../../../images/get_function_url.png)

11. Function Appに戻り、**構成**をクリックします。`MICROSOFT_PROVIDER_AUTHENTICATION_SECRET`変数の値を表示し、それをコピーし（高度な編集をクリックしてコピー）、**後で保存してください。**

この時点で、テスト関数が作成され、**クライアントID、テナントID、シークレット、スコープ、関数URL**を保存しているはずです。これでPostmanで認証をテストする準備ができました。

##### Part 4: Postmanでの認証テスト

12. これらのOAuth設定を使用してPostmanで作成したエンドポイントにアクセスしてみます：

    1. **Grant Type:** Authorization Code

    2. **Auth URL**: [https://login.microsoftonline.com/](about:blank)`TENANT_ID`[/oauth2/v2.0/authorize](about:blank)

    3. **Auth Token URL**: [https://login.microsoftonline.com/`TENANT_ID`/oauth2/v2.0/token](about:blank)

    4. **Client ID:** 上記ステップ7の`CLIENT_ID`

    5. **Client secret:** 上記ステップ11の`MICROSOFT_PROVIDER_AUTHENTICATION_SECRET`

    6. **Scope**: 上記ステップ5の`SCOPE`

    7. **Client credentials**: Send client credentials in body

13. **Get New Access Token**をクリックし、上記ステップ10で保存したエンドポイントにアクセスする必要があります。成功した場合、次のレスポンスが得られるはずです：`"This HTTP triggered function executed successfully. Pass a name in the query string or in the request body for a personalized response."`

##### Part 5: 関数コードの追加

認証されたAzure Functionができたので、SharePoint / O365を検索するように関数を更新できます。

14. テスト関数に移動し、Solution 1の場合は[このファイル](https://github.com/openai/openai-cookbook/blob/main/examples/chatgpt/sharepoint_azure_function/solution_one_file_retrieval.js)から、Solution 2の場合は[このファイル](https://github.com/openai/openai-cookbook/blob/main/examples/chatgpt/sharepoint_azure_function/solution_two_preprocessing.js)からコードを貼り付けます。関数を保存します。

> **このコードは方向性を示すものです** - そのまま動作するはずですが、ニーズに合わせてカスタマイズするように設計されています（このドキュメントの最後にある例を参照）。

15. **設定**の下の**構成**タブに移動して、以下の環境変数を設定します。Azure UIによっては、これが**環境変数**に直接リストされている場合があります。

    1. `TENANT_ID`: 前のセクションからコピー

    2. `CLIENT_ID`: 前のセクションからコピー

    3. _Solution 2のみ：_

       1. `OPENAI_API_KEY:` platform.openai.comでOpenAI APIキーを作成

16. **開発ツール**の下の**コンソール**タブに移動

    1. コンソールで以下のパッケージをインストール

       1. `npm install @microsoft/microsoft-graph-client`

       2. `npm install axios`

       3. _Solution 2のみ：_

          1. `npm install pdf-parse`

          2. `npm install openai`

17. これが完了したら、Postmanから再度関数を呼び出し（POST呼び出し）、以下を本文に入れます（レスポンスを生成すると思われるクエリと検索用語を使用）。

     *Solution 1*:
     ```json
    {
        "searchTerm": "<検索用語を選択>"
    }
    ```
    *Solution 2*: 
    ```json
    {
        "query": "<質問を選択>",
        "searchTerm": "<検索用語を選択>"
    }
    ```
18. レスポンスが得られた場合、カスタムGPTで設定する準備ができています！

##### Part 6: カスタムGPTでの設定

19. エンドポイント用のOpenAPI仕様を生成します。

20. それをGPTのActionsセクションに貼り付け、認証タイプとしてOAuthを選択します。上記のPostmanと同じ方法でOAuth設定を入力します。

21. アクションを保存すると、GPT構成の下部にコールバックURIが表示されます。そのURLをコピーし、**Azure PortalのFunction Appに戻ります**。

22. **設定**の下の**認証**をクリックし、Entraアプリケーションをクリックします。

23. そこに到着したら、**管理**セクションの下の**認証**をクリックします。

24. そのページの**Web**セクションの下に新しいリダイレクトURIを追加し、ステップ20で取得したコールバックURIを貼り付けて、保存をクリックします。

25. このアクションを使用するようにプロンプトをカスタマイズします。このドキュメントのサンプルGPT指示でサンプルプロンプトを確認できます。これは、searchTermを変更して3回答えを見つけようとするようにカスタマイズされています。

26. GPTをテストすると、期待通りに動作するはずです。

## Solution 1 詳細ウォークスルー: [ファイル返却](https://platform.openai.com/docs/actions/sending-files)パターンを使用してGPTにファイルを返す

以下は、このソリューション固有の設定手順とウォークスルーです。完全なコードは[こちら](https://github.com/openai/openai-cookbook/blob/main/examples/chatgpt/sharepoint_azure_function/solution_one_file_retrieval.js)で確認できます。Solution 2に興味がある場合は、[こちら](#solution-2-converting-the-file-to-text-in-the-azure-function-1)にジャンプできます。

### コードウォークスルー

以下は、関数の異なる部分を説明します。開始する前に、必要なパッケージがインストールされ、環境変数が設定されていることを確認してください（インストール手順セクションを参照）。

#### 認証の実装

以下は、関数で使用するヘルパー関数です。

##### Microsoft Graph Clientの初期化

アクセストークンでGraphクライアントを初期化する関数を作成します。これはOffice 365とSharePointを検索するために使用されます。

```javascript
const { Client } = require('@microsoft/microsoft-graph-client');

function initGraphClient(accessToken) {
    return Client.init({
        authProvider: (done) => {
            done(null, accessToken);
        }
    });
}
```

##### On-Behalf-Of (OBO) トークンの取得

この関数は、既存のベアラートークンを使用してMicrosoftのアイデンティティプラットフォームからOBOトークンを要求します。これにより、認証情報を渡すことができ、検索がログインユーザーがアクセスできるファイルのみを返すことを保証します。

```javascript
const axios = require('axios');
const qs = require('querystring');

async function getOboToken(userAccessToken) {
    const { TENANT_ID, CLIENT_ID, MICROSOFT_PROVIDER_AUTHENTICATION_SECRET } = process.env;
    const params = {
        client_id: CLIENT_ID,
        client_secret: MICROSOFT\_PROVIDER\_AUTHENTICATION\_SECRET,
        grant_type: 'urn:ietf:params:oauth:grant-type:jwt-bearer',
        assertion: userAccessToken,
        requested_token_use: 'on_behalf_of',
        scope: 'https://graph.microsoft.com/.default'
    };

    const url = `https\://login.microsoftonline.com/${TENANT_ID}/oauth2/v2.0/token`;
    try {
        const response = await axios.post(url, qs.stringify(params), {
            headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
        });
        return response.data.access\_token;
    } catch (error) {
        console.error('Error obtaining OBO token:', error.response?.data || error.message);
        throw error;
    }
}
```

#### O365 / SharePointアイテムからのコンテンツ取得

この関数は、ドライブアイテムのコンテンツを取得し、base64文字列に変換し、`openaiFileResponse`形式に合うように再構築します。

```javascript
const getDriveItemContent = async (client, driveId, itemId, name) => {
   try
       const filePath = `/drives/${driveId}/items/${itemId}`;
       const downloadPath = filePath + `/content`
       // ここでコンテンツを取得してbase64に変換
       const fileStream = await client.api(downloadPath).getStream();
       let chunks = [];
           for await (let chunk of fileStream) {
               chunks.push(chunk);
           }
       const base64String = Buffer.concat(chunks).toString('base64');
       // ここでレスポンスに含める他のメタデータを取得
       const file = await client.api(filePath).get();
       const mime_type = file.file.mimeType;
       const name = file.name;
       return {"name":name, "mime_type":mime_type, "content":base64String}
   } catch (error) {
       console.error('Error fetching drive content:', error);
       throw new Error(`Failed to fetch content for ${name}: ${error.message}`);
   }
```

#### リクエストを処理するAzure Functionの作成

これらすべてのヘルパー関数ができたので、Azure Functionは、ユーザーを認証し、検索を実行し、検索結果を反復してテキストを抽出し、GPTにテキストの関連部分を取得することで、フローを調整します。

**HTTPリクエストの処理：** 関数は、HTTPリクエストからクエリとsearchTermを抽出することから始まります。Authorizationヘッダーが存在するかチェックし、ベアラートークンを抽出します。

**認証：** ベアラートークンを使用して、上記で定義したgetOboTokenを使用してMicrosoftのアイデンティティプラットフォームからOBOトークンを取得します。

**Graph Clientの初期化：** OBOトークンを使用して、上記で定義したinitGraphClientを使用してMicrosoft Graphクライアントを初期化します。

**ドキュメント検索：** 検索クエリを構築し、searchTermに基づいてドキュメントを見つけるためにMicrosoft Graph APIに送信します。

**ドキュメント処理**: 検索によって返された各ドキュメントについて：

- getDriveItemContentを使用してドキュメントコンテンツを取得します。

- ドキュメントをbase64文字列に変換し、`openaiFileResponse`構造に合うように再構築します。

**レスポンス**: 関数はそれらをHTTPレスポンスで送り返します。

```javascript
module.exports = async function (context, req) {
   // const query = req.query.query || (req.body && req.body.query);
   const searchTerm = req.query.searchTerm || (req.body && req.body.searchTerm);
   if (!req.headers.authorization) {
       context.res = {
           status: 400,
           body: 'Authorization header is missing'
       };
       return;
   }
   /// 以下は関数に渡されたトークンを取得し、OBOトークンを取得するために使用
   const bearerToken = req.headers.authorization.split(' ')[1];
   let accessToken;
   try {
       accessToken = await getOboToken(bearerToken);
   } catch (error) {
       context.res = {
           status: 500,
           body: `Failed to obtain OBO token: ${error.message}`
       };
       return;
   }
   // 上記で定義したinitGraphClient関数を使用してGraph Clientを初期化
   let client = initGraphClient(accessToken);
   // これはMicrosoft Graph Search APIで使用される検索本文です: https://learn.microsoft.com/en-us/graph/search-concept-files
   const requestBody = {
       requests: [
           {
               entityTypes: ['driveItem'],
               query: {
                   queryString: searchTerm
               },
               from: 0,
               // 以下はGraph APIからの上位10件の検索結果を要約するように設定されていますが、ドキュメントに基づいて構成できます
               size: 10
           }
       ]
   };


   try {
       // ここで検索を実行
       const list = await client.api('/search/query').post(requestBody);
       const processList = async () => {
           // これは各検索レスポンスを処理し、ファイルの内容を取得してgpt-3.5-turboで要約
           const results = [];
           await Promise.all(list.value[0].hitsContainers.map(async (container) => {
               for (const hit of container.hits) {
                   if (hit.resource["@odata.type"] === "#microsoft.graph.driveItem") {
                       const { name, id } = hit.resource;
                       // 以下はファイルが存在する場所
                       const driveId = hit.resource.parentReference.driveId;
                       // 上記で定義したヘルパー関数を使用してコンテンツを取得し、base64に変換し、再構築
                       const contents = await getDriveItemContent(client, driveId, id, name);
                       results.push(contents)
               }
           }));
           return results;
       };
       let results;
       if (list.value[0].hitsContainers[0].total == 0) {
           // Microsoft Graph APIが結果を返さない場合、APIに結果が見つからないことを返す
           results = 'No results found';
       } else {
           // Microsoft Graph APIが結果を返す場合、processListを実行して反復処理
           results = await processList();
           // ここでChatGPTがファイルであることを認識できるようにレスポンスを構造化
           results = {'openaiFileResponse': results}
       }
       context.res = {
           status: 200,
           body: results
       };
   } catch (error) {
       context.res = {
           status: 500,
           body: `Error performing search or processing results: ${error.message}`,
       };
   }
};
```

### カスタマイゼーション

以下は、カスタマイズ可能な潜在的な領域です。

- 何も見つからない場合に一定回数再検索するようにGPTプロンプトをカスタマイズできます。

- 特定のSharePointサイトやO365ドライブのみを検索するように検索クエリをカスタマイズしてコードをカスタマイズできます。これにより検索に焦点を当て、検索を改善できます。現在設定されている関数は、ログインユーザーがアクセスできるすべてのファイルを検索します。

- 特定の種類のファイルのみを返すようにコードを更新できます。例えば、構造化データ/CSVのみを返します。

- Microsoft Graphへの呼び出し内で検索するファイル数をカスタマイズできます。[こちら](https://platform.openai.com/docs/actions/getting-started)のドキュメントに基づいて、最大10ファイルのみを配置する必要があることに注意してください。

### 考慮事項

100K文字以下の返却と[45秒のタイムアウト](https://platform.openai.com/docs/actions/production/timeouts)に関して、Actionsの同じ制限がすべてここに適用されることに注意してください。

- [ファイル返却](https://platform.openai.com/docs/actions/sending-files)と[ファイルアップロード](https://help.openai.com/en/articles/8555545-file-uploads-faq)に関するドキュメントを必ずお読みください。これらの制限がここに適用されます。

### サンプルGPT指示

```text
あなたは、ユーザーの質問に答えるのを助けるQ&Aヘルパーです。APIアクションを通じてドキュメントリポジトリにアクセスできます。ユーザーが質問をしたとき、検索に使用すべきと思われる単一のキーワードまたは用語を「searchTerm」に渡します。

****

シナリオ1: 答えがある場合

アクションが結果を返す場合、アクションからの結果を取得してユーザーの質問に答えようとします。

****

シナリオ2: 結果が見つからない場合

アクションから「No results found」のレスポンスを受け取った場合、そこで停止し、結果がなかったことをユーザーに知らせ、異なる検索用語を試すことを伝え、理由を説明します。別の検索を実行する前に、必ずユーザーに知らせる必要があります。

例：

****

「DEI」の結果が見つかりませんでした。[理由を挿入]のため、今度は[用語を挿入]を試します

****

その後、以前に試したものと似ている異なるsearchTermを、単一の単語で試してください。

これを3回試してください。3回目の後、ユーザーの質問に答える関連ドキュメントが見つからなかったことをユーザーに知らせ、SharePointを確認するよう伝えてください。
各ステップで何を検索しているかを明示的に示してください。

****

どちらのシナリオでも、ユーザーの質問に答えようとしてください。見つけた知識に基づいてユーザーの質問に答えられない場合は、ユーザーに知らせ、SharePointのHRドキュメントを確認するよう求めてください。
```

### サンプルOpenAPI仕様

これは、ドキュメント[こちら](https://platform.openai.com/docs/actions/sending-files)のファイル取得構造に一致するレスポンスを期待し、検索を通知するための`searchTerm`パラメータを渡します。

>スクリーンショット[こちら](#part-3-set-up-test-function)でコピーしたリンクに基づいて、関数アプリ名、関数名、コードを必ず変更してください

```yaml
openapi: 3.0.0
info:
  title: SharePoint Search API
  description: API for searching SharePoint documents.
  version: 1.0.0
servers:
  - url: https://{your_function_app_name}.azurewebsites.net/api
    description: SharePoint Search API server
paths:
  /{your_function_name}?code={enter your specific endpoint id here}:
    post:
      operationId: searchSharePoint
      summary: Searches SharePoint for documents matching a query and term.
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              properties:
                searchTerm:
                  type: string
                  description: A specific term to search for within the documents.
      responses:
        '200':
          description: A CSV file of query results encoded in base64.
          content:
            application/json:
              schema:
                type: object
                properties:
                  openaiFileResponseData:
                    type: array
                    items:
                      type: object
                      properties:
                        name:
                          type: string
                          description: The name of the file.
                        mime_type:
                          type: string
                          description: The MIME type of the file.
                        content:
                          type: string
                          format: byte
                          description: The base64 encoded contents of the file.
        '400':
          description: Bad request when the SQL query parameter is missing.
        '413':
          description: Payload too large if the response exceeds the size limit.
        '500':
          description: Server error when there are issues executing the query or encoding the results.
```

## Solution 2 詳細ウォークスルー: Azure Function内でファイルをテキストに変換

以下は、Azure Function内でファイルを前処理し、要約を抽出するこのソリューション固有の設定手順とウォークスルーです。完全なコードは[こちら](https://github.com/openai/openai-cookbook/blob/main/examples/chatgpt/sharepoint_azure_function/solution_two_preprocessing.js)で確認できます。

### コードウォークスルー

#### 認証の実装

このソリューションは、上記のSolution 1と同じ認証手順に従います - [Microsoft Graph Clientの初期化](#initializing-the-microsoft-graph-client)と[On-Behalf-Of (OBO) トークンの取得](#obtaining-an-on-behalf-of-obo-token)セクションを参照してください。

#### O365 / SharePointアイテムからのコンテンツ取得

この関数は、ドライブアイテムのコンテンツを取得し、異なるファイルタイプを処理し、テキスト抽出のために必要に応じてファイルをPDFに変換します。これは、PDFには[downloadエンドポイント](https://learn.microsoft.com/en-us/graph/api/driveitem-get-content?view=graph-rest-1.0\&tabs=http)を、他のサポートされているファイルタイプには[convertエンドポイント](https://learn.microsoft.com/en-us/graph/api/driveitem-get-content-format?view=graph-rest-1.0\&tabs=http)を使用します。

```javascript
const getDriveItemContent = async (client, driveId, itemId, name) => {
    try {
        const fileType = path.extname(name).toLowerCase();
        // 以下のファイルタイプは、PDFに変換してテキストを抽出できるものです。https://learn.microsoft.com/en-us/graph/api/driveitem-get-content-format?view=graph-rest-1.0&tabs=httpを参照
        const allowedFileTypes = ['.pdf', '.doc', '.docx', '.odp', '.ods', '.odt', '.pot', '.potm', '.potx', '.pps', '.ppsx', '.ppsxm', '.ppt', '.pptm', '.pptx', '.rtf'];
        // filePathはファイルタイプに基づいて変更され、非pdfタイプをpdfに変換するために?format=pdfを追加するため、上記のallowedFileTypesのすべてのファイルがpdfに変換されます
        const filePath = `/drives/${driveId}/items/${itemId}/content` + ((fileType === '.pdf' || fileType === '.txt' || fileType === '.csv') ? '' : '?format=pdf');
        if (allowedFileTypes.includes(fileType)) {
            response = await client.api(filePath).getStream();
            // 以下はレスポンスのチャンクを取得して結合
            let chunks = [];
            for await (let chunk of response) {
                chunks.push(chunk);
            }
            let buffer = Buffer.concat(chunks);
            // 以下はPDFからテキストを抽出
            const pdfContents = await pdfParse(buffer);
            return pdfContents.text;
        } else if (fileType === '.txt') {
            // タイプがtxtの場合、ストリームを作成する必要がなく、代わりにコンテンツを取得するだけ
            response = await client.api(filePath).get();
            return response;
        }  else if (fileType === '.csv') {
            response = await client.api(filePath).getStream();
            let chunks = [];
            for await (let chunk of response) {
                chunks.push(chunk);
            }
            let buffer = Buffer.concat(chunks);
            let dataString = buffer.toString('utf-8');
            return dataString
            
    } else {
        return 'Unsupported File Type';
    }
     
    } catch (error) {
        console.error('Error fetching drive content:', error);
        throw new Error(`Failed to fetch content for ${name}: ${error.message}`);
    }
};
```

#### テキスト分析のためのGPT 3.5-Turboの統合

この関数は、OpenAI SDKを使用してドキュメントから抽出されたテキストを分析し、ユーザークエリに基づいて関連情報を見つけます。これにより、ユーザーの質問に関連するテキストのみがGPTに返されることを保証します。

```javascript
const getRelevantParts = async (text, query) => {
    try {
        // OpenAIキーを使用してOpenAIクライアントを初期化
        const openAIKey = process.env["OPENAI_API_KEY"];
        const openai = new OpenAI({
            apiKey: openAIKey,
        });
        const response = await openai.chat.completions.create({
            // タイムアウトを防ぐためにスピードのためgpt-3.5-turboを使用。必要に応じてこのプロンプトを調整できます
            model: "gpt-3.5-turbo-0125",
            messages: [
                {"role": "system", "content": "You are a helpful assistant that finds relevant content in text based on a query. You only return the relevant sentences, and you return a maximum of 10 sentences"},
                {"role": "user", "content": `Based on this question: **"${query}"**, get the relevant parts from the following text:*****\n\n${text}*****. If you cannot answer the question based on the text, respond with 'No information provided'`}
            ],
            // 関連コンテンツを抽出するだけなので、temperature 0を使用
            temperature: 0,
            // max_tokens 1000を使用していますが、検索するドキュメント数に基づいてカスタマイズできます
            max_tokens: 1000
        });
        return response.choices[0].message.content;
    } catch (error) {
        console.error('Error with OpenAI:', error);
        return 'Error processing text with OpenAI' + error;
    }
};
```

#### リクエストを処理するAzure Functionの作成

これらすべてのヘルパー関数ができたので、Azure Functionは、ユーザーを認証し、検索を実行し、検索結果を反復してテキストを抽出し、GPTにテキストの関連部分を取得することで、フローを調整します。

**HTTPリクエストの処理：** 関数は、HTTPリクエストからクエリとsearchTermを抽出することから始まります。Authorizationヘッダーが存在するかチェックし、ベアラートークンを抽出します。

**認証：** ベアラートークンを使用して、上記で定義したgetOboTokenを使用してMicrosoftのアイデンティティプラットフォームからOBOトークンを取得します。

**Graph Clientの初期化：** OBOトークンを使用して、上記で定義したinitGraphClientを使用してMicrosoft Graphクライアントを初期化します。

**ドキュメント検索：** 検索クエリを構築し、searchTermに基づいてドキュメントを見つけるためにMicrosoft Graph APIに送信します。

**ドキュメント処理**: 検索によって返された各ドキュメントについて：

- getDriveItemContentを使用してドキュメントコンテンツを取得します。

- ファイルタイプがサポートされている場合、getRelevantPartsを使用してコンテンツを分析し、クエリに基づいて関連情報を抽出するためにテキストをOpenAIのモデルに送信します。

- 分析結果を収集し、ドキュメント名やURLなどのメタデータを含めます。

**レスポンス**: 関数は結果を関連性でソートし、HTTPレスポンスで送り返します。

```javascript
module.exports = async function (context, req) {
    const query = req.query.query || (req.body && req.body.query);
    const searchTerm = req.query.searchTerm || (req.body && req.body.searchTerm);
    if (!req.headers.authorization) {
        context.res = {
            status: 400,
            body: 'Authorization header is missing'
        };
        return;
    }
    /// 以下は関数に渡されたトークンを取得し、OBOトークンを取得するために使用
    const bearerToken = req.headers.authorization.split(' ')[1];
    let accessToken;
    try {
        accessToken = await getOboToken(bearerToken);
    } catch (error) {
        context.res = {
            status: 500,
            body: `Failed to obtain OBO token: ${error.message}`
        };
        return;
    }
    // 上記で定義したinitGraphClient関数を使用してGraph Clientを初期化
    let client = initGraphClient(accessToken);
    // これはMicrosoft Graph Search APIで使用される検索本文です: https://learn.microsoft.com/en-us/graph/search-concept-files
    const requestBody = {
        requests: [
            {
                entityTypes: ['driveItem'],
                query: {
                    queryString: searchTerm
                },
                from: 0,
                // 以下はGraph APIからの上位10件の検索結果を要約するように設定されていますが、ドキュメントに基づいて構成できます
                size: 10
            }
        ]
    };

    try { 
        // コンテンツをトークン化する関数（例：単語に基づく）
        const tokenizeContent = (content) => {
            return content.split(/\s+/);
        };

        // gpt-3.5-turbo用にトークンを10kトークンウィンドウに分割する関数
        const breakIntoTokenWindows = (tokens) => {
            const tokenWindows = []
            const maxWindowTokens = 10000; // 10kトークン
            let startIndex = 0;

            while (startIndex < tokens.length) {
                const window = tokens.slice(startIndex, startIndex + maxWindowTokens);
                tokenWindows.push(window);
                startIndex += maxWindowTokens;
            }

            return tokenWindows;
        };
        // ここで検索を実行
        const list = await client.api('/search/query').post(requestBody);

        const processList = async () => {
            // これは各検索レスポンスを処理し、ファイルの内容を取得してgpt-3.5-turboで要約
            const results = [];

            await Promise.all(list.value[0].hitsContainers.map(async (container) => {
                for (const hit of container.hits) {
                    if (hit.resource["@odata.type"] === "#microsoft.graph.driveItem") {
                        const { name, id } = hit.resource;
                        // 以下を使用してレスポンスに含めるファイルのURLを取得
                        const webUrl = hit.resource.webUrl.replace(/\s/g, "%20");
                        // Microsoft Graph APIがレスポンスをランク付けするため、これを使用して順序付け
                        const rank = hit.rank;
                        // 以下はファイルが存在する場所
                        const driveId = hit.resource.parentReference.driveId;
                        const contents = await getDriveItemContent(client, driveId, id, name);
                        if (contents !== 'Unsupported File Type') {
                            // 以前に定義した関数を使用してコンテンツをトークン化
                            const tokens = tokenizeContent(contents);

                            // トークンを10kトークンウィンドウに分割
                            const tokenWindows = breakIntoTokenWindows(tokens);

                            // 各トークンウィンドウを処理して結果を結合
                            const relevantPartsPromises = tokenWindows.map(window => getRelevantParts(window.join(' '), query));
                            const relevantParts = await Promise.all(relevantPartsPromises);
                            const combinedResults = relevantParts.join('\n'); // 結果を結合

                            results.push({ name, webUrl, rank, contents: combinedResults });
                        } 
                        else {
                            results.push({ name, webUrl, rank, contents: 'Unsupported File Type' });
                        }
                    }
                }
            }));

            return results;
        };
        let results;
        if (list.value[0].hitsContainers[0].total == 0) {
            // Microsoft Graph APIが結果を返さない場合、APIに結果が見つからないことを返す
            results = 'No results found';
        } else {
            // Microsoft Graph APIが結果を返す場合、processListを実行して反復処理
            results = await processList();
            results.sort((a, b) => a.rank - b.rank);
        }
        context.res = {
            status: 200,
            body: results
        };
    } catch (error) {
        context.res = {
            status: 500,
            body: `Error performing search or processing results: ${error.message}`,
        };
    }
};
```

### カスタマイゼーション

以下は、カスタマイズ可能な潜在的な領域です。

- 何も見つからない場合に一定回数再検索するようにGPTプロンプトをカスタマイズできます。

- 特定のSharePointサイトやO365ドライブのみを検索するように検索クエリをカスタマイズしてコードをカスタマイズできます。これにより検索に焦点を当て、検索を改善できます。現在設定されている関数は、ログインユーザーがアクセスできるすべてのファイルを検索します。

- より長いコンテキストのためにgpt-3.5 turboの代わりにgpt-4oを使用できます。これによりコストとレイテンシがわずかに増加しますが、より高品質な要約が得られる可能性があります。

- Microsoft Graphへの呼び出し内で検索するファイル数をカスタマイズできます。

### 考慮事項

100K文字以下の返却と[45秒のタイムアウト](https://platform.openai.com/docs/actions/production/timeouts)に関して、Actionsの同じ制限がすべてここに適用されることに注意してください。

- これはテキストのみで動作し、画像には対応していません。Azure Function内で追加のコードを使用して、GPT-4oを使用して画像の要約を抽出することでカスタマイズできます。

- これは構造化データでは動作しません。構造化データがユースケースの主要部分である場合は、Solution 1をお勧めします。

### サンプルGPT指示

```
あなたは、ユーザーの質問に答えるのを助けるQ&Aヘルパーです。APIアクションを通じてドキュメントリポジトリにアクセスできます。ユーザーが質問をしたとき、その質問を「query」パラメータにそのまま渡し、「searchTerm」には検索に使用すべきと思われる単一のキーワードまたは用語を使用します。

****

シナリオ1: 答えがある場合

アクションが結果を返す場合、アクションからの結果を取得し、アクションから返されたwebUrlとともに簡潔に要約します。アクションからの知識を最大限に活用してユーザーの質問に答えます

****

シナリオ2: 結果が見つからない場合

アクションから「No results found」のレスポンスを受け取った場合、そこで停止し、結果がなかったことをユーザーに知らせ、異なる検索用語を試すことを伝え、理由を説明します。別の検索を実行する前に、必ずユーザーに知らせる必要があります。

例：

****

「DEI」の結果が見つかりませんでした。[理由を挿入]のため、今度は[用語を挿入]を試します

****

その後、以前に試したものと似ている異なるsearchTermを、単一の単語で試してください。

これを3回試してください。3回目の後、ユーザーの質問に答える関連ドキュメントが見つからなかったことをユーザーに知らせ、SharePointを確認するよう伝えてください。各ステップで何を検索しているかを明示的に示してください。

****

どちらのシナリオでも、ユーザーの質問に答えようとしてください。見つけた知識に基づいてユーザーの質問に答えられない場合は、ユーザーに知らせ、SharePointのHRドキュメントを確認するよう求めてください。ファイルがCSV、XLSX、またはXLSの場合、リンクを使用してファイルをダウンロードし、高度なデータ分析を使用するために再アップロードするようユーザーに伝えることができます。
```

### サンプルOpenAPI仕様

以下の仕様は、前処理を通知するための`query`パラメータと、Microsoft Graphで適切なファイルを見つけるための`searchTerm`を渡します。

>スクリーンショット[こちら](#part-3-set-up-test-function)でコピーしたリンクに基づいて、関数アプリ名、関数名、コードを必ず変更してください

```yaml
openapi: 3.0.0
info:
  title: SharePoint Search API
  description: API for searching SharePoint documents.
  version: 1.0.0
servers:
  - url: https://{your_function_app_name}.azurewebsites.net/api
    description: SharePoint Search API server
paths:
  /{your_function_name}?code={enter your specific endpoint id here}:
    post:
      operationId: searchSharePoint
      summary: Searches SharePoint for documents matching a query and term.
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              properties:
                query:
                  type: string
                  description: The full query to search for in SharePoint documents.
                searchTerm:
                  type: string
                  description: A specific term to search for within the documents.
      responses:
        '200':
          description: Search results
          content:
            application/json:
              schema:
                type: array
                items:
                  type: object
                  properties:
                    documentName:
                      type: string
                      description: The name of the document.
                    snippet:
                      type: string
                      description: A snippet from the document containing the search term.
                    url:
                      type: string
                      description: The URL to access the document.
```

## FAQ

- コードで[SharePoint API](https://learn.microsoft.com/en-us/sharepoint/dev/sp-add-ins/get-to-know-the-sharepoint-rest-service?tabs=csom)の代わりにMicrosoft Graph APIを使用するのはなぜですか？

  - SharePoint APIはレガシーです - Microsoftのドキュメント[こちら](https://learn.microsoft.com/en-us/sharepoint/dev/apis/sharepoint-rest-graph)によると、「SharePoint Onlineの場合、SharePointに対するREST APIを使用したイノベーションは、Microsoft Graph REST APIを通じて推進されます。」Graph APIはより柔軟性を提供し、SharePoint APIは[Microsoft Graph APIと直接やり取りする代わりに、なぜこれが必要なのか？](#why-is-this-necessary-instead-of-interacting-with-the-microsoft-api-directly)セクションにリストされている同じファイル問題に直面します。

- これはどのような種類のファイルをサポートしますか？

  - _Solution 1：_

    1. ファイルアップロードに関するドキュメント[こちら](https://help.openai.com/en/articles/8555545-file-uploads-faq)と同じガイドラインに従います。

  - _Solution 2：_

    1. これは、Convert Fileエンドポイントのドキュメント[_こちら_](https://learn.microsoft.com/en-us/graph/api/driveitem-get-content-format?view=graph-rest-1.0\&tabs=http)にリストされているすべてのファイルをサポートします。具体的には、_pdf、doc、docx、odp、ods、odt、pot、potm、potx、pps、ppsx、ppsxm、ppt、pptm、pptx、rtf_をサポートします。

    2. 検索結果がXLS、XLSX、またはCSVを返す場合、これはユーザーにファイルをダウンロードし、高度なデータ分析を使用して質問するために再アップロードするよう促します。上記で述べたように、構造化データがユースケースの一部である場合は、Solution 1をお勧めします。

- なぜOBOトークンを要求する必要があるのですか？

  - Azure Functionへの認証に使用するのと同じトークンをGraph APIへの認証に使用しようとすると、「無効なオーディエンス」トークンエラーが発生します。これは、トークンのオーディエンスがuser\_impersonationのみである可能性があるためです。

  - これに対処するため、関数は[On Behalf Ofフロー](https://learn.microsoft.com/en-us/entra/identity-platform/v2-oauth2-on-behalf-of-flow)を使用してアプリ内でFiles.Read.Allにスコープされた新しいトークンを要求します。これはログインユーザーの権限を継承し、この関数がログインユーザーがアクセス権を持つファイルのみを検索することを意味します。

  - Azure Function Appsはステートレスであることを意図しているため、各リクエストで意図的に新しいOn Behalf Ofトークンを要求しています。Azure Key Vaultと統合してシークレットを保存し、プログラム的に取得することも可能です。