# GitLabでCodex CLIを使用したコード品質とセキュリティ修正の自動化

## はじめに

本番コードをデプロイする際、ほとんどのチームはCI/CDパイプラインを使用して、マージ前に変更を検証しています。レビュアーは通常、単体テストの結果、脆弱性スキャン、コード品質レポートを確認します。従来、これらはルールベースのエンジンによって生成され、既知の問題をキャッチしますが、文脈的または高次の問題を見逃すことが多く、開発者にとって優先順位を付けたり対処したりするのが困難なノイズの多い結果を残すことがあります。

LLMを使用することで、このプロセスに新しいインテリジェンスレイヤーを追加できます：コード品質について推論し、セキュリティ発見事項を解釈することです。GitLabパイプラインを**OpenAIのCodex CLI**で拡張することで、チームは静的ルールを超えた洞察を得ることができます：

* **コード品質** → マージリクエストで文脈的な問題を直接表示するGitLab準拠のCodeClimate JSONレポートを生成。

* **セキュリティ** → 既存のSAST結果を後処理して重複を統合し、悪用可能性によって問題をランク付けし、明確で実行可能な修復手順を提供。

このガイドでは、両方のユースケースでCodex CLIをGitLabパイプラインに統合する方法を示し、構造化された機械可読レポートと実行可能で人間が読みやすいガイダンスを提供します。

## Codex CLIとは？

Codex CLIは、OpenAIの推論モデルを開発ワークフローに導入するためのオープンソースのコマンドラインツールです。インストール、使用方法、完全なドキュメントについては、公式リポジトリを参照してください：[github.com/openai/codex](https://github.com/openai/codex?utm_source=chatgpt.com)。

このクックブックでは、一時的なGitLabランナーで**Full Autoモード**を使用して、標準準拠のJSONレポートを生成します。

### 前提条件

このガイドに従うには、以下が必要です：

* GitLabアカウントとプロジェクト  
* **インターネットアクセス**を持つGitLabランナー（2 vCPU、8GBメモリ、30GBストレージのLinuxランナーでテストしました）  
* ランナーは`api.openai.com`に接続できる必要があります  
* **OpenAI APIキー**（`OPENAI_API_KEY`）  
* **設定 → CI/CD → 変数**でGitLab CI/CD変数が設定されている

## 例 #1 - Codex CLIを使用したコード品質レポートの生成

### 背景

このリポジトリは、[GitLabのnode expressテンプレート](https://gitlab.com/gitlab-org/project-templates/express/-/tree/main)をベースにした意図的に脆弱なNode.js Expressデモアプリで、GitLab CI/CDでの静的アプリケーションセキュリティテスト（SAST）とコード品質スキャンを紹介するために構築されました。

コードには、コマンドインジェクション、パストラバーサル、安全でない`eval`、正規表現DoS、弱い暗号化（MD5）、ハードコードされた秘密などの一般的な落とし穴が含まれています。これは、Codexを活用したアナライザーがマージリクエストで直接レンダリングされるGitLabネイティブレポート（コード品質とSAST）を生成することを検証するために使用されます。

CIは`node:24`イメージといくつかの追加機能（`jq`、`curl`、`ca-certificates`、`ajv-cli`）を持つGitLab SaaSランナーで実行されます。ジョブは`set -euo pipefail`、スキーマ検証、厳密なJSONマーカーで強化され、Codex出力が変動してもパースを確実にします。

このパイプラインパターン（プロンプト、JSONマーカー抽出、スキーマ検証）は他のスタックに適応できますが、プロンプトの文言とスキーマルールの調整が必要な場合があります。Codexはサンドボックスで実行されるため、一部のシステムコマンド（`awk`や`nl`など）が制限される場合があります。

あなたのチームは、マージ前に**コード品質チェックが自動的に実行される**ことを確実にしたいと考えています。GitLabのマージリクエストウィジェットで発見事項を直接表示するには、レポートは**CodeClimate JSON形式**に従う必要があります。[参考：GitLab Docs](https://docs.gitlab.com/ci/testing/code_quality/#import-code-quality-results-from-a-cicd-job)

### コード品質CI/CDジョブの例

**Codex CLI**を使用して準拠JSONファイルを生成するドロップイン GitLab CIジョブは以下の通りです：

```yaml
stages: [codex]

default:
  image: node:24
  variables:
    CODEX_QA_PATH: "gl-code-quality-report.json"
    CODEX_RAW_LOG: "artifacts/codex-raw.log"
    # Strict prompt: must output a single JSON array (or []), no prose/markdown/placeholders.
    CODEX_PROMPT: |
      Review this repository and output a GitLab Code Quality report in CodeClimate JSON format.
      RULES (must follow exactly):
      - OUTPUT MUST BE A SINGLE JSON ARRAY. Example: [] or [ {...}, {...} ].
      - If you find no issues, OUTPUT EXACTLY: []
      - DO NOT print any prose, backticks, code fences, markdown, or placeholders.
      - DO NOT write any files. PRINT ONLY between these two lines:
        === BEGIN_CODE_QUALITY_JSON ===
        <JSON ARRAY HERE>
        === END_CODE_QUALITY_JSON ===
      Each issue object MUST include these fields:
        "description": String,
        "check_name": String (short rule name),
        "fingerprint": String (stable across runs for same issue),
        "severity": "info"|"minor"|"major"|"critical"|"blocker",
        "location": { "path": "<repo-relative-file>", "lines": { "begin": <line> } }
      Requirements:
      - Use repo-relative paths from the current checkout (no "./", no absolute paths).
      - Use only files that actually exist in this repo.
      - No trailing commas. No comments. No BOM.
      - Prefer concrete, de-duplicated findings. If uncertain, omit the finding.

codex_review:
  stage: codex
  # Skip on forked MRs (no secrets available). Run only if OPENAI_API_KEY exists.
  rules:
    - if: '$CI_PIPELINE_SOURCE == "merge_request_event" && $CI_MERGE_REQUEST_SOURCE_PROJECT_ID != $CI_PROJECT_ID'
      when: never
    - if: '$OPENAI_API_KEY'
      when: on_success
    - when: never

  script:
    - set -euo pipefail
    - echo "PWD=$(pwd)  CI_PROJECT_DIR=${CI_PROJECT_DIR}"
    # Ensure artifacts always exist so upload never warns, even on early failure
    - mkdir -p artifacts
    - ': > ${CODEX_RAW_LOG}'
    - ': > ${CODEX_QA_PATH}'
    # Minimal deps + Codex CLI
    - apt-get update && apt-get install -y --no-install-recommends curl ca-certificates git lsb-release
    - npm -g i @openai/codex@latest
    - codex --version && git --version
    # Build a real-file allowlist to guide Codex to valid paths/lines
    - FILE_LIST="$(git ls-files | sed 's/^/- /')"
    - |
      export CODEX_PROMPT="${CODEX_PROMPT}
      Only report issues in the following existing files (exactly as listed):
      ${FILE_LIST}"
    # Run Codex; allow non-zero exit but capture output for extraction
    - |
      set +o pipefail
      script -q -c 'codex exec --full-auto "$CODEX_PROMPT"' | tee "${CODEX_RAW_LOG}" >/dev/null
      CODEX_RC=${PIPESTATUS[0]}
      set -o pipefail
      echo "Codex exit code: ${CODEX_RC}"
    # Strip ANSI + \r, extract JSON between markers to a temp file; validate or fallback to []
    - |
      TMP_OUT="$(mktemp)"
      sed -E 's/\x1B\[[0-9;]*[A-Za-z]//g' "${CODEX_RAW_LOG}" \
        | tr -d '\r' \
        | awk '
            /^\s*=== BEGIN_CODE_QUALITY_JSON ===\s*$/ {grab=1; next}
            /^\s*=== END_CODE_QUALITY_JSON ===\s*$/   {grab=0}
            grab
          ' > "${TMP_OUT}"
      # If extracted content is empty/invalid or still contains placeholders, replace with []
      if ! node -e 'const f=process.argv[1]; const s=require("fs").readFileSync(f,"utf8").trim(); if(!s || /(<JSON ARRAY HERE>|BEGIN_CODE_QUALITY_JSON|END_CODE_QUALITY_JSON)/.test(s)) process.exit(2); JSON.parse(s);' "${TMP_OUT}"; then
        echo "WARNING: Extracted content empty/invalid; writing empty [] report."
        echo "[]" > "${TMP_OUT}"
      fi
      mv -f "${TMP_OUT}" "${CODEX_QA_PATH}"
      # Soft warning if Codex returned non-zero but we still produced a report
      if [ "${CODEX_RC}" -ne 0 ]; then
        echo "WARNING: Codex exited with code ${CODEX_RC}. Proceeding with extracted report." >&2
      fi

  artifacts:
    when: always
    reports:
      codequality: gl-code-quality-report.json
    paths:
      - artifacts/codex-raw.log
    expire_in: 14 days
```

1. Codex CLIをインストール（`npm -g i @openai/codex@latest`）  
2. `git ls-files`でファイル許可リストを構築  
3. 厳密なJSONのみのプロンプトで**full-autoモード**でCodexを実行  
4. マーカー間の有効なJSONを抽出し、検証し、無効な場合は`[]`にフォールバック  
5. GitLabにアーティファクトを公開して、結果がマージリクエストにインラインで表示されるようにする

生成されたアーティファクトは、パイプラインページからダウンロードできます

<img src="../../images/gitlab-pipelines-success.png" alt="GitLab Pipelines" width="700"/>

または、フィーチャーブランチからマスターブランチへのマージとして実行する場合、

<img src="../../images/gitlab-mr-widget.png" alt="GitLab Merge Request Widget" width="700"/>

Codex CLIをGitLab CI/CDパイプラインに組み込むことで、**静的ルールを超えたコード品質チェックを向上させる**ことができます。構文エラーやスタイル違反のみをキャッチするのではなく、文脈で潜在的な問題を強調する推論ベースの分析を可能にします。

このアプローチには以下のような利点があります：

* **一貫性**：すべてのマージリクエストが同じ推論プロセスでレビューされる  
* **文脈認識**：LLMはルールベーススキャナーが見逃す微妙な問題にフラグを立てることができる  
* **開発者のエンパワーメント**：フィードバックは即座に、視覚的に、実行可能である

チームがこのワークフローを採用することで、LLMを活用した品質チェックは従来のリンティングと脆弱性スキャンを補完し、本番環境に出荷されるコードが堅牢で保守可能であることを確実にするのに役立ちます。

## 例 #2 – セキュリティ修復のためのCodex CLIの使用

### 背景

この例では、意図的に脆弱なNode.js ExpressアプリであるOWASP Juice Shop](https://github.com/juice-shop/juice-shop?utm_source=chatgpt.com)でテストしました。これには、インジェクション、安全でない`eval`、弱い暗号、ハードコードされた秘密などの一般的な欠陥が含まれており、Codexを活用した分析の検証に理想的です。

あなたのチームは、コード変更が導入されるたびに、マージ前にパイプラインが自動的にセキュリティ脆弱性をチェックすることを確実にしたいと考えています。これは既に静的アナライザーと言語固有のスキャナーによって処理されており、GitLab SAST JSONスキーマでレポートを生成します。しかし、生の出力は硬直的でノイズが多く、レビュアーに明確な次のステップを残さないことがよくあります。

Codex CLIをパイプラインに追加することで、[GitLab SASTスキャナー](https://docs.gitlab.com/user/application_security/sast/)（または他のスキャナー出力）によって生成されたスキャナー結果を**実行可能な修復ガイダンス**に変換し、**適用可能なgitパッチ**を生成することもできます：

### ステップ1：推奨事項の生成

* Codexは`gl-sast-report.json`を読み取ります。  
* 重複する発見事項を統合します。  
* 悪用可能性によってランク付けします（例：ユーザー入力 → 危険なシンク）。  
* 上位5つのアクションと詳細な修復ノートを含む簡潔な`security_priority.md`を生成します。

#### セキュリティ推奨事項CI/CDジョブの例

**要件**：このジョブは、上流のSASTジョブが既に`gl-sast-report.json`を生成していることを期待します。Codexはそれを読み取り、レビュアー向けに`security_priority.md`を生成します。

```yaml
stages:
 - codex
 - remediation

default:
 image: node:24

variables:
 CODEX_SAST_PATH: "gl-sast-report.json"
 CODEX_SECURITY_MD: "security_priority.md"
 CODEX_RAW_LOG: "artifacts/codex-sast-raw.log"

 # --- Recommendations prompt (reads SAST → writes Markdown) ---
 CODEX_PROMPT: |
   You are a security triage assistant analyzing GitLab SAST output.
   The SAST JSON is located at: ${CODEX_SAST_PATH}

   GOAL:
   - Read and parse ${CODEX_SAST_PATH}.
   - Consolidate duplicate or overlapping findings (e.g., same CWE + same sink/function, same file/line ranges, or same data flow root cause).
   - Rank findings by realistic exploitability and business risk, not just library presence.
     * Prioritize issues that:
       - Are reachable from exposed entry points (HTTP handlers, controllers, public APIs, CLI args).
       - Involve user-controlled inputs reaching dangerous sinks (e.g., SQL exec, OS exec, eval, path/file ops, deserialization, SSRF).
       - Occur in authentication/authorization boundaries or around secrets/keys/tokens.
       - Have clear call stacks/evidence strings pointing to concrete methods that run.
       - Affect internet-facing or privileged components.
     * De-prioritize purely theoretical findings with no reachable path or dead code.

   CONSOLIDATION RULES:
   - Aggregate by (CWE, primary sink/function, file[:line], framework route/handler) when applicable.
   - Merge repeated instances across files if they share the same source-sink pattern and remediation is the same.
   - Keep a single representative entry with a count of affected locations; list notable examples.

   OUTPUT FORMAT (MARKDOWN ONLY, BETWEEN MARKERS BELOW):
   - Start with a title and short summary of total findings and how many were consolidated.
   - A table of TOP PRIORITIES sorted by exploitability (highest first) with columns:
     Rank | CWE | Title | Affected Locations | Likely Exploit Path | Risk | Rationale (1–2 lines)
   - "Top 5 Immediate Actions" list with concrete next steps.
   - "Deduplicated Findings (Full Details)" with risk, 0–100 exploitability score, evidence (file:line + methods), remediation, owners, references.
   - If ${CODEX_SAST_PATH} is missing or invalid JSON, output a brief note stating no parsable SAST findings.

   RULES (must follow exactly):
   - PRINT ONLY between these two lines:
     === BEGIN_SECURITY_MD ===
     <MARKDOWN CONTENT HERE>
     === END_SECURITY_MD ===
   - No prose, backticks, code fences, or anything outside the markers.
   - Be concise but specific. Cite only evidence present in the SAST report.

# ---------------------------
# Stage: codex → Job 1 (Recommendations)
# ---------------------------
codex_recommendations:
 stage: codex
 rules:
   - if: '$CI_PIPELINE_SOURCE == "merge_request_event" && $CI_MERGE_REQUEST_SOURCE_PROJECT_ID != $CI_PROJECT_ID'
     when: never
   - if: '$OPENAI_API_KEY'
     when: on_success
   - when: never
 script:
   - set -euo pipefail
   - mkdir -p artifacts
   - ": > ${CODEX_RAW_LOG}"
   - ": > ${CODEX_SECURITY_MD}"

   - apt-get update && apt-get install -y --no-install-recommends curl ca-certificates git lsb-release
   - npm -g i @openai/codex@latest
   - codex --version && git --version

   - |
     if [ ! -s "${CODEX_SAST_PATH}" ]; then
       echo "WARNING: ${CODEX_SAST_PATH} not found or empty. Codex will emit a 'no parsable findings' note."
     fi

   - FILE_LIST="$(git ls-files | sed 's/^/- /')"
   - |
     export CODEX_PROMPT="${CODEX_PROMPT}

     Existing repository files (for reference only; use paths exactly as listed in SAST evidence):
     ${FILE_LIST}"

   # Run Codex and capture raw output (preserve Codex's exit code via PIPESTATUS)
   - |
     set +o pipefail
     codex exec --full-auto "$CODEX_PROMPT" | tee "${CODEX_RAW_LOG}" >/dev/null
     CODEX_RC=${PIPESTATUS[0]}
     set -o pipefail
     echo "Codex exit code: ${CODEX_RC}"

   # Extract markdown between markers; fallback to a minimal note
   - |
     TMP_OUT="$(mktemp)"
     sed -E 's/\x1B\[[0-9;]*[A-Za-z]//g' "${CODEX_RAW_LOG}" | tr -d '\r' | awk '
       /^\s*=== BEGIN_SECURITY_MD ===\s*$/ {grab=1; next}
       /^\s*=== END_SECURITY_MD ===\s*$/   {grab=0}
       grab
     ' > "${TMP_OUT}"
     if ! [ -s "${TMP_OUT}" ]; then
       cat > "${TMP_OUT}" <<'EOF' # Security Findings Priority
       No parsable SAST findings detected in `gl-sast-report.json`._
     EOF
       echo "WARNING: No content extracted; wrote minimal placeholder."
     fi
     mv -f "${TMP_OUT}" "${CODEX_SECURITY_MD}"
     if [ "${CODEX_RC}" -ne 0 ]; then
       echo "WARNING: Codex exited with code ${CODEX_RC}. Proceeding with extracted report." >&2
     fi
 artifacts:
   when: always
   paths:
     - artifacts/codex-sast-raw.log
     - security_priority.md
   expire_in: 14 days
```

受け取る出力の例は以下の通りです：

### 出力例：統合されたSAST発見事項

`gl-sast-report.json`を解析し、重複する問題をマージしました。  
**生の発見事項総数：** 5 → **統合後：** 4つの代表的エントリ  
（エンドポイント間で重複したSQLインジェクションパターンがマージされました）。

#### 概要テーブル

| ランク | CWE      | タイトル                                | 影響を受ける場所 | 悪用経路の可能性                  | リスク     | 根拠（1-2行）                                                                                 |
|------|----------|--------------------------------------|-------------------|--------------------------------------|----------|--------------------------------------------------------------------------------------------------------|
| 1    | CWE-798  | ハードコードされたJWT秘密鍵            | 1                 | 認証トークン発行/検証   | クリティカル | リポジトリリークにより有効な管理者JWTの生成が可能；簡単な悪用、インターネット向け。                     |
| 2    | CWE-89   | ログインと検索でのSQLインジェクション    | 2                 | ログインエンドポイント；製品検索       | クリティカル | 生のSQL連結；パブリックHTTPハンドラー経由での直接ログインバイパスとデータ流出。             |
| 3    | CWE-94   | evalによるサーバーサイドコードインジェクション  | 1                 | ユーザープロファイル更新ハンドラー          | 高     | ユーザー入力での`eval()`はRCEを許可；条件付きで有効だが、到達可能な場合は依然として高影響。          |
| 4    | — (SSRF) | 任意の画像URL取得によるSSRF   | 1                 | 画像URL取得/書き込みフロー           | 高     | 未検証URLの外部取得により内部サービス/メタデータアクセスが可能（例：AWSメタデータ）。     |

#### 上位5つの即座のアクション
1. `lib/insecurity.ts:23`のハードコードされたJWT署名キーを置き換え；シークレットストレージから読み込み、キーをローテーション、既存トークンを無効化。  
2. `routes/login.ts:34`をパラメータ化クエリを使用するよう更新；生の連結を削除；入力を検証・エスケープ。  
3. `routes/search.ts:23`を修正し、文字列連結の代わりにORMバインドパラメータまたはエスケープされた`LIKE`ヘルパーを使用。  
4. `routes/userProfile.ts:55–66`をリファクタリング；`eval()`を安全なテンプレートまたはホワイトリスト化された評価器に置き換え。  
5. 画像インポートロジックを強化：スキーム/ホストを許可リスト化、リンクローカル/メタデータIPをブロック、タイムアウトとサイズ制限を適用。  

##### 重複除去された発見事項（詳細）

##### 1. CWE-798 — ハードコードされたJWT秘密鍵
- リスク：クリティカル — 悪用可能性 98/100  
- 証拠：  
  - ファイル：`lib/insecurity.ts:23`  
  - メッセージ：ソースに埋め込まれたRSA秘密鍵により偽造された管理者トークンが可能  
- 推奨修復：ソースからキーを削除、env/シークレットマネージャー経由で読み込み、キーをローテーション、短いTTLを強制  
- 所有者/チーム：バックエンド/コア（lib）  
- 参考：CWE-798; OWASP ASVS 2.1.1, 2.3.1  
---
##### 2. CWE-89 — SQLインジェクション（ログイン＆検索）
- リスク：クリティカル — 悪用可能性 95/100  
- 証拠：  
  - `routes/login.ts:34` — `' OR 1=1--`による典型的なログインバイパス  
  - `routes/search.ts:23` — `%25' UNION SELECT ...`によるUNIONベースの抽出  
- 推奨修復：パラメータ化クエリ/ORMを使用、入力を検証、WAF/エラー抑制を追加  
- 所有者/チーム：バックエンド/API（routes）  
- 参考：CWE-89; OWASP Top 10 A03:2021; ASVS 5.3  
---
##### 3. CWE-94 — サーバーサイドコードインジェクション（`eval`）
- リスク：高 — 悪用可能性 72/100  
- 証拠：  
  - `routes/userProfile.ts:55–66` — 動的ユーザー名パターンに`eval()`を使用  
- 推奨修復：`eval()`を削除、または厳密なホワイトリストでサンドボックス化；入力を検証/エンコード  
- 所有者/チーム：バックエンド/API（routes）  
- 参考：CWE-94; OWASP Top 10 A03:2021  
---
##### 4. SSRF — 任意の画像URL取得
- リスク：高 — 悪用可能性 80/100  
- 証拠：  
  - 画像インポートが任意の`imageUrl`を取得 → 内部サービス（`169.254.169.254`）にアクセス可能  
- 推奨修復：HTTPS + DNS/IP許可リストを強制、RFC1918/リンクローカルをブロック、解決後検証、リダイレクトなし  
- 所有者/チーム：バックエンド/API（routes）  
- 参考：OWASP SSRF Prevention; OWASP Top 10 A10:2021  
---
### ステップ2：推奨事項に基づくセキュリティ問題の修復
- CodexはSAST JSONとリポジトリツリーの両方を使用します。  
- 各高/クリティカル問題について：  
  - 構造化されたプロンプトを構築 → 統一された`git diff`を出力。  
  - Diffは`.patch`として保存される前に検証されます（`git apply --check`）。  

#### 修復CI/CDジョブの例

**要件**：このジョブは、MR作成用のパッチファイルを生成するための入力として使用する`security_priority.md`ファイルの前段階出力に依存します：

```yaml
 stages:
  - remediation

default:
  image: node:24

variables:
  # Inputs/outputs
  SAST_REPORT_PATH: "gl-sast-report.json"
  PATCH_DIR: "codex_patches"
  CODEX_DIFF_RAW: "artifacts/codex-diff-raw.log"

  # --- Resolution prompt (produces unified git diffs only) ---
  CODEX_DIFF_PROMPT: |
    You are a secure code remediation assistant.
    You will receive:
    - The repository working tree (read-only)
    - One vulnerability (JSON from a GitLab SAST report)
    - Allowed files list

    GOAL:
    - Create the minimal, safe fix for the vulnerability.
    - Output a unified git diff that applies cleanly with `git apply -p0` (or -p1 for a/ b/ paths).
    - Prefer surgical changes: input validation, safe APIs, parameterized queries, permission checks.
    - Do NOT refactor broadly or change unrelated code.

    RULES (must follow exactly):
    - PRINT ONLY the diff between the markers below.
    - Use repo-relative paths; `diff --git a/path b/path` headers are accepted.
    - No binary file changes. No prose/explanations outside the markers.

    MARKERS:
    === BEGIN_UNIFIED_DIFF ===
    <unified diff here>
    === END_UNIFIED_DIFF ===

    If no safe fix is possible without deeper changes, output an empty diff between the markers.

# ---------------------------
# Stage: remediation → Generate unified diffs/patches
# ---------------------------
codex_resolution:
  stage: remediation
  rules:
    - if: '$OPENAI_API_KEY'
      when: on_success
    - when: never
  script:
    - set -euo pipefail
    - mkdir -p "$PATCH_DIR" artifacts

    # Deps
    - apt-get update && apt-get install -y --no-install-recommends bash git jq curl ca-certificates
    - npm -g i @openai/codex@latest
    - git --version && codex --version || true

    # Require SAST report; no-op if missing
    - |
      if [ ! -s "${SAST_REPORT_PATH}" ]; then
        echo "No SAST report found; remediation will no-op."
        printf "CODEX_CREATED_PATCHES=false\n" > codex.env
        exit 0
      fi

    # Pull High/Critical items
    - jq -c '.vulnerabilities[]? | select((.severity|ascii_downcase)=="high" or (.severity|ascii_downcase)=="critical")' "$SAST_REPORT_PATH" \
        | nl -ba > /tmp/hicrit.txt || true
    - |
      if [ ! -s /tmp/hicrit.txt ]; then
        echo "No High/Critical vulnerabilities found. Nothing to fix."
        printf "CODEX_CREATED_PATCHES=false\n" > codex.env
        exit 0
      fi

    # Ground Codex to actual repo files
    - FILE_LIST="$(git ls-files | sed 's/^/- /')"

    # Identity for any local patch ops
    - git config user.name "CI Codex Bot"
    - git config user.email "codex-bot@example.com"

    - created=0

    # Loop: build prompt (robust temp-file), run Codex, extract diff, validate
    - |
      while IFS=$'\t' read -r idx vuln_json; do
        echo "Processing vulnerability #$idx"
        echo "$vuln_json" > "/tmp/vuln-$idx.json"

        PROMPT_FILE="$(mktemp)"
        {
          printf "%s\n\n" "$CODEX_DIFF_PROMPT"
          printf "VULNERABILITY_JSON:\n<<JSON\n"
          cat "/tmp/vuln-$idx.json"
          printf "\nJSON\n\n"
          printf "EXISTING_REPOSITORY_FILES (exact list):\n"
          printf "%s\n" "$FILE_LIST"
        } > "$PROMPT_FILE"

        PER_FINDING_PROMPT="$(tr -d '\r' < "$PROMPT_FILE")"
        rm -f "$PROMPT_FILE"

        : > "$CODEX_DIFF_RAW"
        set +o pipefail
        codex exec --full-auto "$PER_FINDING_PROMPT" | tee -a "$CODEX_DIFF_RAW" >/dev/null
        RC=${PIPESTATUS[0]}
        set -o pipefail
        echo "Codex (diff) exit code: ${RC}"

        OUT_PATCH="$PATCH_DIR/fix-$idx.patch"
        sed -E 's/\x1B\[[0-9;]*[A-Za-z]//g' "$CODEX_DIFF_RAW" \
          | tr -d '\r' \
          | awk '
              /^\s*=== BEGIN_UNIFIED_DIFF ===\s*$/ {grab=1; next}
              /^\s*=== END_UNIFIED_DIFF ===\s*$/   {grab=0}
              grab
            ' > "$OUT_PATCH"

        if ! [ -s "$OUT_PATCH" ] || ! grep -qE '^\s*diff --git ' "$OUT_PATCH"; then
          echo "  No usable diff produced for #$idx; skipping."
          rm -f "$OUT_PATCH"
          continue
        fi

        # Validate: accept -p0 (repo-relative) or -p1 (a/ b/ prefixes)
        if git apply --check -p0 "$OUT_PATCH" || git apply --check -p1 "$OUT_PATCH"; then
          echo "  Patch validated → $OUT_PATCH"
          created=$((created+1))
        else
          echo "  Patch failed to apply cleanly; removing."
          rm -f "$OUT_PATCH"
        fi
      done < /tmp/hicrit.txt

      if [ "$created" -gt 0 ]; then
        printf "CODEX_CREATED_PATCHES=true\nPATCH_DIR=%s\n" "$PATCH_DIR" > codex.env
      else
        printf "CODEX_CREATED_PATCHES=false\n" > codex.env
      fi
  artifacts:
    when: always
    paths:
      - codex_patches/
      - artifacts/codex-diff-raw.log
    reports:
      dotenv: codex.env
    expire_in: 14 days
```

Codex CLIでCI/CDジョブを実行すると、セキュリティスキャナーによって最初に発見された問題を修正するGitパッチを受け取ります：

```patch
<unified diff here>
diff --git a/routes/profileImageUrlUpload.ts b/routes/profileImageUrlUpload.ts
index 9b4a62d..c7f1a7e 100644
--- a/routes/profileImageUrlUpload.ts
+++ b/routes/profileImageUrlUpload.ts
@@ -5,17 +5,12 @@
 * SPDX-License-Identifier: MIT
 */
-import fs from 'node:fs'
-import { Readable } from 'node:stream'
-import { finished } from 'node:stream/promises'
import { type Request, type Response, type NextFunction } from 'express'
import * as security from '../lib/insecurity'
import { UserModel } from '../models/user'
-import * as utils from '../lib/utils'
-import logger from '../lib/logger'
export function profileImageUrlUpload () {
  return async (req: Request, res: Response, next: NextFunction) => {
    if (req.body.imageUrl !== undefined) {
      const url = req.body.imageUrl
      if (url.match(/(.)*solve\\/challenges\\/server-side(.)*/) !== null) req.app.locals.abused_ssrf_bug = true
      const loggedInUser = security.authenticatedUsers.get(req.cookies.token)
      if (loggedInUser) {
-        try {
-          const response = await fetch(url)
-          if (!response.ok || !response.body) {
-            throw new Error('url returned a non-OK status code or an empty body')
-          }
-          const ext = ['jpg', 'jpeg', 'png', 'svg', 'gif'].includes(url.split('.').slice(-1)[0].toLowerCase()) ? url.split('.').slice(-1)[0].toLowerCase() : 'jpg'
-          const fileStream = fs.createWriteStream(`frontend/dist/frontend/assets/public/images/uploads/${loggedInUser.data.id}.${ext}`, { flags: 'w' })
-          await finished(Readable.fromWeb(response.body as any).pipe(fileStream))
-          await UserModel.findByPk(loggedInUser.data.id).then(async (user: UserModel | null) => { return await user?.update({ profileImage: `/assets/public/images/uploads/${loggedInUser.data.id}.${ext}` }) }).catch((error: Error) => { next(error) })
-        } catch (error) {
-          try {
-            const user = await UserModel.findByPk(loggedInUser.data.id)
-            await user?.update({ profileImage: url })
-            logger.warn(`Error retrieving user profile image: ${utils.getErrorMessage(error)}; using image link directly`)
-          } catch (error) {
-            next(error)
-            return
-          }
-        }
+        try {
+          const user = await UserModel.findByPk(loggedInUser.data.id)
+          await user?.update({ profileImage: url })
+        } catch (error) {
+          next(error)
+          return
+        }
      } else {
        next(new Error('Blocked illegal activity by ' + req.socket.remoteAddress))
        return
```

## 主な利点
GitLab CI/CDでCodex CLIを使用することで、既存のレビュープロセスを拡張し、チームがより速く出荷できるようになります。

* **補完的**：Codexはスキャナーを置き換えるのではなく、その発見事項を解釈し、修正を加速します。 
* **実行可能**：レビュアーは脆弱性だけでなく、それらを修正するための優先順位付けされたステップを見ることができます。  
* **自動化**：パッチはCI内で直接作成され、`git apply`や修復ブランチの準備が整います。  

---

## まとめ

このクックブックでは、**Codex CLI**をGitLab CI/CDパイプラインに組み込んで、ソフトウェア配信をより安全で保守可能にする方法を探りました：

* **コード品質レポート**：推論ベースの発見事項がリント、単体テスト、スタイルチェックと並んで表示されるよう、GitLab準拠のCodeClimate JSONを生成。

* **脆弱性解釈**：SASTやその他のセキュリティスキャナーの生出力（`gl-sast-report.json`）を取得し、重複除去、悪用可能性ランキング、実行可能な次のステップを含む優先順位付けされた人間が読みやすい計画（`security_priority.md`）に変換。

* **自動修復**：Codexに統一されたgit diffを`.patch`ファイルとして生成させることでワークフローを拡張。これらのパッチは検証され（`git apply --check`）、新しいブランチに自動的に適用できます。

これらのパターンを総合すると、**LLMを活用した分析が従来のルールベースツールを補完し、置き換えるものではない**ことがわかります。スキャナーは検出の信頼できる情報源であり続け、Codexは文脈認識、優先順位付け、開発者ガイダンス、さらにはMR経由で具体的な修正を提案する能力を追加します。GitLabのスキーマとAPIは、これらの出力を予測可能で実行可能、そして開発者ワークフローに完全に統合されたものにする構造を提供します。

重要な教訓は、良い結果には**明確なプロンプト、スキーマ検証、ガードレール**が必要だということです。JSONマーカー、重要度ホワイトリスト、スキーマ強制、diff検証により、出力が使用可能であることを保証します。

今後、このパターンは単一のCodexを活用した修復フローを通じて、すべての主要なスキャンタイプを統合するよう拡張できます：

* **依存関係スキャン** → ロックファイル間でCVEを統合し、アップグレードを推奨し、脆弱なバージョンをバンプするdiffを自動生成。  
* **コンテナ/イメージスキャン** → 古いベースイメージにフラグを立て、Dockerfileの更新を提案。  
* **DAST結果** → 悪用可能なエンドポイントを強調し、検証やアクセス制御のためのルーティング/ミドルウェアにパッチを適用。

これらを単一のCodexを活用した後処理＋修復パイプラインにマージすることで、チームはすべてのセキュリティドメインにわたって**実行可能なガイダンス、検証されたパッチ**の一貫したストリームを得ることができます。

**より広い要点：** プロンプトエンジニアリング、スキーマ検証、GitLabのネイティブMRワークフローへの統合により、LLMは「アドバイザー」から**ファーストクラスのCI/CDエージェント**へと進化し、チームが機能的であるだけでなく、安全で保守可能、そして可能な限り自動的に修復されたコードを出荷するのを支援します。