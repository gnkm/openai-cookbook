# GitHub Pull Requestにおけるコード品質とセキュリティの推論

## はじめに
このガイドでは、OpenAI推論モデルをGitHub Pull Request（PR）ワークフローに統合し、コードの品質、セキュリティ、および企業標準への準拠を自動的にレビューする方法について説明します。開発プロセスの早期段階でAI駆動のインサイトを活用することで、問題をより早期に発見し、手動作業を削減し、コードベース全体で一貫したベストプラクティスを維持できます。

## なぜPRにOpenAI推論モデルを統合するのか？
• コードの臭い、セキュリティ脆弱性、スタイルの不整合を自動検出することで、コードレビュー時間を節約  
• 組織全体で一貫した信頼性の高いコードのためのコーディング標準を強制  
• 開発者に潜在的な改善点について迅速なAIガイド付きフィードバックを提供

## 使用例
• レビュアーがマージ前に新しいコード変更のセキュリティについてフィードバックを求める場合  
• チームが標準的なコーディングガイドラインを強制し、組織全体で一貫したコード品質を確保したい場合

## 前提条件

### 1. OpenAI「プロジェクトキー」の生成
1. platform.openai.com/api-keysにアクセスし、新しいシークレットキーを作成する  
2. トークンをGitHubリポジトリシークレットに`OPENAI_API_KEY`として安全に保存する

### 2. OpenAIモデルの選択
コード変更の詳細な分析には[OpenAI推論モデル](https://platform.openai.com/docs/guides/reasoning)を使用します。最も高度なモデルから始めて、必要に応じてプロンプトを調整してください。

### 3. Pull Requestの選択
1. リポジトリでGitHub Actionsが有効になっていることを確認  
2. リポジトリシークレットや変数（例：`PROMPT`、`MODELNAME`、`BEST_PRACTICES`変数）を設定する権限があることを確認

### 4. 企業コーディング標準の定義
標準をリポジトリ変数（`BEST_PRACTICES`）として保存します。これには以下が含まれる場合があります：  
• コードスタイルとフォーマット  
• 可読性と保守性  
• セキュリティとコンプライアンス  
• エラーハンドリングとログ記録  
• パフォーマンスとスケーラビリティ  
• テストとQA  
• ドキュメントとバージョン管理  
• アクセシビリティと国際化

### 5. プロンプト内容の定義
セキュリティ、品質、ベストプラクティスチェックに向けてOpenAIをガイドするメタプロンプトを構築します。以下を含めてください：  
1. コード品質と標準  
2. セキュリティと脆弱性分析  
3. 障害許容性とエラーハンドリング  
4. パフォーマンスとリソース管理  
5. ステップバイステップ検証

OpenAIに明示的な推奨事項を含む徹底的な行ごとのレビューを提供するよう促してください。

## GitHub Actionsワークフローの作成

このGitHub Actionsワークフローは、mainブランチに対するすべてのpull requestでトリガーされ、2つのジョブで構成されています。最初のジョブは、変更されたすべてのファイル（.jsonと.pngファイルを除く）の差分を収集し、これらの変更をOpenAIに送信して分析します。OpenAIからの修正提案はPRのコメントに含まれます。2番目のジョブは、定義された企業標準に対してPRを評価し、コードがそれらの標準にどの程度準拠しているかを要約するマークダウンテーブルを返します。プロンプト、モデル名、ベストプラクティスなどの変数を更新することで、ワークフローを簡単に調整または改良できます。

```yaml
name: PR Quality and Security Check

on:
  pull_request:
    branches: [main]

permissions:
  contents: read
  pull-requests: write

jobs:
  quality-security-analysis:
    runs-on: ubuntu-latest
    steps:
      - name: Check out code
        uses: actions/checkout@v3
        with:
          fetch-depth: 0  # Ensure full history for proper diff

      - name: Gather Full Code From Changed Files
        run: |
          CHANGED_FILES=$(git diff --name-only origin/main...HEAD)
          echo '{"original files": [' > original_files_temp.json
          for file in $CHANGED_FILES; do
            if [[ $file == *.json ]] || [[ $file == *.png ]]; then
              continue
            fi
            if [ -f "$file" ]; then
              CONTENT=$(jq -Rs . < "$file")
              echo "{\"filename\": \"$file\", \"content\": $CONTENT}," >> original_files_temp.json
            fi
          done
          sed -i '$ s/,$//' original_files_temp.json
          echo "]}" >> original_files_temp.json

      - name: Display Processed Diff (Debug)
        run: cat original_files_temp.json

      - name: Get Diff
        run: |
          git diff origin/main...HEAD \
            | grep '^[+-]' \
            | grep -Ev '^(---|\+\+\+)' > code_changes_only.txt
          jq -Rs '{diff: .}' code_changes_only.txt > diff.json
          if [ -f original_files_temp.json ]; then
            jq -s '.[0] * .[1]' diff.json original_files_temp.json > combined.json
            mv combined.json diff.json

      - name: Display Processed Diff (Debug)
        run: cat diff.json

      - name: Analyze with OpenAI
        env:
          OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
        run: |
          DIFF_CONTENT=$(jq -r '.diff' diff.json)
          ORIGINAL_FILES=$(jq -r '."original files"' diff.json)
          PROMPT="Please review the following code changes for any obvious quality or security issues. Provide a brief report in markdown format:\n\nDIFF:\n${DIFF_CONTENT}\n\nORIGINAL FILES:\n${ORIGINAL_FILES}"
          jq -n --arg prompt "$PROMPT" '{
            "model": "gpt-4",
            "messages": [
              { "role": "system", "content": "You are a code reviewer." },
              { "role": "user", "content": $prompt }
            ]
          }' > request.json
          curl -sS https://api.openai.com/v1/chat/completions \
            -H "Content-Type: application/json" \
            -H "Authorization: Bearer ${OPENAI_API_KEY}" \
            -d @request.json > response.json

      - name: Extract Review Message
        id: extract_message
        run: |
          ASSISTANT_MSG=$(jq -r '.choices[0].message.content' response.json)
          {
            echo "message<<EOF"
            echo "$ASSISTANT_MSG"
            echo "EOF"
          } >> $GITHUB_OUTPUT

      - name: Post Comment to PR
        env:
          COMMENT: ${{ steps.extract_message.outputs.message }}
          GH_TOKEN: ${{ github.token }}
        run: |
          gh api \
            repos/${{ github.repository }}/issues/${{ github.event.pull_request.number }}/comments \
            -f body="$COMMENT"
  enterprise-standard-check:
    runs-on: ubuntu-latest
    needs: [quality-security-analysis]

    steps:
      - name: Checkout code
        uses: actions/checkout@v3
        with:
          fetch-depth: 0  # ensures we get both PR base and head

      - name: Gather Full Code From Changed Files
        run: |
          # Identify changed files from the base (origin/main) to the pull request HEAD
          CHANGED_FILES=$(git diff --name-only origin/main...HEAD)

          # Build a JSON array containing filenames and their content
          echo '{"original files": [' > original_files_temp.json
          for file in $CHANGED_FILES; do
            # Skip .json and .txt files
            if [[ $file == *.json ]] || [[ $file == *.txt ]]; then
              continue
            fi

            # If the file still exists (i.e., wasn't deleted)
            if [ -f "$file" ]; then
              CONTENT=$(jq -Rs . < "$file")
              echo "{\"filename\": \"$file\", \"content\": $CONTENT}," >> original_files_temp.json
            fi
          done

          # Remove trailing comma on the last file entry and close JSON
          sed -i '$ s/,$//' original_files_temp.json
          echo "]}" >> original_files_temp.json

      - name: Analyze Code Against Best Practices
        id: validate
        env:
          OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
        run: |
          set -e
          # Read captured code
          ORIGINAL_FILES=$(cat original_files_temp.json)

          # Construct the prompt:
          #  - Summarize each best-practice category
          #  - Provide a rating for each category: 'extraordinary', 'acceptable', or 'poor'
          #  - Return a Markdown table titled 'Enterprise Standards'
          PROMPT="You are an Enterprise Code Assistant. Review each code snippet below for its adherence to the following categories: 
          1) Code Style & Formatting
          2) Security & Compliance
          3) Error Handling & Logging
          4) Readability & Maintainability
          5) Performance & Scalability
          6) Testing & Quality Assurance
          7) Documentation & Version Control
          8) Accessibility & Internationalization

          Using \${{ vars.BEST_PRACTICES }} as a reference, assign a rating of 'extraordinary', 'acceptable', or 'poor' for each category. Return a markdown table titled 'Enterprise Standards' with rows for each category and columns for 'Category' and 'Rating'. 

          Here are the changed file contents to analyze:
          $ORIGINAL_FILES"

          # Create JSON request for OpenAI
          jq -n --arg system_content "You are an Enterprise Code Assistant ensuring the code follows best practices." \
                --arg user_content "$PROMPT" \
          '{
            "model": "${{ vars.MODELNAME }}",
            "messages": [
              {
                "role": "system",
                "content": $system_content
              },
              {
                "role": "user",
                "content": $user_content
              }
            ]
          }' > request.json

          # Make the API call
          curl -sS https://api.openai.com/v1/chat/completions \
            -H "Content-Type: application/json" \
            -H "Authorization: Bearer $OPENAI_API_KEY" \
            -d @request.json > response.json

          # Extract the model's message
          ASSISTANT_MSG=$(jq -r '.choices[0].message.content' response.json)

          # Store for next step
          {
            echo "review<<EOF"
            echo "$ASSISTANT_MSG"
            echo "EOF"
          } >> $GITHUB_OUTPUT

      - name: Post Table Comment
        env:
          COMMENT: ${{ steps.validate.outputs.review }}
          GH_TOKEN: ${{ github.token }}
        run: |
          # If COMMENT is empty or null, skip posting
          if [ -z "$COMMENT" ] || [ "$COMMENT" = "null" ]; then
            echo "No comment to post."
            exit 0
          fi

          gh api \
            repos/${{ github.repository }}/issues/${{ github.event.pull_request.number }}/comments \
            -f body="$COMMENT"
```

## ワークフローのテスト
このワークフローをリポジトリにコミットし、新しいPRを開いてください。ワークフローが自動的に実行され、AI生成のフィードバックがPRコメントとして投稿されます。

*公開例については、OpenAI-Forumリポジトリのワークフローを参照してください：[pr_quality_and_security_check.yml](https://github.com/alwell-kevin/OpenAI-Forum/blob/main/.github/workflows/pr_quality_and_security_check.yml)*

![pr_quality_and_security_check.png](../../images/pr_quality_and_security_check.png)

![workflow_check.png](../../images/workflow_check.png)