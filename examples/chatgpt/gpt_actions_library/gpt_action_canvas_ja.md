# Canvas LMS クックブック

### 目次

1. [**一般的なアプリ情報**](#一般的なアプリ情報) - Canvas LMSの概要、その機能、およびAI統合を通じて教育体験を向上させるChatGPTのカスタムアクションの役割。

2. [**ChatGPTからCanvasへの認証**](#chatgptからcanvasへの認証) - ChatGPTをCanvasに接続するための認証方法（OAuthとユーザー生成アクセストークン）の説明と、各オプションの詳細な設定手順。

3. [**サンプルユースケース：学生コースアシスタント**](#サンプルユースケース学生コースアシスタント) - コースナビゲーション、試験準備、個別フィードバックで学生を支援するChatGPTの使用例の詳細、特定のAPI呼び出しとワークフローを含む。

4. [**検討すべきその他のユースケース**](#検討すべきその他のユースケース) - 教室分析やレポート生成など、Canvas APIを使用した追加の潜在的統合。

5. [**おめでとうございます**](#おめでとうございます)  

## 一般的なアプリ情報

Canvasは、オンライン学習と教育をサポートするために設計された広く使用されている学習管理システム（LMS）です。コース管理、コンテンツ配信、評価、学生コラボレーションのための堅牢なツールセットを提供しています。[Canvas REST API](https://canvas.instructure.com/doc/api/all_resources.html)を通じて、CanvasはChatGPTなどのAI搭載ツールを含むサードパーティアプリケーションとの広範なカスタマイズと統合を可能にします。

CanvasとのChatGPTのカスタムアクションにより、教育者はAIを活用してコースコンテンツを強化し、タスクを自動化し、学生に個別化された学習ジャーニーを提供できます。例として、アクティブなコースに基づく仮想ティーチングアシスタントがあり、Canvasから情報を取得して教育的な対話を作成する機能に適しています。カスタムアクション付きChatGPTは、Canvas体験全体を自動化したり、Canvasアプリでの完了により適した多くの機能の代替として機能することを意図していません。

## ChatGPTからCanvasへの認証

カスタムアクションでの認証の一般的な概要については、[アクション認証ドキュメント](https://platform.openai.com/docs/actions/authentication)を参照してください。

Canvasでの認証には2つのオプションがあります：1) OAuthと2) ユーザー生成アクセストークン。
- 大規模展開では、アクション認証にOAuthを使用することが必要です。
- ユーザーが単一ユーザー展開を検討している場合、または管理者設定にアクセスできない場合は、ユーザー生成アクセストークンを検討できます。アクションによって行われるすべてのリクエストは、ユーザーが生成したトークンを使用して行われるため、Canvasはすべてのリクエストをユーザーのアクティビティとして登録し、ユーザーの権限を使用してそれらを完了することに注意してください。

### CanvasでのOAuthの実装

このCanvas CookbookではOAuthを使用していませんが、複数のユーザーがいる展開では必須です。詳細なウォークスルーについては、[Canvas OAuthドキュメント](https://canvas.instructure.com/doc/api/file.oauth.html#oauth2-flow)を参照してください。

Canvas カスタムアクションでOAuthを実装する際に留意すべき点：

- OAuthにはClient IDとClient Secretを取得するためにCanvasの管理者設定へのアクセスが必要です。
- 認証URLは次のようになります（Canvas Install URLを更新してください）：https://<canvas-install-url>/login/oauth2/auth
- トークンURLは次のようになります（Canvas Install URLを更新してください）：https://<canvas-install-url>/login/oauth2/token
- カスタムアクションでスコープを定義する必要がない場合があります。開発者キーがスコープを必要とせず、スコープパラメータが指定されていない場合、アクセストークンはすべてのスコープにアクセスできます。開発者キーがスコープを必要とし、スコープパラメータが指定されていない場合、Canvasは「invalid_scope」で応答します。開発者キーの詳細は[こちら](https://canvas.instructure.com/doc/api/file.developer_keys.html)、エンドポイントは[こちら](https://canvas.instructure.com/doc/api/file.oauth_endpoints.html#get-login-oauth2-auth)。
- トークン交換方法はデフォルト（POSTリクエスト）
- Canvasは`redirect_uri`という用語を使用し、ChatGPTは認証成功後のリダイレクトプロセスを完了するURLに`Callback URL`という用語を使用します。

### ユーザー生成アクセストークンでの認証の実装

場合によっては、Canvasでのカスタムアクション認証に[ユーザー生成アクセストークン](https://canvas.instructure.com/doc/api/file.oauth.html#manual-token-generation)を使用することが適切な場合があります。以下の手順に従ってください：

  1. こちらに示すCanvasアカウント設定に進みます：
  ![canvas_lms_settings_link.png](../../../images/canvas_lms_settings_link.png)
  2. こちらに示すトークンのリストまでスクロールダウンします：          
  ![canvas_lms_list_of_tokens.png](../../../images/canvas_lms_list_of_tokens.png)
  3. 新しいトークンを生成し、**このトークンを保存**してください。後でアクセスできなくなります。
  ![canvas_lms_new_token.png](../../../images/canvas_lms_new_token.png)

## サンプルユースケース：学生コースアシスタント

### 概要

詳細な情報を提供し、個別化された練習試験を生成し、学習を向上させるための建設的なフィードバックを提供することで、学生がコースをナビゲートし理解するのを支援します。

### 考慮事項

- シラバスなどの一部の情報は、APIによってリクエストされるとHTMLページとして返されます。これによりChatGPTで表示することが不可能になります。代わりに、コースの説明、モジュール、課題を参照してユーザーをガイドしてください。
- リクエストは`include[]`クエリパラメータを使用して特定の情報を取得するように変更できます。コースに関する特定の情報をリクエストする必要がある場合は、GPT指示で例を提供してください。

### GPT指示

これらの指示を書く方法は複数あります。プロンプトエンジニアリング戦略とベストプラクティスのガイダンスについては[こちら](https://platform.openai.com/docs/guides/prompt-engineering)を参照してください。

```
# **コンテキスト：** あなたはCanvas学習管理システムでホストされているコースに関する詳細な情報を提供することで大学生をサポートします。コースコンテンツの理解を助け、提供された教材に基づいて練習試験を生成し、学習の旅を支援するための洞察に満ちたフィードバックを提供します。学生は基本的な学術用語に精通していると仮定してください。

# **指示：**

## シナリオ

### - ユーザーが特定のコースに関する情報を求める場合、この5ステップのプロセスに従ってください：
1. 支援を希望するコースと特定の焦点領域（例：コース全体の概要、特定のモジュール）を指定するようユーザーに求めます。
2. リクエストされたコースのコースIDがわからない場合は、listYourCoursesを使用してCanvasで適切なコースと対応するIDを見つけます。返されたコースのリストにリクエストされたコースと一致するコースがない場合は、searchCoursesを使用して類似の名前のコースがあるかどうかを確認します。
3. getSingleCourse API呼び出しとlistModules API呼び出しを使用してCanvasからコース情報を取得します。
4. ユーザーに焦点を当てたいモジュールを尋ね、listModuleItemsを使用してリクエストされたモジュールアイテムを取得します。課題については、それらへのリンクを共有します。
5. ユーザーがより多くの情報を必要とするか、試験の準備が必要かどうかを尋ねます。

### ユーザーが特定のコースの練習テストまたは練習試験を受けたいと言う場合、この6ステップのプロセスに従ってください：
1. 何問の質問かを尋ねます
2. テストしたい章やトピックを尋ね、Canvasのコースモジュールからいくつかの例を提供します。
3. 一度に1つの質問をし、質問が多肢選択式であることを確認します（質問が回答されるまで次の質問を生成しないでください）
4. ユーザーが回答したら、正解か不正解かを伝え、正解の説明を提供します
5. ユーザーにテスト結果をエクスポートしたいかどうかを尋ね、PDFを作成するコードを書きます
6. ユーザーのニーズと進歩に合わせた追加のリソースと学習のヒントを提供し、他のコースやトピックでさらなる支援が必要かどうかを尋ねます。

### ユーザーが学習ガイドの作成を求める場合
- 生成された学習ガイドを表形式でフォーマットします
```

### OpenAPIスキーマ

- 特集されたAPI呼び出し
  - [GET] [listYourCourses](https://canvas.instructure.com/doc/api/courses.html#method.courses.index)
  - [GET] [getSingleCourse](https://canvas.instructure.com/doc/api/courses.html#method.courses.show)
  - [GET] [listModules](https://canvas.instructure.com/doc/api/modules.html#method.context_modules_api.index)
  - [GET] [listModuleItems](https://canvas.instructure.com/doc/api/modules.html#method.context_module_items_api.index)
  - [GET] [searchCourses](https://canvas.instructure.com/doc/api/search.html#method.search.all_courses)

以下は[Canvas APIリファレンス](https://canvas.instructure.com/doc/api/index.html)と[ActionsGPT](https://chatgpt.com/g/g-TYEliDU6A-actionsgpt)の組み合わせで生成されました。

```yaml
openapi: 3.1.0
info:
  title: Canvas API
  description: API for interacting with Canvas LMS, including courses, modules, module items, and search functionalities.
  version: 1.0.0
servers:
  - url: https://canvas.instructure.com/api/v1
    description: Canvas LMS API server
    variables:
      domain:
        default: canvas.instructure.com
        description: The domain of your Canvas instance
paths:
  /courses:
    get:
      operationId: listYourCourses
      summary: List your courses
      description: Retrieves a paginated list of active courses for the current user.
      parameters:
        - name: enrollment_type
          in: query
          description: Filter by enrollment type (e.g., "teacher", "student").
          schema:
            type: string
        - name: enrollment_role
          in: query
          description: Filter by role type. Requires admin permissions.
          schema:
            type: string
        - name: enrollment_state
          in: query
          description: Filter by enrollment state (e.g., "active", "invited").
          schema:
            type: string
        - name: exclude_blueprint_courses
          in: query
          description: Exclude Blueprint courses if true.
          schema:
            type: boolean
        - name: include
          in: query
          description: Array of additional information to include (e.g., "term", "teachers").
          schema:
            type: array
            items:
              type: string
        - name: per_page
          in: query
          description: The number of results to return per page.
          schema:
            type: integer
          example: 10
        - name: page
          in: query
          description: The page number to return.
          schema:
            type: integer
          example: 1
      responses:
        '200':
          description: A list of courses.
          content:
            application/json:
              schema:
                type: array
                items:
                  type: object
                  properties:
                    id:
                      type: integer
                      description: The ID of the course.
                    name:
                      type: string
                      description: The name of the course.
                    account_id:
                      type: integer
                      description: The ID of the account associated with the course.
                    enrollment_term_id:
                      type: integer
                      description: The ID of the term associated with the course.
                    start_at:
                      type: string
                      format: date-time
                      description: The start date of the course.
                    end_at:
                      type: string
                      format: date-time
                      description: The end date of the course.
                    course_code:
                      type: string
                      description: The course code.
                    state:
                      type: string
                      description: The current state of the course (e.g., "unpublished", "available").
        '400':
          description: Bad request, possibly due to invalid query parameters.
        '401':
          description: Unauthorized, likely due to invalid authentication credentials.

  /courses/{course_id}:
    get:
      operationId: getSingleCourse
      summary: Get a single course
      description: Retrieves the details of a specific course by its ID.
      parameters:
        - name: course_id
          in: path
          required: true
          description: The ID of the course.
          schema:
            type: integer
        - name: include
          in: query
          description: Array of additional information to include (e.g., "term", "teachers").
          schema:
            type: array
            items:
              type: string
      responses:
        '200':
          description: A single course object.
          content:
            application/json:
              schema:
                type: object
                properties:
                  id:
                    type: integer
                    description: The ID of the course.
                  name:
                    type: string
                    description: The name of the course.
                  account_id:
                    type: integer
                    description: The ID of the account associated with the course.
                  enrollment_term_id:
                    type: integer
                    description: The ID of the term associated with the course.
                  start_at:
                    type: string
                    format: date-time
                    description: The start date of the course.
                  end_at:
                    type: string
                    format: date-time
                    description: The end date of the course.
                  course_code:
                    type: string
                    description: The course code.
                  state:
                    type: string
                    description: The current state of the course (e.g., "unpublished", "available").
                  is_public:
                    type: boolean
                    description: Whether the course is public.
                  syllabus_body:
                    type: string
                    description: The syllabus content of the course.
                  term:
                    type: object
                    description: The term associated with the course.
                    properties:
                      id:
                        type: integer
                      name:
                        type: string
                      start_at:
                        type: string
                        format: date-time
                      end_at:
                        type: string
                        format: date-time
        '400':
          description: Bad request, possibly due to an invalid course ID or query parameters.
        '401':
          description: Unauthorized, likely due to invalid authentication credentials.
        '404':
          description: Course not found, possibly due to an invalid course ID.

  /courses/{course_id}/modules:
    get:
      operationId: listModules
      summary: List modules in a course
      description: Retrieves the list of modules for a given course in Canvas.
      parameters:
        - name: course_id
          in: path
          required: true
          description: The ID of the course.
          schema:
            type: integer
        - name: include
          in: query
          description: Include additional information such as items in the response.
          schema:
            type: array
            items:
              type: string
            example: ["items"]
        - name: search_term
          in: query
          description: The partial title of the module to match and return.
          schema:
            type: string
        - name: student_id
          in: query
          description: Return module completion information for the student with this ID.
          schema:
            type: integer
        - name: per_page
          in: query
          description: The number of results to return per page.
          schema:
            type: integer
          example: 10
        - name: page
          in: query
          description: The page number to return.
          schema:
            type: integer
          example: 1
      responses:
        '200':
          description: A list of modules in the course.
          content:
            application/json:
              schema:
                type: array
                items:
                  type: object
                  properties:
                    id:
                      type: integer
                      description: The ID of the module.
                    name:
                      type: string
                      description: The name of the module.
                    items_count:
                      type: integer
                      description: The number of items in the module.
                    state:
                      type: string
                      description: The state of the module (e.g., "active", "locked").
        '400':
          description: Bad request, possibly due to an invalid course ID or query parameters.
        '401':
          description: Unauthorized, likely due to invalid authentication credentials.
        '404':
          description: Course not found, possibly due to an invalid course ID.

  /courses/{course_id}/modules/{module_id}/items:
    get:
      operationId: listModuleItems
      summary: List items in a module
      description: Retrieves the list of items within a specific module in a Canvas course.
      parameters:
        - name: course_id
          in: path
          required: true
          description: The ID of the course.
          schema:
            type: integer
        - name: module_id
          in: path
          required: true
          description: The ID of the module.
          schema:
            type: integer
        - name: include
          in: query
          description: Include additional information in the response, such as content details.
          schema:
            type: array
            items:
              type: string
            example: ["content_details"]
        - name: student_id
          in: query
          description: Return completion information for the student with this ID.
          schema:
            type: integer
        - name: per_page
          in: query
          description: The number of results to return per page.
          schema:
            type: integer
          example: 10
        - name: page
          in: query
          description: The page number to return.
          schema:
            type: integer
          example: 1
      responses:
        '200':
          description: A list of items in the module.
          content:
            application/json:
              schema:
                type: array
                items:
                  type: object
                  properties:
                    id:
                      type: integer
                      description: The ID of the module item.
                    title:
                      type: string
                      description: The title of the module item.
                    type:
                      type: string
                      description: The type of the module item (e.g., "Assignment", "File").
                    position:
                      type: integer
                      description: The position of the item within the module.
                    indent:
                      type: integer
                      description: The level of indentation of the item in the module.
                    completion_requirement:
                      type: object
                      description: The completion requirement for the item.
                      properties:
                        type:
                          type: string
                        min_score:
                          type: integer
                    content_id:
                      type: integer
                      description: The ID of the associated content item (e.g., assignment, file).
                    state:
                      type: string
                      description: The state of the item (e.g., "active", "locked").
        '400':
          description: Bad request, possibly due to an invalid module ID or query parameters.
        '401':
          description: Unauthorized, likely due to invalid authentication credentials.
        '404':
          description: Module or course not found, possibly due to an invalid module or course ID.

  /search/all_courses:
    get:
      operationId: searchCourses
      summary: Search for courses
      description: Searches for public courses in Canvas.
      parameters:
        - name: search
          in: query
          description: The search term to filter courses.
          schema:
            type: string
        - name: public_only
          in: query
          description: If true, only returns public courses.
          schema:
            type: boolean
        - name: open_enrollment_only
          in: query
          description: If true, only returns courses with open enrollment.
          schema:
            type: boolean
        - name: enrollment_type
          in: query
          description: Filter by enrollment type (e.g., "teacher", "student").
          schema:
            type: string
        - name: sort
          in: query
          description: Sort the results by "asc" or "desc" order.
          schema:
            type: string
          enum:
            - asc
            - desc
        - name: per_page
          in: query
          description: The number of results to return per page.
          schema:
            type: integer
          example: 10
        - name: page
          in: query
          description: The page number to return.
          schema:
            type: integer
          example: 1
      responses:
        '200':
          description: A list of courses matching the search criteria.
          content:
            application/json:
              schema:
                type: array
                items:
                  type: object
                  properties:
                    id:
                      type: integer
                      description: The ID of the course.
                    name:
                      type: string
                      description: The name of the course.
                    account_id:
                      type: integer
                      description: The ID of the account associated with the course.
                    enrollment_term_id:
                      type: integer
                      description: The ID of the term associated with the course.
                    start_at:
                      type: string
                      format: date-time
                      description: The start date of the course.
                    end_at:
                      type: string
                      format: date-time
                      description: The end date of the course.
                    course_code:
                      type: string
                      description: The course code.
                    state:
                      type: string
                      description: The current state of the course (e.g., "unpublished", "available").
                    is_public:
                      type: boolean
                      description: Whether the course is public.
                    term:
                      type: object
                      description: The term associated with the course.
                      properties:
                        id:
                          type: integer
                        name:
                          type: string
                        start_at:
                          type: string
                          format: date-time
                        end_at:
                          type: string
                          format: date-time
        '400':
          description: Bad request, possibly due to invalid query parameters.
        '401':
          description: Unauthorized, likely due to invalid authentication credentials.
        '404':
          description: No courses found matching the criteria.
```

### サンプル会話スターター

- 練習試験を受けるのを手伝ってください。
- 私のコースの1つの概要を教えてください。
- 私のすべてのコースをリストしてください。

### GPT機能

- [オン] ウェブブラウジング
- [オン] DALL·E画像生成
- [オン] コードインタープリター＆データ分析

## 検討すべきその他のユースケース

以下は、Canvas APIを使用して探索できる追加のユースケースの非網羅的なリストです。それぞれの基本的な概要は提供されていますが、GPT指示と参照される特定のAPI呼び出しは、あなたのニーズに最適なものを決定するために意図的にユーザーに委ねられています。

### 教室分析とレポート

**ユースケース：** 学生のエンゲージメント、成績、参加に関する包括的な分析とパフォーマンスレポートで教師を支援します。このデータを活用することで、教師は情報に基づいた決定を行い、コース配信を調整し、リスクのある学生を特定し、全体的な教室の効果を向上させることができます。

**APIリソース：**

- [**Analytics**](https://canvas.instructure.com/doc/api/analytics.html)と[**Quiz Statistics**](https://canvas.instructure.com/doc/api/quiz_statistics.html)：学生の参加、成績、コースレベルの統計に関する詳細なデータを取得します。
- [**Quiz Reports**](https://canvas.instructure.com/doc/api/quiz_reports.html)：クラス全体のパフォーマンスを分析し、時間の経過とともに進歩を追跡するためのさまざまなレポートを生成・表示します。

### 採点済み課題のレビューと改善ガイダンス

**ユースケース：** 学生が採点済みの課題をレビューし、パフォーマンスを分析し、知識のギャップがある分野での改善方法について的確なガイダンスを受けるためのツールを提供します。このツールは、学生が苦労した特定の質問やセクションを強調し、改善に役立つ追加のリソースや練習教材を提案できます。

**APIリソース：**

- [**Submissions**](https://canvas.instructure.com/doc/api/submissions.html)と[**Quiz Submissions**](https://canvas.instructure.com/doc/api/quiz_submissions.html)：学生の提出物と関連する成績を取得します。
- [**Assignments**](https://canvas.instructure.com/doc/api/assignments.html)：ルーブリックと採点基準を含む課題の詳細情報を取得します。
- [**Rubric Assessments**](https://canvas.instructure.com/doc/api/rubrics.html)：詳細なフィードバックとルーブリック評価にアクセスします
- [**Modules**](https://canvas.instructure.com/doc/api/modules.html)：List modules APIを使用して学生の弱点分野をターゲットとした追加の学習モジュールを提案します。
- [**Quizzes**](https://canvas.instructure.com/doc/api/quizzes.html)：特定の知識ギャップの改善に役立つ練習クイズを推奨します

# おめでとうございます！

Canvas LMSを使用して動作するカスタムアクション付きのカスタムGPTの作成に成功しました。以下のスクリーンショットに似た会話ができるはずです。素晴らしい仕事です。頑張り続けてください！

![canvas_lms_sample_conversation.png](../../../images/canvas_lms_sample_conversation.png)