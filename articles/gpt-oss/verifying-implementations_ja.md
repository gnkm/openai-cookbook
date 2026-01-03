# gpt-oss 実装の検証

[OpenAI gpt-oss モデル](https://openai.com/open-models)は、オープンモデルエコシステムに多くの新しい概念を導入しており、[期待どおりに動作させるには時間がかかる場合があります](https://x.com/ClementDelangue/status/1953119901649891367)。このガイドは、推論ソリューションを構築している開発者が実装を検証するため、または開発者が任意のプロバイダーの実装を自分でテストして信頼を得るためのものです。

## gpt-oss モデルの実装がなぜ異なるのか？

新しいモデルは、既存のオープンモデルよりも、他の OpenAI モデルの一部に似た動作をします。いくつかの例を次に示します：

1. **harmony レスポンス形式。** これらのモデルは、会話を構造化するために [OpenAI harmony 形式](https://cookbook.openai.com/articles/openai-harmony)で訓練されました。通常の API 開発者はほとんどの場合 harmony を扱う必要はありませんが、Chat Completions 互換、Responses 互換、またはその他の推論 API を提供する推論プロバイダーは、入力を OpenAI harmony 形式に正しくマッピングする必要があります。モデルが正しい形式でプロンプトを受け取らない場合、これは連鎖的な生成の問題を引き起こす可能性があり、少なくとも関数呼び出しのパフォーマンスが悪化します。
2. **ツール呼び出し間の思考の連鎖（CoT）の処理**。これらのモデルは、CoT の一部としてツール呼び出しを実行できます。これの結果として、モデルは最終的な応答に到達するまで、後続のサンプリングで CoT を受け取る必要があります。これは、生の CoT をエンドユーザーに表示すべきではありませんが、開発者がツール呼び出しとツール出力とともに渡すことができるように、API によって返される必要があることを意味します。[この別のガイドで詳細をご覧ください](https://cookbook.openai.com/articles/gpt-oss/handle-raw-cot)。
3. **実際の推論コードの違い**。私たちは、mixture-of-experts（MoE）の重みを MXFP4 形式でのみ公開しました。これはまだ比較的新しい形式であり、他のアーキテクチャ決定とともに、他のオープンモデル用に書かれた既存の推論コードは gpt-oss モデル用に適応する必要があります。そのため、基本的な（最適化されていない）[PyTorch 実装](https://github.com/openai/gpt-oss/tree/main/gpt_oss/torch)と、[より最適化された Triton 実装](https://github.com/openai/gpt-oss/tree/main/gpt_oss/triton)の両方を公開しました。さらに、正確性のために [vLLM 実装](https://github.com/vllm-project/vllm/blob/7e3a8dc90670fd312ce1e0d4eba9bf11c571e3ad/vllm/model_executor/models/gpt_oss.py)を検証しました。これらが他の実装のための教育資料として役立つことを願っています。

## API 設計

### Responses API

最高のパフォーマンスを得るために、推論プロバイダーが Responses API 形式を実装することをお勧めします。API の形状は、要約された CoT（ユーザーに表示するため）とツール呼び出しとともに生の CoT を出力するような動作のために特別に設計されており、形式に追加のプロパティをボルトで固定する必要がありません。正確なパフォーマンスのための最も重要な部分は、`output` の一部として生の CoT を返すことです。

このために、Responses API の `reasoning` アイテムに新しい `content` 配列を追加しました。生の CoT は `reasoning_text` タイプ要素にラップされる必要があり、全体的な出力アイテムは次のようになります：

```
{
  "type": "reasoning",
  "id": "item_67ccd2bf17f0819081ff3bb2cf6508e60bb6a6b452d3795b",
  "status": "completed",
  "summary": [
    /* オプションの要約要素 */
  ],
  "content": [
    {
      "type": "reasoning_text",
      "text": "The user needs to know the weather, I will call the get_weather tool."
    }
  ]
}
```

これらのアイテムは後続のターンで受け取られ、[生の CoT 処理ガイド](https://cookbook.openai.com/articles/gpt-oss/handle-raw-cot)で概説されているように、harmony フォーマットされたプロンプトに挿入される必要があります。

[完全な仕様については、Responses API ドキュメントをご覧ください](https://platform.openai.com/docs/api-reference/responses/create)。

### Chat Completions

多くのプロバイダーが Chat Completions 互換 API を提供しています。生の CoT を受け取る方法を提供するために公開された API リファレンスをドキュメントで拡張していませんが、gpt-oss モデルを Chat Completions 互換 API を介して提供するプロバイダーが、メッセージの一部として CoT を返し、開発者がそれらを返す方法を持つことは依然として重要です。

現在、コミュニティで一般的に合意された仕様はなく、メッセージの一般的なプロパティは `reasoning` または `reasoning_content` のいずれかです。**OpenAI Agents SDK などのクライアントと互換性を持たせるために、Chat Completions での生の CoT の主要なプロパティとして `reasoning` フィールドを使用することをお勧めします**。

## ツール呼び出しと API 形状のクイック検証

プロバイダーが機能しているかどうかを検証するには、他の評価を実行するためにも使用できる [gpt-oss GitHub リポジトリ](https://github.com/openai/gpt-oss)で公開されている Node.js スクリプトを使用できます。テストを実行するには、[Node.js](http://nodejs.org/) または同様のランタイムがインストールされている必要があります。

これらのテストは、テストしようとしている Responses API または Chat Completions API に対して、一連のツール/関数呼び出しベースのリクエストを実行します。その後、正しいツールが呼び出されたかどうかと、API 形状が正しいかどうかの両方を評価します。

これは主にスモークテストとして機能しますが、API が SDK と互換性があり、基本的な関数呼び出しを処理できるかどうかの良い指標となるはずです。推論実装の完全な精度を保証するものではなく（詳細については以下の評価セクションを参照）、OpenAI API との完全な互換性を保証するものでもありません。それでも、主要な実装の問題の有用な指標となるはずです。

テストスイートを実行するには、次のコマンドを実行します：

```shell
# リポジトリをクローン
git clone https://github.com/openai/gpt-oss.git

# 互換性テストディレクトリに移動
cd gpt-oss/compatibility-test/

# 依存関係をインストール
npm install

# providers.ts のプロバイダー設定を変更してプロバイダーを追加

# テストを実行
npm start -- --provider <your-provider-name>
```

その後、API 実装と関数呼び出しパフォーマンスの詳細の両方の結果を受け取るはずです。

テストが成功した場合、出力は0個の無効なリクエストと、pass@k と pass^k の両方で90%以上を示すはずです。これは、実装がおそらく正しいことを意味します。完全に確認するには、以下で説明するように評価も検査する必要があります。

個々の応答の詳細なビューが必要な場合は、ディレクトリに作成された `jsonl` ファイルを確認できます。

`DEBUG=openai-agents:openai npm start -- --provider <provider-name>` を使用して、実際のリクエストペイロードを表示するためにデバッグモードを有効にすることもできますが、ノイズが多くなる可能性があります。1つのテストのみを実行するには、より簡単なデバッグのために `-n 1` フラグを使用します。ストリーミングイベントをテストするには、`--streaming` を使用します。

## 評価を通じた正確性の検証

Artificial Analysis のチームは、さまざまなプロバイダーに対して AIME と GPQA の評価を実行しています。プロバイダーについて不確かな場合は、[最新のメトリックについて Artificial Analysis をご覧ください](https://artificialanalysis.ai/models/gpt-oss-120b/providers#evaluations)。

安全のために、自分で評価を実行することを検討する必要があります。独自の評価を実行するには、上記のテストと同じリポジトリに `gpt_oss/evals` フォルダーがあり、vLLM 実装と一部の独自のリファレンス実装の AIME（問題ごとに16回の試行）、GPQA（問題ごとに8回の試行）、Healthbench（問題ごとに1回の試行）の評価を検証するために使用したテストハーネスが含まれています。同じスクリプトを使用して実装をテストできます。

Responses API 互換 API をテストするには、次を実行します：

```bash
python -m gpt_oss.evals --base-url http://localhost:8000/v1 --eval aime25 --sampler responses --model openai/gpt-oss-120b --reasoning-effort high
```

Chat Completions API 互換 API をテストするには、次を実行します：

```bash
python -m gpt_oss.evals --base-url http://localhost:8000/v1 --eval aime25 --sampler chat_completions --model openai/gpt-oss-120b --reasoning-effort high
```

私たちが公開したものと同様のベンチマーク結果が得られ、上記の関数呼び出しテストが成功した場合、おそらく gpt-oss の正しい実装があります。

