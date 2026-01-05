# GPT Action Library: GitHub

## はじめに

このページでは、GPT ActionをGitHubに接続する開発者向けの手順を提供します。進める前に、以下のリソースに慣れ親しんでください：
- [GPT Actionsの紹介](https://platform.openai.com/docs/actions)
- [GPT Actions Library](https://platform.openai.com/docs/actions/actions-library)
- [GPT Actionをゼロから構築する](https://platform.openai.com/docs/actions/getting-started)

このGPT Actionは、開発者がGitHub Pull Request diffの品質とセキュリティを評価するのに役立ちます。各ドメインに対してフィードバックと提案を提供し、開発者がフィードバックを修正または承認してから、Pull Requestにコメントとして自動的に送信することができます。

## 価値と例となるビジネスユースケース

### **価値**：
ユーザーはChatGPTの自然言語機能を活用して、GitHub Pull Requestレビューを支援できます。

- **開発者向け**：コード変更を分析し、提案された修正に対する即座のフィードバックで高品質なレビューを実行できます。
- **組織向け**：diffがベストプラクティスとコーディング標準に準拠していることを確保し、またはリファクタリングされた代替案を自動的に提案します（ベストプラクティスを定義するために追加のAPIリクエストが必要な場合があります）。
- **全体的に**：このAI搭載のコードレビューアシスタントで生産性を向上させ、より高品質で安全なコードを確保できます。

### **例となるユースケース**：
- レビュアーが提案されたコード変更の品質とセキュリティに関するフィードバックを求める場合。
- 組織がコードレビュー中にベストプラクティスと標準への準拠を自動的に促進する場合。

## デモンストレーション動画：
[![動画を見る](https://img.youtube.com/vi/bcjybCh-x-Q/0.jpg)](https://www.youtube.com/watch?v=bcjybCh-x-Q)

## アプリケーション情報

### **主要リンク**
開始前に、これらのリソースを確認してください：
- [GitHub](https://github.com)
- [GitHub API Documentation](https://docs.github.com/en/rest/pulls?apiVersion=2022-11-28)

### **前提条件**
オープンなプルリクエストがあるリポジトリを持っていることを確認してください。

## アプリケーションセットアップ

### **Pull Requestの選択**
1. リポジトリに移動します。例：[example PR](https://github.com/microsoft/vscode/pull/229241)。
   - オーナー（例：「microsoft」）、リポジトリ名（例：「vscode」）、PR番号（例：「229241」）をメモしてください。
   - リポジトリオーナーがSSO組織の場合、トークンに[承認](https://docs.github.com/en/organizations/managing-programmatic-access-to-your-organization/managing-requests-for-personal-access-tokens-in-your-organization#managing-fine-grained-personal-access-token-requests)が必要な場合があります。
2. [高品質なコードレビューの実行方法](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/getting-started/best-practices-for-pull-requests)を確認してください。

### **「Fine Grained」GitHub Personal Access Tokenの生成**
1. GitHubにログインし、**Settings**に移動します。
2. **Developer settings** > **Fine Grained Personal access tokens**に移動します。
3. **Generate new token**をクリックし、名前を付け、有効期限を設定し、必要なスコープ（例：`read:content`、`read&write:pull_requests`）を選択します。
4. トークンをコピーして安全に保存します。

## ChatGPTの手順

### **カスタムGPTの指示**

カスタムGPTを作成したら、以下を指示パネルにコピーしてください：

```
# **コンテキスト：** あなたはソフトウェア開発者をサポートし、GitHubでホストされているリポジトリからのプルリクエストdiffコンテンツに関する詳細情報を提供します。既知のベストプラクティスに基づいてコード変更に関する簡潔なフィードバックを提供することで、プルリクエストの品質、セキュリティ、完全性の影響を理解するのを支援します。開発者はフィードバック（場合によっては修正を加えて）をPull Requestに投稿することを選択できます。開発者はソフトウェア開発に精通していると仮定してください。

# **指示：**

## シナリオ
### - ユーザーが特定のプルリクエストに関する情報を求める場合、この5段階のプロセスに従ってください：
1. まだ持っていない場合は、ユーザーに支援を求めるプルリクエストのオーナー、リポジトリ、プルリクエスト番号、および特定の焦点領域（例：コードパフォーマンス、セキュリティ脆弱性、ベストプラクティス）を指定するよう求めます。
2. 提供されたオーナー、リポジトリ、プルリクエスト番号を使用して、getPullRequestDiff API呼び出しを使ってGitHubからPull Request情報を取得します。
3. プルリクエストdiffの要約を4文以内で提供し、特定の焦点領域（例：コードパフォーマンス、セキュリティ脆弱性、ベストプラクティス）について該当する場合は改善提案を行います。
4. ユーザーにフィードバックをコメントとして投稿するか、投稿前に修正するかを尋ねます。ユーザーがフィードバックを修正する場合は、そのフィードバックを組み込んでこのステップを繰り返します。
5. ユーザーがフィードバックをPull Requestへのコメントとして投稿することを確認した場合、postPullRequestComment APIを使用してプルリクエストにフィードバックをコメントします。
```

### OpenAPIスキーマ

カスタムGPTを作成したら、以下のテキストをActionsパネルにコピーしてください。質問がありますか？この手順の詳細については[Getting Started Example](https://platform.openai.com/docs/actions/getting-started)をご確認ください。

以下は、GitHubに接続してPull Request DiffをGETし、Pull RequestにフィードバックをPOSTする例です。

```javascript
openapi: 3.1.0
info:
  title: GitHub Pull Request API
  description: Retrieve the diff of a pull request and post comments back to it.
  version: 1.0.0
servers:
  - url: https://api.github.com
    description: GitHub API
paths:
  /repos/{owner}/{repo}/pulls/{pull_number}:
    get:
      operationId: getPullRequestDiff
      summary: Get the diff of a pull request.
      parameters:
        - name: owner
          in: path
          required: true
          schema:
            type: string
          description: Owner of the repository.
        - name: repo
          in: path
          required: true
          schema:
            type: string
          description: Name of the repository.
        - name: pull_number
          in: path
          required: true
          schema:
            type: integer
          description: The number of the pull request.
        - name: Accept
          in: header
          required: true
          schema:
            type: string
            enum:
              - application/vnd.github.v3.diff
          description: Media type for the diff format.
      responses:
        "200":
          description: Successfully retrieved the pull request diff.
          content:
            text/plain:
              schema:
                type: string
        "404":
          description: Pull request not found.
  /repos/{owner}/{repo}/issues/{issue_number}/comments:
    post:
      operationId: postPullRequestComment
      summary: Post a comment to the pull request.
      parameters:
        - name: owner
          in: path
          required: true
          schema:
            type: string
          description: Owner of the repository.
        - name: repo
          in: path
          required: true
          schema:
            type: string
          description: Name of the repository.
        - name: issue_number
          in: path
          required: true
          schema:
            type: integer
          description: The issue or pull request number.
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              properties:
                body:
                  type: string
                  description: The content of the comment.
      responses:
        "201":
          description: Successfully created a comment.
          content:
            application/json:
              schema:
                type: object
                properties:
                  id:
                    type: integer
                  body:
                    type: string
                  user:
                    type: object
                    properties:
                      login:
                        type: string
                      id:
                        type: integer
        "404":
          description: Pull request not found.
```

## 認証手順

以下は、このサードパーティアプリケーションとの認証設定手順です。質問がありますか？この手順の詳細については[Getting Started Example](https://platform.openai.com/docs/actions/getting-started)をご確認ください。

### ChatGPTでの設定（Getting Started Exampleのステップ2を参照）

ChatGPTで「Authentication」をクリックし、**「Bearer」**を選択します。以下の情報を入力してください。トークンが上記のアプリケーションセットアップで説明された権限を持っていることを確認してください。

- Authentication Type: API Key
- Auth Type: Bearer
- API Key 
  <personal_access_token>

### GPTのテスト

これでGPTをテストする準備が整いました。「Can you review my pull request? owner: <org_name>, repo: <repo_name>, pull request number: <PR_Number>」のような簡単なプロンプトを入力すると、以下のような結果が期待できます：

![landing_page.png](../../../../images/landing_page.png)

1. 参照されたプルリクエスト（PR）の変更の要約。

![First Interaction](../../../images/first_interaction.png)

2. 品質とセキュリティのフィードバック、およびPRの次のイテレーションに組み込む提案。

![First Feedback](../../../images/first_feedback.png)

3. フィードバックを反復するか、それを受け入れてGPTにあなたからのコメントとしてPRに直接投稿させるオプション。

![First Interaction](../../../images/final_result.png)

*優先してほしい統合はありますか？統合にエラーはありますか？GitHubでPRまたはissueを提出していただければ、確認いたします。*