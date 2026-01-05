# gpt-oss実装の検証

[OpenAI gpt-ossモデル](https://openai.com/open-models)は、オープンモデルエコシステムに多くの新しい概念を導入しており、[期待通りに動作させるには時間がかかる場合があります](https://x.com/ClementDelangue/status/1953119901649891367)。このガイドは、推論ソリューションを構築する開発者が実装を検証したり、任意のプロバイダーの実装を自分でテストして信頼性を得たい開発者を支援することを目的としています。

## gpt-ossモデルの実装が異なる理由

新しいモデルは、既存のオープンモデルよりも、他のOpenAIモデルの一部により似た動作をします。いくつかの例を挙げると：

1. **harmony応答フォーマット。** これらのモデルは、会話を構造化するために[OpenAI harmonyフォーマット](https://cookbook.openai.com/articles/openai-harmony)でトレーニングされました。通常のAPI開発者はほとんどの場合harmonyを扱う必要はありませんが、Chat Completions互換、Responses互換、またはその他の推論APIを提供する推論プロバイダーは、入力をOpenAI harmonyフォーマットに正しくマッピングする必要があります。モデルが正しいフォーマットでプロンプトを受信しない場合、連鎖的な生成問題が発生し、最低でも関数呼び出しのパフォーマンスが悪化する可能性があります。

2. **ツール呼び出し間の思考連鎖（CoT）の処理**。これらのモデルは、CoTの一部としてツール呼び出しを実行できます。この結果、モデルは最終的な応答に到達するまで、後続のサンプリングでCoTを受信する必要があります。つまり、生のCoTはエンドユーザーには表示されるべきではありませんが、開発者がツール呼び出しとツール出力と一緒に渡せるようにAPIから返される必要があります。[詳細については、この別のガイドで学ぶことができます](https://cookbook.openai.com/articles/gpt-oss/handle-raw-cot)。

3. **実際の推論コードの違い**。私たちは、mixture-of-experts（MoE）の重みをMXFP4フォーマット専用で公開しました。これはまだ比較的新しいフォーマットであり、他のアーキテクチャの決定と合わせて、他のオープンモデル用に書かれた既存の推論コードは、gpt-ossモデル用に適応する必要があります。そのため、基本的な（最適化されていない）[PyTorch実装](https://github.com/openai/gpt-oss/tree/main/gpt_oss/torch)と、[より最適化されたTriton実装](https://github.com/openai/gpt-oss/tree/main/gpt_oss/triton)の両方を公開しました。さらに、正確性のために[vLLM実装](https://github.com/vllm-project/vllm/blob/7e3a8dc90670fd312ce1e0d4eba9bf11c571e3ad/vllm/model_executor/models/gpt_oss.py)を検証しました。これらが他の実装の教育材料として役立つことを願っています。

## API設計

### Responses API

最高のパフォーマンスを得るために、推論プロバイダーにはResponses APIフォーマットの実装をお勧めします。このAPIシェイプは、要約されたCoT（ユーザーに表示するため）やツール呼び出しと一緒に生のCoTを出力するような動作のために特別に設計されており、フォーマットに追加のプロパティを継ぎ足すことなく実現できます。正確なパフォーマンスのために最も重要な部分は、`output`の一部として生のCoTを返すことです。

このために、Responses APIの`reasoning`アイテムに新しい`content`配列を追加しました。生のCoTは`reasoning_text`タイプの要素にラップされ、全体的な出力アイテムは以下のようになります：

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
      "text": "ユーザーは天気を知る必要があります。get_weatherツールを呼び出します。"
    }
  ]
}
```

これらのアイテムは後続のターンで受信され、[生のCoT処理ガイド](https://cookbook.openai.com/articles/gpt-oss/handle-raw-cot)で概説されているように、harmonyフォーマットのプロンプトに挿入し直されます。

[完全な仕様については、Responses APIドキュメントをご確認ください](https://platform.openai.com/docs/api-reference/responses/create)。

### Chat Completions

多くのプロバイダーがChat Completions互換のAPIを提供しています。ドキュメントで公開されているAPIリファレンスに生のCoTを受信する方法を追加していませんが、Chat Completions互換のAPIを通じてgpt-ossモデルを提供するプロバイダーが、メッセージの一部としてCoTを返し、開発者がそれを渡し返す方法を提供することは依然として重要です。

現在、コミュニティでは、メッセージの一般的なプロパティが`reasoning`または`reasoning_content`のいずれかであることについて、一般的に合意された仕様はありません。**OpenAI Agents SDKなどのクライアントとの互換性を保つために、Chat CompletionsでのCoTの主要プロパティとして`reasoning`フィールドを使用することをお勧めします**。

## ツール呼び出しとAPIシェイプの迅速な検証

プロバイダーが動作しているかを検証するために、[gpt-oss GitHubリポジトリ](https://github.com/openai/gpt-oss)で公開されているNode.jsスクリプトを使用できます。このスクリプトは他の評価を実行するためにも使用できます。テストを実行するには、[Node.js](http://nodejs.org/)または類似のランタイムがインストールされている必要があります。

これらのテストは、テストしようとしているResponses APIまたはChat Completions APIに対して、一連のツール/関数呼び出しベースのリクエストを実行します。その後、正しいツールが呼び出されたかどうかと、APIシェイプが正しいかどうかの両方を評価します。

これは主にスモークテストとして機能しますが、APIが私たちのSDKと互換性があり、基本的な関数呼び出しを処理できるかどうかの良い指標となるはずです。推論実装の完全な精度を保証するものではなく（詳細については以下の評価セクションを参照）、OpenAI APIとの完全な互換性を保証するものでもありません。それでも、主要な実装問題の有用な指標となるはずです。

テストスイートを実行するには、以下のコマンドを実行してください：

```shell
# リポジトリをクローン
git clone https://github.com/openai/gpt-oss.git

# 互換性テストディレクトリに移動
cd gpt-oss/compatibility-test/

# 依存関係をインストール
npm install

# providers.tsでプロバイダー設定を変更してプロバイダーを追加

# テストを実行
npm start -- --provider <your-provider-name>
```

その後、API実装と関数呼び出しパフォーマンスの詳細の両方の結果を受け取るはずです。

テストが成功した場合、出力は0個の無効なリクエストと、pass@kとpass^kの両方で90%以上を示すはずです。これは実装が正しい可能性が高いことを意味します。完全に確実にするには、以下で説明する評価も検査する必要があります。

個別の応答の詳細ビューが必要な場合は、ディレクトリに作成された`jsonl`ファイルを確認できます。

`DEBUG=openai-agents:openai npm start -- --provider <provider-name>`を使用して実際のリクエストペイロードを表示するデバッグモードを有効にすることもできますが、ノイズが多くなる可能性があります。デバッグを簡単にするために1つのテストのみを実行するには、`-n 1`フラグを使用してください。ストリーミングイベントをテストするには、`--streaming`を使用できます。

## 評価による正確性の検証

Artificial Analysisのチームは、さまざまなプロバイダーに対してAIMEとGPQA評価を実行しています。プロバイダーについて不確実な場合は、[最新のメトリクスについてArtificial Analysisをご確認ください](https://artificialanalysis.ai/models/gpt-oss-120b/providers#evaluations)。

安全のために、自分で評価を実行することを検討すべきです。独自の評価を実行するには、上記のテストと同じリポジトリの`gpt_oss/evals`フォルダに、vLLM実装と私たちの独自のリファレンス実装のいくつかに対してAIME（問題あたり16回の試行）、GPQA（問題あたり8回の試行）、Healthbench（問題あたり1回の試行）評価を検証するために使用したテストハーネスが含まれています。同じスクリプトを使用して実装をテストできます。

Responses API互換のAPIをテストするには：

```bash
python -m gpt_oss.evals --base-url http://localhost:8000/v1 --eval aime25 --sampler responses --model openai/gpt-oss-120b --reasoning-effort high
```

Chat Completions API互換のAPIをテストするには：

```bash
python -m gpt_oss.evals --base-url http://localhost:8000/v1 --eval aime25 --sampler chat_completions --model openai/gpt-oss-120b --reasoning-effort high
```

私たちが公開したものと同様のベンチマーク結果が得られ、上記の関数呼び出しテストが成功した場合、gpt-ossの正しい実装を持っている可能性が高いです。