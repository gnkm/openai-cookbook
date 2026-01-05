# GPT Action Library: Salesforce + Gong

## はじめに

このページでは、GPT ActionをSpecific applicationに接続するミドルウェアを構築する開発者向けの手順とガイドを提供します。進める前に、まず以下の情報をよく理解してください：

- [GPT Actionsの概要](https://platform.openai.com/docs/actions)
- [GPT Actions Libraryの概要](https://platform.openai.com/docs/actions/actions-library)
- [GPT Actionをゼロから構築する例](https://platform.openai.com/docs/actions/getting-started)

この特定のGPT Actionは、SalesforceとGongから情報を取得するGPTの構築方法の概要を提供します。これには、既存のクックブックで文書化されている複数のカスタムアクションの作成が含まれます。次のセクションでこれらのクックブックをハイライトします。

### 価値 + ビジネスユースケースの例

**価値**: ユーザーは以下のためにChatGPTの機能を活用できるようになります：

- Salesforceに接続
- 顧客アカウントを検索
- 過去の通話からGongトランスクリプトを取得

**ユースケースの例**:

営業担当者が今後の顧客ミーティングの準備をしています。この統合を使用することで、Salesforceから関連するアカウント詳細を迅速に取得し、最近のGong通話トランスクリプトにアクセスし、MEDPICCやSPICEDなどの実証済み営業手法に基づいて構造化されたAI生成の要約と洞察を受け取ることができます。これにより、担当者は顧客の現在の状態と次のステップについて明確で実行可能な理解を得ることができます — すべてが数分で完了します。

## アプリケーション情報
この例では、Salesforce とGong（ミドルウェア経由）に接続しています。Salesforceの基本セットアップと認証手順、およびミドルウェアの作成については、既存のクックブックを参照します。

### Salesforce GPT Action

SalesforceのGPT Actionのセットアップに関するクックブックを参照してください。そのクックブックで注意すべき2つの設定は以下の通りです：

- [アプリケーション情報](https://cookbook.openai.com/examples/chatgpt/gpt_actions_library/gpt_action_salesforce#application-information) - Salesforceで理解しておくべき必要な概念をカバーしています
- [認証手順](https://cookbook.openai.com/examples/chatgpt/gpt_actions_library/gpt_action_salesforce#authentication-instructions) - SalesforceでのConnected Appの作成とOAuthの設定（SalesforceとChatGPTの両方）をカバーしています

### ミドルウェア GPT Action
ミドルウェア作成に関する以下のクックブックのいずれかを参照してください：

- [GPT Actions library (Middleware) - AWS](https://cookbook.openai.com/examples/chatgpt/gpt_actions_library/gpt_middleware_aws_function)
- [GPT Actions library (Middleware) - Azure Functions](https://cookbook.openai.com/examples/chatgpt/gpt_actions_library/gpt_middleware_azure_function)
- [GPT Actions library (Middleware) - Google Cloud Function](https://cookbook.openai.com/examples/chatgpt/gpt_actions_library/gpt_middleware_google_cloud_function)

### アプリケーションの前提条件

上記のクックブックの前提条件に加えて、Gong APIキーへのアクセス権があることを確認してください。

## アプリケーションのセットアップ

### サーバーレス関数のデプロイ

このサーバーレス関数は`callIds`の配列を受け取り、Gongからトランスクリプトを取得し、ChatGPTに送信するレスポンスをクリーンアップします。以下は、Azure Functions（Javascript）での例です：

```javascript
const { app } = require('@azure/functions');
const axios = require('axios');

// Replace with your Gong API token
const GONG_API_BASE_URL = "https://api.gong.io/v2";
const GONG_API_KEY = process.env.GONG_API_KEY;

app.http('callTranscripts', {
    methods: ['POST'],
    authLevel: 'function',
    handler: async (request, context) => {        
        try {            
            const body = await request.json();
            const callIds = body.callIds;

            if (!Array.isArray(callIds) || callIds.length === 0) {
                return {
                    status: 400,
                    body: "Please provide call IDs in the 'callIds' array."
                };
            }

            // Fetch call transcripts
            const transcriptPayload = { filter: { callIds } };
            const transcriptResponse = await axios.post(`${GONG_API_BASE_URL}/calls/transcript`, transcriptPayload, {
                headers: {
                    'Authorization': `Basic ${GONG_API_KEY}`,
                    'Content-Type': 'application/json'
                }
            });

            const transcriptData = transcriptResponse.data;

            // Fetch extensive call details
            const extensivePayload = {
                filter: { callIds },
                contentSelector: {
                    exposedFields: { parties: true }
                }
            };

            const extensiveResponse = await axios.post(`${GONG_API_BASE_URL}/calls/extensive`, extensivePayload, {
                headers: {
                    'Authorization': `Basic ${GONG_API_KEY}`,
                    'Content-Type': 'application/json'
                }
            });

            const extensiveData = extensiveResponse.data;

            // Create a map of call IDs to metadata and speaker details
            const callMetaMap = {};
            extensiveData.calls.forEach(call => {
                callMetaMap[call.metaData.id] = {
                    title: call.metaData.title,
                    started: call.metaData.started,
                    duration: call.metaData.duration,
                    url: call.metaData.url,
                    speakers: {}
                };

                call.parties.forEach(party => {
                    callMetaMap[call.metaData.id].speakers[party.speakerId] = party.name;
                });
            });

            // Transform transcript data into content and include metadata
            transcriptData.callTranscripts.forEach(call => {
                const meta = callMetaMap[call.callId];
                if (!meta) {
                    throw new Error(`Metadata for callId ${call.callId} not found.`);
                }

                let content = '';
                call.transcript.forEach(segment => {
                    const speakerName = meta.speakers[segment.speakerId] || "Unknown Speaker";

                    // Combine all sentences for the speaker into a paragraph
                    const sentences = segment.sentences.map(sentence => sentence.text).join(' ');
                    content += `${speakerName}: ${sentences}\n\n`; // Add a newline between speaker turns
                });

                // Add metadata and content to the call object
                call.title = meta.title;
                call.started = meta.started;
                call.duration = meta.duration;
                call.url = meta.url;
                call.content = content;
                
                delete call.transcript;
            });

            // Return the modified transcript data
            return {
                status: 200,
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(transcriptData)
            };
        } catch (error) {
            context.log('[ERROR]', "Error processing request:", error);

            return {
                status: error.response?.status || 500,
                body: {
                    message: "An error occurred while fetching or processing call data.",
                    details: error.response?.data || error.message
                }
            };
        }
    }
});

```

以下は、`package.json`ファイルに含める依存関係です：

```javascript
"dependencies": {
    "@azure/functions": "^4.0.0",
    "axios": "^1.7.7"
  }
```

## ChatGPTの手順

### カスタムGPTの指示

カスタムGPTを作成したら、以下のテキストを指示パネルにコピーしてください。質問がありますか？この手順の詳細については、[Getting Started Example](https://platform.openai.com/docs/actions/getting-started)をご覧ください。

```
# トリガー
ユーザーが準備したいアカウント名を入力

# ステップ
1. アカウント名の取得 - その名前のSalesforceアカウントを検索する`executeSOSLSearch`カスタムアクション（SOSL）を呼び出します。最大5つのアカウントを取得します。クエリは次のようになります - `FIND {Acme} IN ALL FIELDS RETURNING Account(Id, Name) LIMIT 5`

2. アカウントを次の形式で表示 - `Account Name - salesforceID`。ユーザーにどのアカウントに興味があるかを確認してもらいます。

3. アカウントのGong Call IDを取得 - 確認されたアカウントについて、`executeSOQLQuery`を呼び出してすべてのGong Call IDを取得します。次のようになります - `SELECT XXX, YYY, ZZZ
FROM Gong__Gong_Call__c 
WHERE Gong__Primary_Account__c = '<AccountId>' 
ORDER BY Gong__Call_Start__c DESC 
LIMIT 2
`

4. callIdsを`getTranscriptsByCallIds`に渡す

# トリガー
ユーザーが「通話を要約」と言う

# ステップ

トランスクリプトの両方を使用して、以下の出力を提供します

## アカウント名
アカウント名を出力

## 通話の詳細
>トランスクリプトを取得した通話を、日付と参加者と共に以下のテーブル形式でリストしてください：
>>ヘッダー: <通話のタイトル>, <日付>, <参加者>, <Gong URL>

## 推奨ミーティング焦点エリア：
>トランスクリプトを分析してテーマ、課題、機会を特定します。これに基づいて、次のミーティングの推奨焦点エリアのリストを生成します。これらはクライアントのニーズに特化した実行可能で具体的なものである必要があります。各項目がミーティングの焦点となるべき**理由**を説明してください。

以下の各洞察について、洞察を得た**どの通話と日付**を指定してください：

### メトリクス
顧客が達成しようとしている定量化可能な成果。コスト削減、収益増加、ユーザー成長、効率向上などが含まれます。言及されたKPIや成功指標を探してください。

### 経済的購買者
真の経済的意思決定者が言及されたか関与していたかを特定します。これには役職、名前、予算所有権や最終権限のヒントが含まれます。

### 決定基準
顧客がソリューションを評価するために使用する主要な要因は何ですか？これには価格、パフォーマンス、サポート、統合、使いやすさなどが含まれます。

### 決定プロセス
顧客が購買決定を行う計画の説明：段階、関与するステークホルダー、承認プロセス、タイムライン。

### ペーパープロセス
法務、調達、コンプライアンス、または契約関連の手順とタイムラインの言及をここに記録してください。

### 痛みの特定
顧客が直面している核心的なビジネス課題を、理想的には彼ら自身の言葉でハイライトします。緊急性を駆動している要因を理解してください。

### チャンピオン
内部で私たちのソリューションを支持している人はいますか？支持を示す名前、役割、行動を言及してください（例：「これを内部で推進しています」）。

### （オプション）競合
議論された競合ベンダー、内部構築、または代替ソリューションを言及してください。
```
上記の例では、(3)のクエリをカスタムSalesforceオブジェクトからGong Call IDを取得するものに置き換えてください。

これで2つの別々のアクションを作成します - 1つはSalesforceに接続し、もう1つはGong APIを呼び出すミドルウェアに接続します。

### Salesforceカスタムアクション用のOpenAPIスキーマ

カスタムGPTを作成したら、以下のテキストをActionsパネルにコピーしてください。質問がありますか？この手順の詳細については、[Getting Started Example](https://platform.openai.com/docs/actions/getting-started)をご覧ください。

以下は、Salesforceへの接続の例です。このセクションにあなたのURLを挿入する必要があります。

```javascript
openapi: 3.1.0
info:
  title: Salesforce API
  version: 1.0.0
  description: API for accessing Salesforce sObjects and executing queries.
servers:
  - url: https://<subdomain>.my.salesforce.com/services/data/v59.0
    description: Salesforce API server
paths:
  /query:
    get:
      summary: Execute a SOQL Query
      description: Executes a given SOQL query and returns the results.
      operationId: executeSOQLQuery
      parameters:
        - name: q
          in: query
          description: The SOQL query string to be executed.
          required: true
          schema:
            type: string
      responses:
        '200':
          description: Query executed successfully.
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/QueryResult'

  /search:
    get:
      summary: Execute a SOSL Search
      description: Executes a SOSL search based on the given query and returns matching records.
      operationId: executeSOSLSearch
      parameters:
        - name: q
          in: query
          description: The SOSL search string (e.g., 'FIND {Acme}').
          required: true
          schema:
            type: string
      responses:
        '200':
          description: Search executed successfully.
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/SearchResult'

components:
  schemas:
    QueryResult:
      type: object
      description: Result of a SOQL query.
      properties:
        totalSize:
          type: integer
          description: The total number of records matching the query.
        done:
          type: boolean
          description: Indicates if the query result includes all records.
        records:
          type: array
          description: The list of records returned by the query.
          items:
            $ref: '#/components/schemas/SObject'

    SearchResult:
      type: object
      description: Result of a SOSL search.
      properties:
        searchRecords:
          type: array
          description: The list of records matching the search query.
          items:
            $ref: '#/components/schemas/SObject'

    SObject:
      type: object
      description: A Salesforce sObject, which represents a database table record.
      properties:
        attributes:
          type: object
          description: Metadata about the sObject, such as type and URL.
          properties:
            type:
              type: string
              description: The sObject type.
            url:
              type: string
              description: The URL of the record.
        Id:
          type: string
          description: The unique identifier for the sObject.
      additionalProperties: true
```

### Salesforceカスタムアクションの認証手順
[GPT Actions library - Salesforce](https://cookbook.openai.com/examples/chatgpt/gpt_actions_library/gpt_action_salesforce#in-chatgpt)に示されている手順に従ってください。

### Gongに接続するミドルウェア用のOpenAPIスキーマ
この例では、Gong APIを呼び出すAzure Function用にセットアップしています。`url`をあなた自身のミドルウェアURLに置き換えてください。

```
openapi: 3.1.0
info:
  title: Call Transcripts API
  description: API to retrieve call transcripts and associated metadata by specific call IDs.
  version: 1.0.1
servers:
  - url: https://<subdomain>.azurewebsites.net/api
    description: Production server
paths:
  /callTranscripts:
    post:
      operationId: getTranscriptsByCallIds
      x-openai-isConsequential: false
      summary: Retrieve call transcripts by call IDs
      description: Fetches specific call transcripts based on the provided call IDs in the request body.
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              properties:
                callIds:
                  type: array
                  description: List of call IDs for which transcripts need to be fetched.
                  items:
                    type: string
              required:
                - callIds
      responses:
        '200':
          description: A successful response containing the requested call transcripts and metadata.
          content:
            application/json:
              schema:
                type: object
                properties:
                  requestId:
                    type: string
                    description: Unique request identifier.
                  records:
                    type: object
                    description: Metadata about the pagination.
                    properties:
                      totalRecords:
                        type: integer
                        description: Total number of records available.
                      currentPageSize:
                        type: integer
                        description: Number of records in the current page.
                      currentPageNumber:
                        type: integer
                        description: The current page number.
                  callTranscripts:
                    type: array
                    description: List of call transcripts.
                    items:
                      type: object
                      properties:
                        callId:
                          type: string
                          description: Unique identifier for the call.
                        title:
                          type: string
                          description: Title of the call or meeting.
                        started:
                          type: string
                          format: date-time
                          description: Timestamp when the call started.
                        duration:
                          type: integer
                          description: Duration of the call in seconds.
                        url:
                          type: string
                          format: uri
                          description: URL to access the call recording or details.
                        content:
                          type: string
                          description: Transcript content of the call.
        '400':
          description: Invalid request. Possibly due to missing or invalid `callIds` parameter.
        '401':
          description: Unauthorized access due to invalid or missing API key.
        '500':
          description: Internal server error.
```

*優先してほしい統合はありますか？統合にエラーはありますか？githubでPRやissueを提出していただければ、確認いたします。*