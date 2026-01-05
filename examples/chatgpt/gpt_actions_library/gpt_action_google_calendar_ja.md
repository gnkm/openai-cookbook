# GPT Action Library: Google Calendar

## はじめに

このページでは、特定のアプリケーション向けのGPT Actionを構築する開発者向けの手順とガイドを提供します。進める前に、まず以下の情報をよく理解しておいてください：

- [GPT Actionsの紹介](https://platform.openai.com/docs/actions)
- [GPT Actions Libraryの紹介](https://platform.openai.com/docs/actions/actions-library)
- [GPT Actionをゼロから構築する例](https://platform.openai.com/docs/actions/getting-started)

このGPT Actionは、**Google Calendar**への接続方法の概要を提供します。OAuthを使用してGoogleアカウントにリンクし、カレンダー内でイベントの作成、読み取り、更新、削除を可能にします。

### 価値 + ビジネス活用例

**価値**: ユーザーはChatGPTの自然言語機能を活用して、Google Calendarに直接接続できるようになります。

**活用例**: 
- カレンダーに新しいイベントを作成したい場合
- 特定の条件に基づいてカレンダーのイベントを検索したい場合
- カレンダーからイベントを削除したい場合

***注意:*** これは、@<あなたのGPTの名前>機能を使用して他のGPTから呼び出すのに有用なGPTの良い例です。この機能の詳細については、[ヘルプサイト](https://help.openai.com/en/articles/8908924-what-is-the-mentions-feature-for-gpts)をご覧ください。

## アプリケーション情報

### アプリケーションの前提条件

開始する前に、以下の前提条件を満たせることを確認してください。

- Google CalendarアクセスのあるGoogleアカウント
- Google Calendar APIにアクセスし、Google Cloud ConsoleでOAuth認証情報を設定する権限

# Google Calendar設定手順

## Google Calendar APIの有効化

- [console.cloud.google.com](https://console.cloud.google.com)にアクセスします。
- プロジェクトセレクターで、このGPT Actionに使用したいプロジェクトを選択します。まだプロジェクトがない場合は、**Create Project**ボタンをクリックします。
- 新しいプロジェクトを作成する際は、プロジェクト名を入力し、関連付けたい請求アカウントを選択します。この例では、'No Organization'が選択されています。

<!--ARCADE EMBED START--><div style="position: relative; padding-bottom: calc(55.43981481481482% + 41px); height: 0; width: 100%;"><iframe src="https://demo.arcade.software/0QxHM3NKyUZcv3di9CkA?embed&embed_mobile=tab&embed_desktop=inline&show_copy_link=true" title="Cookbook | Create Google Cloud Project" frameborder="0" loading="lazy" webkitallowfullscreen mozallowfullscreen allowfullscreen allow="clipboard-write" style="position: absolute; top: 0; left: 0; width: 100%; height: 100%; color-scheme: light;" ></iframe></div><!--ARCADE EMBED END-->

これでGoogle Cloud Projectができ、Google CalendarへのAPIアクセスを設定する準備が整いました。

- クイックアクセスメニューで、**APIs & Services** > **Library**を選択します
- **Google Calendar API**（DKIMではない）を検索してクリックします。
- **Enable**ボタンをクリックします。

<!--ARCADE EMBED START--><div style="position: relative; padding-bottom: calc(53.793774319066145% + 41px); height: 0; width: 100%;"><iframe src="https://demo.arcade.software/uEOZVBdf8OZ8sP0DZAld?embed&embed_mobile=tab&embed_desktop=inline&show_copy_link=true" title="Cookbook | Enable Google Calendar API" frameborder="0" loading="lazy" webkitallowfullscreen mozallowfullscreen allowfullscreen allow="clipboard-write" style="position: absolute; top: 0; left: 0; width: 100%; height: 100%; color-scheme: light;" ></iframe></div><!--ARCADE EMBED END-->

## OAuth認証情報の作成

次のステップは、GPT ActionがGoogle CalendarにアクセスできるようにするためのOAuth認証情報を設定することです。

現在の設定によっては、OAuth同意画面を設定する必要がある場合があります。まずはそれから始めます。

- 左メニューで**Credentials**をクリックします
- **Configure consent screen**をクリックします
- オプションが表示された場合は、**Go To New Experience**を選択し、**Get Started**をクリックします
- アプリ名を入力し、User support emailドロップダウンでメールアドレスを選択します。
- Internal audienceを選択し、連絡先メールアドレスを入力します。
- 利用規約に同意し、**Create**をクリックします

<!--ARCADE EMBED START--><div style="position: relative; padding-bottom: calc(53.793774319066145% + 41px); height: 0; width: 100%;"><iframe src="https://demo.arcade.software/Xs5oyXa1ssYY9zyPsL0s?embed&embed_mobile=tab&embed_desktop=inline&show_copy_link=true" title="Cookbook | Create Consent Screen" frameborder="0" loading="lazy" webkitallowfullscreen mozallowfullscreen allowfullscreen allow="clipboard-write" style="position: absolute; top: 0; left: 0; width: 100%; height: 100%; color-scheme: light;" ></iframe></div><!--ARCADE EMBED END-->

これでOAuth認証情報を作成する準備が整いました。

- **Create OAuth Credentials**をクリックします
- **Web Application**を選択します
- アプリケーション名を入力します
- Authorizes JavaScript Originsの下に、`https://chat.openai.com`と`https://chatgpt.com`を入力します
- 今のところ**Authorized redirect URIs**は空白のままにしておきます（後で戻ってきます）
- **Create**をクリックします
- 認証情報ページを開くと、画面右側にOAuthクライアントIDとクライアントシークレットが表示されます。

<!--ARCADE EMBED START--><div style="position: relative; padding-bottom: calc(53.793774319066145% + 41px); height: 0; width: 100%;"><iframe src="https://demo.arcade.software/OHyS6C3ETFPCc4eqrQ4a?embed&embed_mobile=tab&embed_desktop=inline&show_copy_link=true" title="OAuth overview – Google Auth Platform – cookbook-demo – Google Cloud console" frameborder="0" loading="lazy" webkitallowfullscreen mozallowfullscreen allowfullscreen allow="clipboard-write" style="position: absolute; top: 0; left: 0; width: 100%; height: 100%; color-scheme: light;" ></iframe></div><!--ARCADE EMBED END-->

## OAuthスコープの設定

次に、OAuthクライアントIDがアクセスできるスコープ（またはサービス）を設定します。この場合、Google Calendar APIへのアクセスを設定します。

- 左メニューで**Data Access**をクリックします
- **Add or Remove Scopes**をクリックします
- 右パネルで`https://www.googleapis.com/auth/calendar`でフィルタリングします
- フィルタリングされた結果で、最初の結果を選択します。スコープは`/auth/calendar`で終わるはずです
- **Update**をクリックし、次に**Save**をクリックします

<!--ARCADE EMBED START--><div style="position: relative; padding-bottom: calc(53.793774319066145% + 41px); height: 0; width: 100%;"><iframe src="https://demo.arcade.software/mbsRtOs10arPZtzjeum2?embed&embed_mobile=tab&embed_desktop=inline&show_copy_link=true" title="Clients – Google Auth Platform – cookbook-demo – Google Cloud console" frameborder="0" loading="lazy" webkitallowfullscreen mozallowfullscreen allowfullscreen allow="clipboard-write" style="position: absolute; top: 0; left: 0; width: 100%; height: 100%; color-scheme: light;" ></iframe></div><!--ARCADE EMBED END-->

# GPT Action設定手順

これでGPT Actionを設定する準備が整いました。まず、GPTがGoogle Calendarで認証できるようにするためのOAuth設定を行います。

- GPTでアクションを作成します。
- 設定の歯車アイコンをクリックし、**OAuth**を選択します
- Google Cloud Consoleから**Client ID**と**Client Secret**を入力します。
- 以下の詳細を入力します：
  - Authorization URL: `https://accounts.google.com/o/oauth2/auth`
  - Token URL: `https://oauth2.googleapis.com/token`
  - Scopes: `https://www.googleapis.com/auth/calendar`
- Token Exchange Methodはデフォルトのままにしておきます。
- **Save**をクリックします

<img src="../../../images/google-calendar-action-config.png" alt="Google Calendar OAuth" width="400"/>

これでアクションのOpenAPIスキーマを入力できます。以下の設定により、イベントの読み取りと作成が可能になります。これをOpenAPIスキーマフィールドに入力してください。

```yaml
openapi: 3.1.0
info:
  title: Google Calendar API
  description: This API allows you to read and create events in a user's Google Calendar.
  version: 1.0.0
servers:
  - url: https://www.googleapis.com/calendar/v3
    description: Google Calendar API server

paths:
  /calendars/primary/events:
    get:
      summary: List events from the primary calendar
      description: Retrieve a list of events from the user's primary Google Calendar.
      operationId: listEvents
      tags:
        - Calendar
      parameters:
        - name: timeMin
          in: query
          description: The lower bound (inclusive) of the events to retrieve, in RFC3339 format.
          required: false
          schema:
            type: string
            format: date-time
            example: "2024-11-01T00:00:00Z"
        - name: timeMax
          in: query
          description: The upper bound (exclusive) of the events to retrieve, in RFC3339 format.
          required: false
          schema:
            type: string
            format: date-time
            example: "2024-12-01T00:00:00Z"
        - name: maxResults
          in: query
          description: The maximum number of events to return.
          required: false
          schema:
            type: integer
            default: 10
        - name: singleEvents
          in: query
          description: Whether to expand recurring events into instances. Defaults to `false`.
          required: false
          schema:
            type: boolean
            default: true
        - name: orderBy
          in: query
          description: The order of events. Can be "startTime" or "updated".
          required: false
          schema:
            type: string
            enum:
              - startTime
              - updated
            default: startTime
      responses:
        '200':
          description: A list of events
          content:
            application/json:
              schema:
                type: object
                properties:
                  items:
                    type: array
                    items:
                      type: object
                      properties:
                        id:
                          type: string
                          description: The event ID
                        summary:
                          type: string
                          description: The event summary (title)
                        start:
                          type: object
                          properties:
                            dateTime:
                              type: string
                              format: date-time
                              description: The start time of the event
                            date:
                              type: string
                              format: date
                              description: The start date of the all-day event
                        end:
                          type: object
                          properties:
                            dateTime:
                              type: string
                              format: date-time
                              description: The end time of the event
                            date:
                              type: string
                              format: date
                              description: The end date of the all-day event
                        location:
                          type: string
                          description: The location of the event
                        description:
                          type: string
                          description: A description of the event
        '401':
          description: Unauthorized access due to missing or invalid OAuth token
        '400':
          description: Bad request, invalid parameters

    post:
      summary: Create a new event on the primary calendar
      description: Creates a new event on the user's primary Google Calendar.
      operationId: createEvent
      tags:
        - Calendar
      requestBody:
        description: The event data to create.
        required: true
        content:
          application/json:
            schema:
              type: object
              properties:
                summary:
                  type: string
                  description: The title of the event
                  example: "Team Meeting"
                location:
                  type: string
                  description: The location of the event
                  example: "Conference Room 1"
                description:
                  type: string
                  description: A detailed description of the event
                  example: "Discuss quarterly results"
                start:
                  type: object
                  properties:
                    dateTime:
                      type: string
                      format: date-time
                      description: Start time of the event
                      example: "2024-11-30T09:00:00Z"
                    timeZone:
                      type: string
                      description: Time zone of the event start
                      example: "UTC"
                end:
                  type: object
                  properties:
                    dateTime:
                      type: string
                      format: date-time
                      description: End time of the event
                      example: "2024-11-30T10:00:00Z"
                    timeZone:
                      type: string
                      description: Time zone of the event end
                      example: "UTC"
                attendees:
                  type: array
                  items:
                    type: object
                    properties:
                      email:
                        type: string
                        description: The email address of an attendee
                        example: "attendee@example.com"
              required:
                - summary
                - start
                - end
      responses:
        '201':
          description: Event created successfully
          content:
            application/json:
              schema:
                type: object
                properties:
                  id:
                    type: string
                    description: The ID of the created event
                  summary:
                    type: string
                    description: The event summary (title)
                  start:
                    type: object
                    properties:
                      dateTime:
                        type: string
                        format: date-time
                        description: The start time of the event
                  end:
                    type: object
                    properties:
                      dateTime:
                        type: string
                        format: date-time
                        description: The end time of the event
        '400':
          description: Bad request, invalid event data
        '401':
          description: Unauthorized access due to missing or invalid OAuth token
        '500':
          description: Internal server error
```

成功すると、設定画面の下部に2つのエンドポイントが表示されます。

<img src="../../../images/google-calendar-action-endpoints.png" alt="Google Calendar Action Endpoints" width="600"/>

# コールバックURLの設定

OAuth設定を構成し、OpenAPIスキーマを設定したので、ChatGPTがコールバックURLを生成します。このURLをGoogle Cloud Consoleの**Authorized redirect URIs**に追加する必要があります。

ChatGPTのアクション設定画面を終了し、下部までスクロールします。そこで、生成されたコールバックURLを見つけることができます。

**注意:** OAuth設定を変更すると、新しいコールバックURLが生成され、これもGoogle Cloud Consoleの**Authorized redirect URIs**に追加する必要があります。

<img src="../../../images/google-calendar-callback.png" alt="Google Calendar Callback URL" width="600"/>

このURLをコピーし、Google Cloud Consoleの**Authorized redirect URIs**に追加して、**Save**をクリックします。

<img src="../../../images/google-calendar-callback-settings.png" alt="Google Calendar Callback URL" width="600"/>

# アクションのテスト

アクションが設定されたので、ChatGPTでテストできます。GPTにテスト質問をしてみてください。例えば：`今日の予定は何ですか？` アクションを初めて使用する場合は、アクションの認証を求められます。**Sign in with googleapis.com**をクリックし、プロンプトに従ってアクションを認証してください。

<img src="../../../images/google-signin.png" alt="Google Calendar Sign In" width="600"/>

認証が完了すると、カレンダーからの結果が表示されるはずです。

<img src="../../../images/google-calendar-results.png" alt="Google Calendar results" width="600"/>