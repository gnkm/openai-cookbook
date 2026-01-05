# Databricks MCP Assistant (React UI付き)

サプライチェーンクエリ用のフルスタック、Databricksテーマの会話型アシスタント。OpenAI AgentsとDatabricks MCPサーバーを活用し、React チャットUIとエージェントレスポンスをストリーミングするFastAPIバックエンドを含みます。

---

## 機能
- 会話型チャットUI（React）とDatabricksの赤色パレット
- ストリーミング `/chat` エンドポイントを持つFastAPIバックエンド
- セキュアなDatabricks MCP統合
- エージェントロジックとツール使用の例
- モダンなUX、簡単なローカル開発

## クイックスタート

### 0. Databricksアセット

DatabricksのSupply-Chain Optimization Solution Accelerator（または他の業界で作業している場合は他のアクセラレーター）でプロジェクトを開始できます。このアクセラレーターのGitHubリポジトリをDatabricksワークスペースにクローンし、ノートブック1を実行してバンドルされたノートブックを実行してください：

https://github.com/lara-openai/databricks-supply-chain

これらのノートブックは、エージェントが後でMCP経由でアクセスするすべてのアセットを構築します。生のエンタープライズテーブルや非構造化メールから、従来のMLモデルやグラフワークロードまで含まれます。

### 1. 前提条件
- Python 3.10+
- Node.js 18+
- `~/.databrickscfg` にDatabricksクレデンシャル
- OpenAI APIキー
- （オプション）Python分離用のVirtualenv/pyenv

### 2. Python依存関係のインストール
```bash
pip install -r requirements.txt
```

### 3. バックエンドの起動（FastAPI）

バックエンドを起動するには、以下を実行してください：

```bash
python -m uvicorn api_server:app --reload --port 8000
```
- APIは http://localhost:8000 で利用可能になります
- FastAPIドキュメント: http://localhost:8000/docs

### 4. フロントエンドの起動（React UI）
別のターミナルで以下を実行してください：
```bash
cd ui
npm install
npm run dev
```
- アプリは http://localhost:5173 で利用可能になります

---

## 使用方法
1. ブラウザで [http://localhost:5173](http://localhost:5173) を開きます。
2. サプライチェーンに関する質問（例：「配送センター5の遅延はどうなっていますか？」）を入力してSendを押します。
3. エージェントがDatabricks MCPサーバーからレスポンスをストリーミングで返します。

---

## トラブルシューティング
- **ポートが既に使用中:** `lsof -ti:8000 | xargs kill -9`（バックエンド用）で古いプロセスを終了するか、ポートを変更してください。
- **フロントエンドが読み込まれない:** `ui/` フォルダで `npm install` と `npm run dev` を実行したことを確認してください。

---

## カスタマイズ
- エージェントの挨拶を変更するには、`ui/src/components/ChatUI.jsx` を編集してください。
- バックエンドエージェントロジックを更新するには、`api_server.py` を変更してください。
- UIスタイリングは `ui/src/components/ChatUI.css`（Databricks赤色パレット）にあります。