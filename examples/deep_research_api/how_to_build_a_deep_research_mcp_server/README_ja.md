# Deep Research用MCP

これは、OpenAIファイルストレージサービスからファイルを検索・取得するためのDeep Researchスタイルの最小限のMCPサーバーの例です。

Responses APIからDeep Researchでこのサービスを呼び出す方法については、[このクックブック](https://cookbook.openai.com/examples/deep_research_api/introduction_to_deep_research_api)を参照してください。Agents SDKでMCPサーバーを呼び出す方法については、[このクックブック](https://cookbook.openai.com/examples/deep_research_api/how_to_use_deep_research_API_agents)をチェックしてください！

Deep Researchエージェントは特にSearchとFetchツールに依存しています。Searchは、特定のtop-k IDのセットについてオブジェクトストアを検索する必要があります。Fetchは、objectIdを引数として受け取り、関連するリソースを取得するツールです。

## セットアップと実行

内部ファイルを[OpenAI Vector Storage](https://platform.openai.com/storage/vector_stores/)に保存してください。

Pythonのセットアップ：

```shell
python3 -m venv env
source env/bin/activate
pip install -r requirements.txt
```

サーバーを実行：

```shell
python main.py
```

サーバーはSSEトランスポートを使用して`http://0.0.0.0:8000/sse/`で開始されます。パブリックインターネットからサーバーにアクセスしたい場合は、ngrokを含む様々な方法があります：

```shell
brew install ngrok 
ngrok config add-authtoken <your_token>
ngrok http 8000
```

これで、クライアントからローカルサーバーにアクセスできるようになります。

## ファイル

- `main.py`: [メインサーバーコード](https://github.com/openai/openai-cookbook/blob/main/examples/deep_research_api/how_to_build_a_deep_research_mcp_server/main.py)

## MCPサーバーのフロー図例

![../../../images/mcp_dr.png](../../../images/mcp_dr.png)

## リクエスト例

```python
# system_messageには、MCP用の内部ファイル検索への参照が含まれています。
system_message = """
あなたは、グローバルヘルス経済学チームの代表として、構造化されたデータ駆動型レポートを作成するプロフェッショナルな研究者です。あなたの任務は、ユーザーが提起する健康問題を分析することです。

実行すること：
- データ豊富な洞察に焦点を当てる：具体的な数値、傾向、統計、測定可能な成果を含める（例：入院費用の削減、市場規模、価格動向、支払者の採用）。
- 適切な場合は、チャートや表に変換できる方法でデータを要約し、レスポンスでそれを明示する（例：「これは地域別の患者あたりコストを比較する棒グラフとしてうまく機能するでしょう」）。
- 信頼性の高い最新のソースを優先する：査読済み研究、保健機関（WHO、CDCなど）、規制機関、または製薬会社の収益報告。
- 独自の内部データソースから情報を取得するための内部ファイル検索ツールを含める。すでにファイルを取得している場合は、同じファイルに対して再度fetchを呼び出さない。そのデータの包含を優先する。
- インライン引用を含め、すべてのソースメタデータを返す。

分析的であり、一般論を避け、各セクションが医療政策や財務モデリングに情報を提供できるデータに基づく推論をサポートするようにしてください。
"""

user_query = "セマグルチドがグローバル医療システムに与える経済的影響を研究してください。"

response = client.responses.create(
  model="o3-deep-research-2025-06-26",
  input=[
    {
      "role": "developer",
      "content": [
        {
          "type": "input_text",
          "text": system_message,
        }
      ]
    },
    {
      "role": "user",
      "content": [
        {
          "type": "input_text",
          "text": user_query,
        }
      ]
    }
  ],
  reasoning={
    "summary": "auto"
  },
  tools=[
    {
      "type": "web_search_preview"
    },
    { # MCPツールサポートを追加
      "type": "mcp",
      "server_label": "internal_file_lookup",
      "server_url": "http://0.0.0.0:8000/sse/", # *あなたの*MCPサーバーの場所に更新してください
      "require_approval": "never"
    }
  ]
)
```