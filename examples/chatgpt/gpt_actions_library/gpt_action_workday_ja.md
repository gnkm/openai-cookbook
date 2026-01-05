# **Workday GPT Action クックブック**

## **目次**

1. [一般的なアプリ情報](#一般的なアプリ情報)  
2. [ChatGPTからWorkdayへの認証](#chatgptからworkdayへの認証)  
3. [サンプルユースケース: PTO申請と福利厚生プラン照会](#サンプルユースケース-pto申請と福利厚生プラン照会)  
4. [追加リソース](#追加リソース)  
5. [まとめ](#まとめ)

## 一般的なアプリ情報

Workdayは、人的資本管理、給与計算、財務管理のソリューションを提供するクラウドベースのプラットフォームです。ChatGPTをCustom Actionsを通じてWorkdayと統合することで、従業員の問い合わせに対する自動応答の提供、従業員のHRプロセスガイド、Workdayからの重要な情報取得により、HR業務を強化できます。

ChatGPTのCustom ActionsとWorkdayの組み合わせにより、組織はAIを活用してHRプロセスを改善し、タスクを自動化し、パーソナライズされた従業員サポートを提供できます。これには、福利厚生、休暇、給与に関する問い合わせのための仮想HRアシスタントが含まれます。

## ChatGPTからWorkdayへの認証

ChatGPTをWorkdayに接続するには、OAuthを使用します：

* Client IDとClient Secretを取得するためにWorkday管理者アクセスが必要です。  
* 重要なURL:  
    * **認証URL**: `[Workday Tenant URL]/authorize`、通常は次の形式: `https://wd5-impl.workday.com/<your_tenant>/authorize`  
    * **トークンURL**: `[Workday Tenant URL]/token`、通常は次の形式: `https://wd5-impl-services1.workday.com/ccx/oauth2/<your_tenant>/token` 

*WorkdayでAPIクライアントを作成すると、Workdayが提供するURLを参照してください。テナントとデータセンターに基づいて必要な特定のURLが提供されます。*

**OAuthセットアップ手順**:

1. WorkdayでRegister API clientタスクを使用します。
2. 以下の提供例と同様に、workdayでAPIクライアント設定を行います。  
3. スコープは、GPTが実行するアクションによって異なります。このユースケースでは、次のものが必要です: `Staffing`、`Tenant Non-Configurable`、`Time Off and Leave`、`Include Workday Owned Scope`
4. GPTからの**Redirection URI**をAPIクライアント設定に入力します。
5. 後でGPTで使用するために**Client ID**と**Client Secret**を保存します。  
6. 以下に示すように、GPT認証セクションにOAuth詳細を追加します。  

*リダイレクションURIは、認証としてOAuthが選択されたGPTセットアップ画面で、GPTセットアップから取得されます。* 

![workday-cgpt-oauth.png](../../../../images/workday-cgpt-oauth.png)

![workday-api-client.png](../../../../images/workday-api-client.png)

[APIクライアントに関するWorkdayコミュニティページ]((https://doc.workday.com/admin-guide/en-us/authentication-and-security/authentication/oauth/dan1370797831010.html))は、より詳しく学ぶための良いリソースになります *（これにはコミュニティアカウントが必要です）*。

## サンプルユースケース: PTO申請と福利厚生プラン照会

### 概要

このユースケースでは、従業員がPTO申請を提出し、従業員詳細を取得し、RAASレポートを通じて福利厚生プランを表示する方法を実演します。

## GPT指示

PTO申請ユースケース、従業員詳細取得、福利厚生プラン照会をカバーするために、以下の指示を使用してください：

```
# **コンテキスト:** あなたは、Workdayシステムを通じてPTO申請、従業員詳細、福利厚生プランに関する詳細情報を提供することで従業員をサポートします。PTO申請の提出、個人および職務関連情報の取得、福利厚生プランの表示を支援します。従業員は基本的なHR用語に精通していると仮定してください。
# **指示:**
## シナリオ
### - ユーザーがPTO申請の提出を求める場合、この3ステップのプロセスに従ってください:
1. 開始日、終了日、休暇の種類を含むPTO詳細をユーザーに尋ねます。
2. `Request_Time_Off` API呼び出しを使用して申請を提出します。
3. 承認に関する情報を含む、提出されたPTO申請の要約を提供します。

### - ユーザーが従業員詳細の取得を求める場合、この2ステップのプロセスに従ってください:
1. `Get_Workers`を使用して従業員の詳細を取得します。
2. 簡単な参照のために、従業員の職位、部署、連絡先詳細を要約します。

### - ユーザーが福利厚生プランについて問い合わせる場合、この2ステップのプロセスに従ってください:
1. `Get_Report_As_A_Service`を使用して福利厚生プラン詳細を取得します。
2. 福利厚生の要約を提示します。
```

### 従業員に代わってリクエストを作成する

従業員IDは従業員に対してWorkdayでアクションを実行するために必要なため、この情報は任意のクエリを実行する前に取得する必要があります。これは、認証後にログインしているユーザーを提供するworkdayのRAASレポートを呼び出すことで実現しました。REST API呼び出しだけでこれを行う別の方法があるかもしれません。IDが返されると、他のすべてのアクションで使用されます。

サンプルRAASレポート: Current Userフィールドを使用すると、OAuthで認証された従業員が返されます。    
![custom-report-workday-01.png](../../../../images/custom-report-workday-01.png)

![custom-report-workday-02.png](../../../../images/custom-report-workday-02.png)

### OpenAPIスキーマ

以下は、Workday REST APIリファレンスと[ActionsGPT](https://chatgpt.com/g/g-TYEliDU6A-actionsgpt)を使用して生成されたOpenAPIスキーマの例です。

以下のAPI呼び出しを使用しています：
* **\[POST\] Request\_Time\_Off**: 従業員の休暇申請を作成します。  
* **\[GET\] Get\_Workers**: 従業員詳細の情報を取得します。  
* **\[GET\] Get\_eligibleAbsenceTypes**: 対象の休暇プランを取得します。  
* **\[GET\] Get\_Report\_As\_A\_Service (RAAS)**: 福利厚生詳細のカスタムRAASレポートを含むレポートを取得します。

パスを正しいテナントIDに置き換え、適切なサーバーに設定してください。異なるPTOタイプに対して必要なIDが正しく設定されていることを確認してください。

```yaml
openapi: 3.1.0
info:
  title: Workday Employee API
  description: API to manage worker details, absence types, and benefit plans in Workday.
  version: 1.3.0
servers:
  - url: https://wd5-impl-services1.workday.com/ccx
    description: Workday Absence Management API Server
paths:
  /service/customreport2/tenant/GPT_RAAS:
    get:
      operationId: getAuthenticatedUserIdRaaS
      summary: Retrieve the Employee ID for the authenticated user.
      description: Fetches the Employee ID for the authenticated user from Workday.
      responses:
        '200':
          description: A JSON object containing the authenticated user's Employee ID.
          content:
            application/json:
              schema:
                type: object
                properties:
                  employeeId:
                    type: string
                    description: The Employee ID of the authenticated user.
                    example: "5050"
        '401':
          description: Unauthorized - Invalid or missing Bearer token.
      security:
        - bearerAuth: []

  /api/absenceManagement/v1/tenant/workers/Employee_ID={employeeId}/eligibleAbsenceTypes:
    get:
      operationId: getEligibleAbsenceTypes
      summary: Retrieve eligible absence types by Employee ID.
      description: Fetches a list of eligible absence types for a worker by their Employee ID, with a fixed category filter.
      parameters:
        - name: employeeId
          in: path
          required: true
          description: The Employee ID of the worker (passed as `Employee_ID=3050` in the URL).
          schema:
            type: string
            example: "5050"
        - name: category
          in: query
          required: true
          description: Fixed category filter for the request. This cannot be changed.
          schema:
            type: string
            example: "17bd6531c90c100016d4b06f2b8a07ce"
      responses:
        '200':
          description: A JSON array of eligible absence types.
          content:
            application/json:
              schema:
                type: object
                properties:
                  absenceTypes:
                    type: array
                    items:
                      type: object
                      properties:
                        id:
                          type: string
                        name:
                          type: string
        '401':
          description: Unauthorized - Invalid or missing Bearer token.
        '404':
          description: Worker or absence types not found.
      security:
        - bearerAuth: []

  /api/absenceManagement/v1/tenant/workers/Employee_ID={employeeId}:
    get:
      operationId: getWorkerById
      summary: Retrieve worker details by Employee ID.
      description: Fetches detailed information of a worker using their Employee ID.
      parameters:
        - name: employeeId
          in: path
          required: true
          description: The Employee ID of the worker.
          schema:
            type: string
            example: "5050"
      responses:
        '200':
          description: A JSON object containing worker details.
          content:
            application/json:
              schema:
                type: object
                properties:
                  id:
                    type: string
                  name:
                    type: object
                    properties:
                      firstName:
                        type: string
                      lastName:
                        type: string
                  position:
                    type: string
                  email:
                    type: string
        '401':
          description: Unauthorized - Invalid or missing Bearer token.
        '404':
          description: Worker not found.
      security:
        - bearerAuth: []

  /api/absenceManagement/v1/tenant/workers/Employee_ID={employeeId}/requestTimeOff:
    post:
      operationId: requestTimeOff
      summary: Request time off for a worker.
      description: Allows a worker to request time off by providing the necessary details.
      parameters:
        - name: employeeId
          in: path
          required: true
          description: The Employee ID of the worker requesting time off.
          schema:
            type: string
            example: "5050"
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              properties:
                days:
                  type: array
                  description: Array of days for which the time off is being requested.
                  items:
                    type: object
                    properties:
                      start:
                        type: string
                        format: date
                        description: The start date of the time off.
                        example: "2024-11-26"
                      date:
                        type: string
                        format: date
                        description: The specific date for the time off.
                        example: "2024-11-26"
                      end:
                        type: string
                        format: date
                        description: The end date of the time off.
                        example: "2024-11-26"
                      dailyQuantity:
                        type: number
                        description: The number of hours per day to take off.
                        example: 8
                      timeOffType:
                        type: object
                        description: Time off type with corresponding ID.
                        properties:
                          id:
                            type: string
                            description: The ID of the time off type.
                            example: "b35340ce4321102030f8b5a848bc0000"
                            enum:
                              - <flexible_time_off_id_from_workday>  # Flexible Time Off ID (hexa format)
                              - <sick_leave_id_from_workday>  # Sick Leave ID (hexa format)
      responses:
        '200':
          description: Time off request created successfully.
        '400':
          description: Invalid input or missing parameters.
        '401':
          description: Unauthorized - Invalid or missing Bearer token.
        '404':
          description: Worker not found.
      security:
        - bearerAuth: []

  /service/customreport2/tenant/GPT_Worker_Benefit_Data:
    get:
      operationId: getWorkerBenefitPlans
      summary: Retrieve worker benefit plans enrolled by Employee ID.
      description: Fetches the benefit plans in which the worker is enrolled using their Employee ID.
      parameters:
        - name: Worker!Employee_ID
          in: query
          required: true
          description: The Employee ID of the worker.
          schema:
            type: string
            example: "5020"
        - name: format
          in: query
          required: true
          description: The format of the response (e.g., `json`).
          schema:
            type: string
            example: "json"
      responses:
        '200':
          description: A JSON array of the worker's enrolled benefit plans.
          content:
            application/json:
              schema:
                type: object
                properties:
                  benefitPlans:
                    type: array
                    items:
                      type: object
                      properties:
                        planName:
                          type: string
                        coverage:
                          type: string
                        startDate:
                          type: string
                          format: date
                        endDate:
                          type: string
                          format: date
        '401':
          description: Unauthorized - Invalid or missing Bearer token.
        '404':
          description: Worker or benefit plans not found.
      security:
        - bearerAuth: []

components:
  securitySchemes:
    bearerAuth:
      type: http
      scheme: bearer
      bearerFormat: JWT
  schemas:
    worker:
      type: object
      properties:
        id:
          type: string
        name:
          type: object
          properties:
            firstName:
              type: string
            lastName:
              type: string
        position:
          type: string
        email:
          type: string
    absenceTypes:
      type: array
      items:
        type: object
        properties:
          id:
            type: string
          name:
            type: string
    benefitPlans:
      type: array
      items:
        type: object
        properties:
          planName:
            type: string
          coverage:
            type: string
          startDate:
            type: string
            format: date
          endDate:
            type: string
            format: date
    timeOffTypes:
      type: object
      description: Mapping of human-readable time off types to their corresponding IDs.
      properties:
        Flexible Time Off:
          type: string
          example: "b35340ce4321102030f8b5a848bc0000"
        Sick Leave:
          type: string
          example: "21bd0afbfbf21011e6ccc4dc170e0000"


```

## まとめ

PTO申請、従業員詳細取得、福利厚生プラン照会などの機能を持つWorkday用GPTのセットアップ、おめでとうございます！

この統合により、HRプロセスを合理化し、個人詳細への迅速なアクセスを提供し、従業員がPTOを簡単に申請できるようになります。このガイドは、ChatGPTとWorkdayを実装するためのカスタマイズ可能なフレームワークを提供し、さらなるアクションを簡単に追加してGPT機能をさらに強化できます。

![workday-gpt.png](../../../../images/workday-gpt.png)

![pto-request.png](../../../../images/pto-request.png)