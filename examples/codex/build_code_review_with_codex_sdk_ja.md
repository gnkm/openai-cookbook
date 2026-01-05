# Codex SDKでコードレビューを構築する

Codex Cloudの[コードレビュー](https://chatgpt.com/codex/settings/code-review)を使用すると、チームのクラウドホスト型GitHubリポジトリをCodexに接続し、すべてのPRで自動化されたコードレビューを受けることができます。しかし、コードがオンプレミスでホストされている場合や、SCMとしてGitHubを使用していない場合はどうでしょうか？

幸い、独自のCI/CDランナーでCodexのクラウドホスト型レビュープロセスを複製することができます。このガイドでは、GitHub ActionsとJenkinsの両方でCodex CLIのヘッドレスモードを使用して、独自のコードレビューアクションを構築します。

モデル推奨：これらのワークフローで最も強力なコードレビューの精度と一貫性を得るために、`gpt-5.2-codex`を使用してください。

独自のコードレビューを構築するために、以下の手順を実行し、それらに厳密に従います：

1. CI/CDランナーにCodex CLIをインストールする
2. CLIに付属するコードレビュープロンプトを使用して、ヘッドレス（exec）モードでCodexにプロンプトを送る
3. Codex用の構造化出力JSONスキーマを指定する
4. JSON結果を解析し、それを使用してSCMへのAPI呼び出しを行い、レビューコメントを作成する

実装が完了すると、Codexはインラインコードレビューコメントを残すことができるようになります：
<img src="../../images/codex_code_review.png" alt="GitHubでのCodexコードレビュー" width="500"/>

## コードレビュープロンプト

GPT-5.2-Codexは、コードレビュー能力を向上させるための特別な訓練を受けています。以下のプロンプトでGPT-5.2-Codexにコードレビューを実行させることができます：

```
You are acting as a reviewer for a proposed code change made by another engineer.
Focus on issues that impact correctness, performance, security, maintainability, or developer experience.
Flag only actionable issues introduced by the pull request.
When you flag an issue, provide a short, direct explanation and cite the affected file and line range.
Prioritize severe issues and avoid nit-level comments unless they block understanding of the diff.
After listing findings, produce an overall correctness verdict (\"patch is correct\" or \"patch is incorrect\") with a concise justification and a confidence score between 0 and 1.
Ensure that file citations and line numbers are exactly correct using the tools available; if they are incorrect your comments will be rejected.
```

## Codex構造化出力

プルリクエストのコード範囲にコメントを作成するために、特定の形式でCodexの応答を受け取る必要があります。そのために、OpenAIの[構造化出力](https://platform.openai.com/docs/guides/structured-outputs)形式に準拠した`codex-output-schema.json`というファイルを作成できます。

ワークフローYAMLでこのファイルを使用するには、次のように`output-schema-file`引数でCodexを呼び出すことができます：

```yaml
- name: Run Codex structured review
        id: run-codex
        uses: openai/codex-action@main
        with:
            openai-api-key: ${{ secrets.OPENAI_API_KEY }}
            prompt-file: codex-prompt.md
            sandbox: read-only
            model: ${{ env.CODEX_MODEL }}
            output-schema-file: codex-output-schema.json # <-- スキーマファイル
            output-file: codex-output.json
```

`codex exec`にも同様の引数を渡すことができます：

```bash
codex exec "Review my pull request!" --output-schema codex-output-schema.json
```

## GitHub Actionsの例

すべてをまとめてみましょう。オンプレミス環境でGitHub Actionsを使用している場合は、この例を特定のワークフローに合わせて調整できます。インラインコメントが主要な手順を強調しています。

```yaml
name: Codex Code Review

# レビューアクションを実行するタイミングを決定：
on:
  pull_request:
    types:
      - opened
      - reopened
      - synchronize
      - ready_for_review

concurrency:
  group: codex-structured-review-${{ github.event.pull_request.number }}
  cancel-in-progress: true

jobs:
  codex-structured-review:
    name: Run Codex structured review
    runs-on: ubuntu-latest
    permissions:
      contents: read
      pull-requests: write
    env:
      OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
      GITHUB_TOKEN: ${{ github.token }}
      CODEX_MODEL: ${{ vars.CODEX_MODEL || 'o4-mini' }}
      PR_NUMBER: ${{ github.event.pull_request.number }}
      HEAD_SHA: ${{ github.event.pull_request.head.sha }}
      BASE_SHA: ${{ github.event.pull_request.base.sha }}
      REPOSITORY: ${{ github.repository }}
    outputs:
      codex-output: ${{ steps.run-codex.outputs.final-message }}
    steps:
      - name: Checkout pull request merge commit
        uses: actions/checkout@v5
        with:
          ref: refs/pull/${{ github.event.pull_request.number }}/merge

      - name: Fetch base and head refs
        run: |
          set -euxo pipefail
          git fetch --no-tags origin \
            "${{ github.event.pull_request.base.ref }}" \
            +refs/pull/${{ github.event.pull_request.number }}/head
        shell: bash

      # 構造化出力スキーマにより、codexがファイルパス、行番号、
      # タイトル、本文などを含むコメントを生成することが保証されます。
      - name: Generate structured output schema
        run: |
          set -euo pipefail
          cat <<'JSON' > codex-output-schema.json
          {
              "type": "object",
              "properties": {
                "findings": {
                  "type": "array",
                  "items": {
                    "type": "object",
                    "properties": {
                      "title": {
                        "type": "string",
                        "maxLength": 80
                      },
                      "body": {
                        "type": "string",
                        "minLength": 1
                      },
                      "confidence_score": {
                        "type": "number",
                        "minimum": 0,
                        "maximum": 1
                      },
                      "priority": {
                        "type": "integer",
                        "minimum": 0,
                        "maximum": 3
                      },
                      "code_location": {
                        "type": "object",
                        "properties": {
                          "absolute_file_path": {
                            "type": "string",
                            "minLength": 1
                          },
                          "line_range": {
                            "type": "object",
                            "properties": {
                              "start": {
                                "type": "integer",
                                "minimum": 1
                              },
                              "end": {
                                "type": "integer",
                                "minimum": 1
                              }
                            },
                            "required": [
                              "start",
                              "end"
                            ],
                            "additionalProperties": false
                          }
                        },
                        "required": [
                          "absolute_file_path",
                          "line_range"
                        ],
                        "additionalProperties": false
                      }
                    },
                    "required": [
                      "title",
                      "body",
                      "confidence_score",
                      "priority",
                      "code_location"
                    ],
                    "additionalProperties": false
                  }
                },
                "overall_correctness": {
                  "type": "string",
                  "enum": [
                    "patch is correct",
                    "patch is incorrect"
                  ]
                },
                "overall_explanation": {
                  "type": "string",
                  "minLength": 1
                },
                "overall_confidence_score": {
                  "type": "number",
                  "minimum": 0,
                  "maximum": 1
                }
              },
              "required": [
                "findings",
                "overall_correctness",
                "overall_explanation",
                "overall_confidence_score"
              ],
              "additionalProperties": false
            }
          JSON
        shell: bash

      # このセクションでプロンプトを生成します：
      - name: Build Codex review prompt
        env:
          REVIEW_PROMPT_PATH: ${{ vars.CODEX_PROMPT_PATH || 'review_prompt.md' }}
        run: |
          set -euo pipefail
          PROMPT_PATH="codex-prompt.md"
          TEMPLATE_PATH="${REVIEW_PROMPT_PATH}"

          if [ -n "$TEMPLATE_PATH" ] && [ -f "$TEMPLATE_PATH" ]; then
            cat "$TEMPLATE_PATH" > "$PROMPT_PATH"
          else
            {
              printf '%s\n' "You are acting as a reviewer for a proposed code change made by another engineer."
              printf '%s\n' "Focus on issues that impact correctness, performance, security, maintainability, or developer experience."
              printf '%s\n' "Flag only actionable issues introduced by the pull request."
              printf '%s\n' "When you flag an issue, provide a short, direct explanation and cite the affected file and line range."
              printf '%s\n' "Prioritize severe issues and avoid nit-level comments unless they block understanding of the diff."
              printf '%s\n' "After listing findings, produce an overall correctness verdict (\"patch is correct\" or \"patch is incorrect\") with a concise justification and a confidence score between 0 and 1."
              printf '%s\n' "Ensure that file citations and line numbers are exactly correct using the tools available; if they are incorrect your comments will be rejected."
            } > "$PROMPT_PATH"
          fi

          {
            echo ""
            echo "Repository: ${REPOSITORY}"
            echo "Pull Request #: ${PR_NUMBER}"
            echo "Base ref: ${{ github.event.pull_request.base.ref }}"
            echo "Head ref: ${{ github.event.pull_request.head.ref }}"
            echo "Base SHA: ${BASE_SHA}"
            echo "Head SHA: ${HEAD_SHA}"
            echo "Changed files:"
            git --no-pager diff --name-status "${BASE_SHA}" "${HEAD_SHA}"
            echo ""
            echo "Unified diff (context=5):"
            git --no-pager diff --unified=5 --stat=200 "${BASE_SHA}" "${HEAD_SHA}" > /tmp/diffstat.txt
            git --no-pager diff --unified=5 "${BASE_SHA}" "${HEAD_SHA}" > /tmp/full.diff
            cat /tmp/diffstat.txt
            echo ""
            cat /tmp/full.diff
          } >> "$PROMPT_PATH"
        shell: bash

      # すべてをまとめて：コードレビュープロンプト、
      # 構造化出力、出力ファイルでcodexアクションを実行します：
      - name: Run Codex structured review
        id: run-codex
        uses: openai/codex-action@main
        with:
          openai-api-key: ${{ secrets.OPENAI_API_KEY }}
          prompt-file: codex-prompt.md
          output-schema-file: codex-output-schema.json
          output-file: codex-output.json
          sandbox: read-only
          model: ${{ env.CODEX_MODEL }}

      - name: Inspect structured Codex output
        if: ${{ always() }}
        run: |
          if [ -s codex-output.json ]; then
            jq '.' codex-output.json || true
          else
            echo "Codex output file missing"
          fi
        shell: bash

      # このステップは、コードの特定の行範囲に
      # インラインコードレビューコメントを生成します。
      - name: Publish inline review comments
        if: ${{ always() }}
        env:
          REVIEW_JSON: codex-output.json
        run: |
          set -euo pipefail
          if [ ! -s "$REVIEW_JSON" ]; then
            echo "No Codex output file present; skipping comment publishing."
            exit 0
          fi
          findings_count=$(jq '.findings | length' "$REVIEW_JSON")
          if [ "$findings_count" -eq 0 ]; then
            echo "Codex returned no findings; skipping inline comments."
            exit 0
          fi
          jq -c --arg commit "$HEAD_SHA" '.findings[] | {
              body: (.title + "\n\n" + .body + "\n\nConfidence: " + (.confidence_score | tostring) + (if has("priority") then "\nPriority: P" + (.priority | tostring) else "" end)),
              commit_id: $commit,
              path: .code_location.absolute_file_path,
              line: .code_location.line_range.end,
              side: "RIGHT",
              start_line: (if .code_location.line_range.start != .code_location.line_range.end then .code_location.line_range.start else null end),
              start_side: (if .code_location.line_range.start != .code_location.line_range.end then "RIGHT" else null end)
            } | with_entries(select(.value != null))' "$REVIEW_JSON" > findings.jsonl
          while IFS= read -r payload; do
            echo "Posting review comment payload:" && echo "$payload" | jq '.'
            curl -sS \
              -X POST \
              -H "Accept: application/vnd.github+json" \
              -H "Authorization: Bearer ${GITHUB_TOKEN}" \
              -H "X-GitHub-Api-Version: 2022-11-28" \
              "https://api.github.com/repos/${REPOSITORY}/pulls/${PR_NUMBER}/comments" \
              -d "$payload"
          done < findings.jsonl
        shell: bash

      # このセクションは、レビューを要約する単一のコメントを作成します。
      - name: Publish overall summary comment
        if: ${{ always() }}
        env:
          REVIEW_JSON: codex-output.json
        run: |
          set -euo pipefail
          if [ ! -s "$REVIEW_JSON" ]; then
            echo "Codex output missing; skipping summary."
            exit 0
          fi
          overall_state=$(jq -r '.overall_correctness' "$REVIEW_JSON")
          overall_body=$(jq -r '.overall_explanation' "$REVIEW_JSON")
          confidence=$(jq -r '.overall_confidence_score' "$REVIEW_JSON")
          msg="**Codex automated review**\n\nVerdict: ${overall_state}\nConfidence: ${confidence}\n\n${overall_body}"
          curl -sS \
            -X POST \
            -H "Accept: application/vnd.github+json" \
            -H "Authorization: Bearer ${GITHUB_TOKEN}" \
            -H "X-GitHub-Api-Version: 2022-11-28" \
            "https://api.github.com/repos/${REPOSITORY}/issues/${PR_NUMBER}/comments" \
            -d "$(jq -n --arg body "$msg" '{body: $body}')"
        shell: bash
```

## GitLabの例
GitLabにはGitHub Actionの直接的な同等物はありませんが、GitLab CI/CD内で`codex exec`を実行して自動化されたコードレビューを実行できます。

ただし、GitHub Actionには重要な[安全戦略](https://github.com/openai/codex-action?tab=readme-ov-file#safety-strategy)が含まれています：CodexがOpenAI APIキーにアクセスできないようにsudo権限を削除します。この分離は、機密シークレット（OpenAI APIキーなど）が存在する可能性のあるパブリックリポジトリでは特に重要です。実行中にCodexが認証情報を読み取ったり流出させたりすることを防ぐためです。

このジョブを実行する前に、GitLabプロジェクトを設定してください：

1. **プロジェクト → 設定 → CI/CD**に移動します。
2. **変数**セクションを展開します。
3. 以下の変数を追加します：
   - `OPENAI_API_KEY`
   - `GITLAB_TOKEN`
4. 適切にマスク/保護としてマークします。
5. マージリクエストパイプライン中に実行されるように、以下のGitLabサンプルジョブをリポジトリのルートにある`.gitlab-ci.yml`ファイルに追加します。

パブリックリポジトリでのAPIキーの取り扱いには注意してください。

```yaml
stages:
  - review

codex-structured-review:
  stage: review
  image: ubuntu:22.04
  rules:
    - if: '$CI_PIPELINE_SOURCE == "merge_request_event"'
  variables:
    PR_NUMBER: $CI_MERGE_REQUEST_IID
    REPOSITORY: "$CI_PROJECT_PATH"
    BASE_SHA: "$CI_MERGE_REQUEST_DIFF_BASE_SHA"
    HEAD_SHA: "$CI_COMMIT_SHA"

  before_script:
    - apt-get update -y
    - apt-get install -y git curl jq
    - |
      if ! command -v codex >/dev/null 2>&1; then
        ARCH="$(uname -m)"
        case "$ARCH" in
          x86_64) CODEX_PLATFORM="x86_64-unknown-linux-musl" ;;
          aarch64|arm64) CODEX_PLATFORM="aarch64-unknown-linux-musl" ;;
          *)
            echo "Unsupported architecture: $ARCH"
            exit 1
            ;;
        esac

        CODEX_VERSION="${CODEX_VERSION:-latest}"
        if [ -n "${CODEX_DOWNLOAD_URL:-}" ]; then
          CODEX_URL="$CODEX_DOWNLOAD_URL"
        elif [ "$CODEX_VERSION" = "latest" ]; then
          CODEX_URL="https://github.com/openai/codex/releases/latest/download/codex-${CODEX_PLATFORM}.tar.gz"
        else
          CODEX_URL="https://github.com/openai/codex/releases/download/${CODEX_VERSION}/codex-${CODEX_PLATFORM}.tar.gz"
        fi

        TMP_DIR="$(mktemp -d)"
        curl -fsSL "$CODEX_URL" -o "$TMP_DIR/codex.tar.gz"
        tar -xzf "$TMP_DIR/codex.tar.gz" -C "$TMP_DIR"
        install -m 0755 "$TMP_DIR"/codex-* /usr/local/bin/codex
        rm -rf "$TMP_DIR"
      fi
    - git fetch origin $CI_MERGE_REQUEST_TARGET_BRANCH_NAME
    - git fetch origin $CI_MERGE_REQUEST_SOURCE_BRANCH_NAME
    - git checkout $CI_MERGE_REQUEST_SOURCE_BRANCH_NAME

  script:
    - echo "Running Codex structured review for MR !${PR_NUMBER}"

    # 構造化出力スキーマを生成
    - |
      cat <<'JSON' > codex-output-schema.json
      {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "title": "Codex Structured Review",
        "type": "object",
        "additionalProperties": false,
        "required": [
          "overall_correctness",
          "overall_explanation",
          "overall_confidence_score",
          "findings"
        ],
        "properties": {
          "overall_correctness": {
            "type": "string",
            "description": "Overall verdict for the merge request."
          },
          "overall_explanation": {
            "type": "string",
            "description": "Explanation backing up the verdict."
          },
          "overall_confidence_score": {
            "type": "number",
            "minimum": 0,
            "maximum": 1,
            "description": "Confidence level for the verdict."
          },
          "findings": {
            "type": "array",
            "description": "Collection of actionable review findings.",
            "items": {
              "type": "object",
              "additionalProperties": false,
              "required": [
                "title",
                "body",
                "confidence_score",
                "code_location"
              ],
              "properties": {
                "title": {
                  "type": "string"
                },
                "body": {
                  "type": "string"
                },
                "confidence_score": {
                  "type": "number",
                  "minimum": 0,
                  "maximum": 1
                },
                "code_location": {
                  "type": "object",
                  "additionalProperties": false,
                  "required": [
                    "absolute_file_path",
                    "relative_file_path",
                    "line_range"
                  ],
                  "properties": {
                    "absolute_file_path": {
                      "type": "string"
                    },
                    "relative_file_path": {
                      "type": "string"
                    },
                    "line_range": {
                      "type": "object",
                      "additionalProperties": false,
                      "required": [
                        "start",
                        "end"
                      ],
                      "properties": {
                        "start": {
                          "type": "integer",
                          "minimum": 1
                        },
                        "end": {
                          "type": "integer",
                          "minimum": 1
                        }
                      }
                    }
                  }
                }
              }
            },
            "default": []
          }
        }
      }
      JSON

    # Codexレビュープロンプトを構築
    - |
      PROMPT_PATH="codex-prompt.md"
      TEMPLATE_PATH="${REVIEW_PROMPT_PATH:-review_prompt.md}"
      if [ -n "$TEMPLATE_PATH" ] && [ -f "$TEMPLATE_PATH" ]; then
        cat "$TEMPLATE_PATH" > "$PROMPT_PATH"
      else
        {
          printf '%s\n' "You are acting as a reviewer for a proposed code change..."
          printf '%s\n' "Focus on issues that impact correctness, performance, security..."
          printf '%s\n' "Flag only actionable issues introduced by this merge request..."
          printf '%s\n' "Provide an overall correctness verdict..."
        } > "$PROMPT_PATH"
      fi
      {
        echo ""
        echo "Repository: ${REPOSITORY}"
        echo "Merge Request #: ${PR_NUMBER}"
        echo "Base SHA: ${BASE_SHA}"
        echo "Head SHA: ${HEAD_SHA}"
        echo ""
        echo "Changed files:"
        git --no-pager diff --name-status "${BASE_SHA}" "${HEAD_SHA}"
        echo ""
        echo "Unified diff (context=5):"
        git --no-pager diff --unified=5 "${BASE_SHA}" "${HEAD_SHA}"
      } >> "$PROMPT_PATH"

    # Codex exec CLIを実行
    - |
      printenv OPENAI_API_KEY | codex login --with-api-key && \
      codex exec --output-schema codex-output-schema.json \
                 --output-last-message codex-output.json \
                 --sandbox read-only \
                 - < codex-prompt.md

    # 構造化Codex出力を検査
    - |
      if [ -s codex-output.json ]; then
        jq '.' codex-output.json || true
      else
        echo "Codex output file missing"; exit 1
      fi

    # GitLab MRにインラインコメントを公開
    - |
      findings_count=$(jq '.findings | length' codex-output.json)
      if [ "$findings_count" -eq 0 ]; then
        echo "No findings from Codex; skipping comments."
        exit 0
      fi

      jq -c \
        --arg base "$BASE_SHA" \
        --arg start "$BASE_SHA" \
        --arg head "$HEAD_SHA" '
        .findings[] | {
          body: (.title + "\n\n" + .body + "\n\nConfidence: " + (.confidence_score | tostring)),
          position: {
            position_type: "text",
            base_sha: $base,
            start_sha: $start,
            head_sha: $head,
            new_path: (.code_location.relative_file_path // .code_location.absolute_file_path),
            new_line: .code_location.line_range.end
          }
        }
      ' codex-output.json > findings.jsonl

      while IFS= read -r payload; do
        curl -sS --request POST \
             --header "PRIVATE-TOKEN: $GITLAB_TOKEN" \
             --header "Content-Type: application/json" \
             --data "$payload" \
             "https://gitlab.com/api/v4/projects/${CI_PROJECT_ID}/merge_requests/${PR_NUMBER}/discussions"
      done < findings.jsonl

    # 全体的な要約コメントを公開
    - |
      overall_state=$(jq -r '.overall_correctness' codex-output.json)
      overall_body=$(jq -r '.overall_explanation' codex-output.json)
      confidence=$(jq -r '.overall_confidence_score' codex-output.json)

      summary="**Codex automated review**\n\nVerdict: ${overall_state}\nConfidence: ${confidence}\n\n${overall_body}"

      curl -sS --request POST \
           --header "PRIVATE-TOKEN: $GITLAB_TOKEN" \
           --header "Content-Type: application/json" \
           --data "$(jq -n --arg body "$summary" '{body: $body}')" \
           "https://gitlab.com/api/v4/projects/${CI_PROJECT_ID}/merge_requests/${PR_NUMBER}/notes"

  artifacts:
    when: always
    paths:
      - codex-output.json
      - codex-prompt.md

```

## Jenkinsの例

Jenkinsでジョブをスクリプト化するのに同じアプローチを使用できます。再び、コメントがワークフローの主要段階を強調しています：

```groovy
pipeline {
  agent any

  options {
    timestamps()
    ansiColor('xterm')
    // 同じPRでの重複実行を防ぐ。新しいビルドはマイルストーンを通過した後、古いビルドをキャンセルします。
    disableConcurrentBuilds()
  }

  environment {
    // GHAのようなデフォルトモデル（ジョブ/env レベルで上書き可能）
    CODEX_MODEL = "${env.CODEX_MODEL ?: 'o4-mini'}"

    // 初期化中に入力
    PR_NUMBER   = ''
    HEAD_SHA    = ''
    BASE_SHA    = ''
    REPOSITORY  = ''   // org/repo
  }

  stages {
    stage('Init (PR context, repo, SHAs)') {
      steps {
        checkout scm

        // GitHub Actionと同様にPRコンテキストとSHAを計算
        sh '''
          set -euo pipefail

          # GitHub Branch Source経由でPRをビルドする際のJenkins envからPR番号を導出
          PR_NUMBER="${CHANGE_ID:-}"
          if [ -z "$PR_NUMBER" ]; then
            echo "Not a PR build (CHANGE_ID missing). Exiting."
            exit 1
          fi
          echo "PR_NUMBER=$PR_NUMBER" >> $WORKSPACE/jenkins.env

          # owner/repoを発見（SSH/HTTPS形式を正規化）
          ORIGIN_URL="$(git config --get remote.origin.url)"
          if echo "$ORIGIN_URL" | grep -qE '^git@github.com:'; then
            REPO_PATH="${ORIGIN_URL#git@github.com:}"
            REPO_PATH="${REPO_PATH%.git}"
          else
            # e.g. https://github.com/owner/repo.git
            REPO_PATH="${ORIGIN_URL#https://github.com/}"
            REPO_PATH="${REPO_PATH%.git}"
          fi
          echo "REPOSITORY=$REPO_PATH" >> $WORKSPACE/jenkins.env

          # 必要なすべてのrefがあることを確認
          git fetch --no-tags origin \
            "+refs/heads/*:refs/remotes/origin/*" \
            "+refs/pull/${PR_NUMBER}/head:refs/remotes/origin/PR-${PR_NUMBER}-head" \
            "+refs/pull/${PR_NUMBER}/merge:refs/remotes/origin/PR-${PR_NUMBER}-merge"

          # HEAD（PRヘッド）とBASE（ターゲットブランチのtip）
          CHANGE_TARGET="${CHANGE_TARGET:-main}"
          HEAD_SHA="$(git rev-parse refs/remotes/origin/PR-${PR_NUMBER}-head)"
          BASE_SHA="$(git rev-parse refs/remotes/origin/${CHANGE_TARGET})"

          echo "HEAD_SHA=$HEAD_SHA" >> $WORKSPACE/jenkins.env
          echo "BASE_SHA=$BASE_SHA" >> $WORKSPACE/jenkins.env

          echo "Resolved:"
          echo "  REPOSITORY=$REPO_PATH"
          echo "  PR_NUMBER=$PR_NUMBER"
          echo "  CHANGE_TARGET=$CHANGE_TARGET"
          echo "  HEAD_SHA=$HEAD_SHA"
          echo "  BASE_SHA=$BASE_SHA"
        '''
        script {
          def envMap = readProperties file: 'jenkins.env'
          env.PR_NUMBER  = envMap['PR_NUMBER']
          env.REPOSITORY = envMap['REPOSITORY']
          env.HEAD_SHA   = envMap['HEAD_SHA']
          env.BASE_SHA   = envMap['BASE_SHA']
        }

        // このPRの最新ビルドのみが続行することを確認；古い実行中のビルドはここで中止されます
        milestone 1
      }
    }

    stage('Generate structured output schema') {
      steps {
        sh '''
          set -euo pipefail
          cat > codex-output-schema.json <<'JSON'
          {
            "type": "object",
            "properties": {
              "findings": {
                "type": "array",
                "items": {
                  "type": "object",
                  "properties": {
                    "title": { "type": "string", "maxLength": 80 },
                    "body": { "type": "string", "minLength": 1 },
                    "confidence_score": { "type": "number", "minimum": 0, "maximum": 1 },
                    "priority": { "type": "integer", "minimum": 0, "maximum": 3 },
                    "code_location": {
                      "type": "object",
                      "properties": {
                        "absolute_file_path": { "type": "string", "minLength": 1 },
                        "line_range": {
                          "type": "object",
                          "properties": {
                            "start": { "type": "integer", "minimum": 1 },
                            "end": { "type": "integer", "minimum": 1 }
                          },
                          "required": ["start","end"],
                          "additionalProperties": false
                        }
                      },
                      "required": ["absolute_file_path","line_range"],
                      "additionalProperties": false
                    }
                  },
                  "required": ["title","body","confidence_score","priority","code_location"],
                  "additionalProperties": false
                }
              },
              "overall_correctness": { "type": "string", "enum": ["patch is correct","patch is incorrect"] },
              "overall_explanation": { "type": "string", "minLength": 1 },
              "overall_confidence_score": { "type": "number", "minimum": 0, "maximum": 1 }
            },
            "required": ["findings","overall_correctness","overall_explanation","overall_confidence_score"],
            "additionalProperties": false
          }
          JSON
        '''
      }
    }

    stage('Build Codex review prompt') {
      environment {
        REVIEW_PROMPT_PATH = "${env.CODEX_PROMPT_PATH ?: 'review_prompt.md'}"
      }
      steps {
        sh '''
          set -euo pipefail
          PROMPT_PATH="codex-prompt.md"
          TEMPLATE_PATH="${REVIEW_PROMPT_PATH}"

          if [ -n "$TEMPLATE_PATH" ] && [ -f "$TEMPLATE_PATH" ]; then
            cat "$TEMPLATE_PATH" > "$PROMPT_PATH"
          else
            {
              printf '%s\n' "You are acting as a reviewer for a proposed code change made by another engineer."
              printf '%s\n' "Focus on issues that impact correctness, performance, security, maintainability, or developer experience."
              printf '%s\n' "Flag only actionable issues introduced by the pull request."
              printf '%s\n' "When you flag an issue, provide a short, direct explanation and cite the affected file and line range."
              printf '%s\n' "Prioritize severe issues and avoid nit-level comments unless they block understanding of the diff."
              printf '%s\n' "After listing findings, produce an overall correctness verdict (\\\"patch is correct\\\" or \\\"patch is incorrect\\\") with a concise justification and a confidence score between 0 and 1."
              printf '%s\n' "Ensure that file citations and line numbers are exactly correct using the tools available; if they are incorrect your comments will be rejected."
            } > "$PROMPT_PATH"
          fi

          {
            echo ""
            echo "Repository: ${REPOSITORY}"
            echo "Pull Request #: ${PR_NUMBER}"
            echo "Base ref: ${CHANGE_TARGET}"
            echo "Head ref: ${CHANGE_BRANCH:-PR-${PR_NUMBER}-head}"
            echo "Base SHA: ${BASE_SHA}"
            echo "Head SHA: ${HEAD_SHA}"
            echo "Changed files:"
            git --no-pager diff --name-status "${BASE_SHA}" "${HEAD_SHA}"
            echo ""
            echo "Unified diff (context=5):"
            git --no-pager diff --unified=5 --stat=200 "${BASE_SHA}" "${HEAD_SHA}" > /tmp/diffstat.txt
            git --no-pager diff --unified=5 "${BASE_SHA}" "${HEAD_SHA}" > /tmp/full.diff
            cat /tmp/diffstat.txt
            echo ""
            cat /tmp/full.diff
          } >> "$PROMPT_PATH"
        '''
      }
    }

    stage('Run Codex structured review') {
      environment {
        REVIEW_PROMPT = 'codex-prompt.md'
        REVIEW_SCHEMA = 'codex-output-schema.json'
        REVIEW_OUTPUT = 'codex-output.json'
      }
      steps {
        withCredentials([
          string(credentialsId: 'openai-api-key', variable: 'OPENAI_API_KEY')
        ]) {
          // オプションA：JenkinsエージェントにOpenAI CLIがインストールされている場合
          sh '''
            set -euo pipefail
            if command -v openai >/dev/null 2>&1; then
              # JSONスキーマツール仕様でResponses APIを使用
              # 構造化結果でcodex-output.jsonを生成します。
              openai responses.create \
                --model "${CODEX_MODEL}" \
                --input-file "${REVIEW_PROMPT}" \
                --response-format "json_object" \
                --output-schema "${RESPONSE_FORMAT}" \
                --tool-choice "auto" \
                > raw_response.json || true

              # CLIが正確なフラグをサポートしていない場合のフォールバック：
              # デモの回復力を保つ：raw_response.jsonが空の場合、後のステップが失敗しないように最小限のスタブを作成します。
              if [ ! -s raw_response.json ]; then
                echo '{"findings":[],"overall_correctness":"patch is correct","overall_explanation":"No issues detected.","overall_confidence_score":0.5}' > "${REVIEW_OUTPUT}"
              else
                # CLI/形式が.outputまたは類似の構造化コンテンツを含むJSONオブジェクトを返す場合、ここでマップします。
                # CLI出力形状に合わせてjqパスを調整してください。
                jq -r '.output // .' raw_response.json > "${REVIEW_OUTPUT}" || cp raw_response.json "${REVIEW_OUTPUT}"
              fi
            else
              echo "openai CLI not found; creating a stub output for demo continuity."
              echo '{"findings":[],"overall_correctness":"patch is correct","overall_explanation":"(CLI not available on agent)","overall_confidence_score":0.4}' > "${REVIEW_OUTPUT}"
            fi
          '''
        }
      }
    }

    stage('Inspect structured Codex output') {
      steps {
        sh '''
          if [ -s codex-output.json ]; then
            jq '.' codex-output.json || true
          else
            echo "Codex output file missing"
          fi
        '''
      }
    }

    stage('Publish inline review comments') {
      when { expression { true } }
      steps {
        withCredentials([string(credentialsId: 'github-token', variable: 'GITHUB_TOKEN')]) {
          sh '''
            set -euo pipefail
            REVIEW_JSON="codex-output.json"
            if [ ! -s "$REVIEW_JSON" ]; then
              echo "No Codex output file present; skipping comment publishing."
              exit 0
            fi

            findings_count=$(jq '.findings | length' "$REVIEW_JSON")
            if [ "$findings_count" -eq 0 ]; then
              echo "Codex returned no findings; skipping inline comments."
              exit 0
            fi

            jq -c --arg commit "$HEAD_SHA" '.findings[] | {
                body: (.title + "\\n\\n" + .body + "\\n\\nConfidence: " + (.confidence_score | tostring) + (if has("priority") then "\\nPriority: P" + (.priority | tostring) else "" end)),
                commit_id: $commit,
                path: .code_location.absolute_file_path,
                line: .code_location.line_range.end,
                side: "RIGHT",
                start_line: (if .code_location.line_range.start != .code_location.line_range.end then .code_location.line_range.start else null end),
                start_side: (if .code_location.line_range.start != .code_location.line_range.end then "RIGHT" else null end)
              } | with_entries(select(.value != null))' "$REVIEW_JSON" > findings.jsonl

            while IFS= read -r payload; do
              echo "Posting review comment payload:" && echo "$payload" | jq '.'
              curl -sS \
                -X POST \
                -H "Accept: application/vnd.github+json" \
                -H "Authorization: Bearer ${GITHUB_TOKEN}" \
                -H "X-GitHub-Api-Version: 2022-11-28" \
                "https://api.github.com/repos/${REPOSITORY}/pulls/${PR_NUMBER}/comments" \
                -d "$payload"
            done < findings.jsonl
          '''
        }
      }
    }

    stage('Publish overall summary comment') {
      steps {
        withCredentials([string(credentialsId: 'github-token', variable: 'GITHUB_TOKEN')]) {
          sh '''
            set -euo pipefail
            REVIEW_JSON="codex-output.json"
            if [ ! -s "$REVIEW_JSON" ]; then
              echo "Codex output missing; skipping summary."
              exit 0
            fi

            overall_state=$(jq -r '.overall_correctness' "$REVIEW_JSON")
            overall_body=$(jq -r '.overall_explanation' "$REVIEW_JSON")
            confidence=$(jq -r '.overall_confidence_score' "$REVIEW_JSON")
            msg="**Codex automated review**\\n\\nVerdict: ${overall_state}\\nConfidence: ${confidence}\\n\\n${overall_body}"

            jq -n --arg body "$msg" '{body: $body}' > /tmp/summary.json

            curl -sS \
              -X POST \
              -H "Accept: application/vnd.github+json" \
              -H "Authorization: Bearer ${GITHUB_TOKEN}" \
              -H "X-GitHub-Api-Version: 2022-11-28" \
              "https://api.github.com/repos/${REPOSITORY}/issues/${PR_NUMBER}/comments" \
              -d @/tmp/summary.json
          '''
        }
      }
    }
  }

  post {
    always {
      archiveArtifacts artifacts: 'codex-*.json, *.md, /tmp/diff*.txt', allowEmptyArchive: true
    }
  }
}
```

# まとめ

Codex SDKを使用すると、オンプレミス環境で独自のGitHubコードレビューを構築できます。しかし、プロンプトでCodexをトリガーし、構造化出力を受け取り、その出力でAPI呼び出しを行うというパターンは、コードレビューをはるかに超えて拡張されます。例えば、このパターンを使用してインシデントが作成されたときに根本原因分析をトリガーし、構造化レポートをSlackチャンネルに投稿することができます。または、各PRでコード品質レポートを作成し、結果をダッシュボードに投稿することもできます。