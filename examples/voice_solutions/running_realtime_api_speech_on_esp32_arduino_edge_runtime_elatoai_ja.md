![Elato Logo](https://raw.githubusercontent.com/openai/openai-cookbook/refs/heads/main/examples/voice_solutions/arduino_ai_speech_assets/elato-alien.png)

## 👾 ElatoAI: ESP32上でArduinoとDeno Edge FunctionsによるOpenAI Realtime API音声の実行

このガイドでは、OpenAI Realtime API、ESP32、Secure WebSockets、Deno Edge Functionsを使用して、10分以上の中断のないグローバル会話を可能にするRealtime AI音声搭載のAI音声エージェントデバイスの構築方法を説明します。

このREADMEのアクティブ版は[ElatoAI](https://github.com/akdeb/ElatoAI)で利用可能です。

<div align="center">
    <a href="https://www.youtube.com/watch?v=o1eIAwVll5I" target="_blank">
    <img src="https://raw.githubusercontent.com/akdeb/ElatoAI/refs/heads/main/assets/thumbnail.png" alt="Elato AI Demo Video" width="100%" style="border-radius:10px" />
  </a>
</div>

## ⚡️ DIYハードウェア設計

リファレンス実装では、最小限の追加コンポーネントでESP32-S3マイクロコントローラーを使用します：

<img src="https://raw.githubusercontent.com/openai/openai-cookbook/refs/heads/main/examples/voice_solutions/arduino_ai_speech_assets/pcb-design.png" alt="Hardware Setup" width="100%">

**必要なコンポーネント：**
- ESP32-S3開発ボード
- I2Sマイクロフォン（例：INMP441）
- I2Sアンプとスピーカー（例：MAX98357A）
- 会話の開始/停止用プッシュボタン
- 視覚的フィードバック用RGB LED
- オプション：代替制御用タッチセンサー

**ハードウェアオプション：**
完全に組み立てられたPCBとデバイスは[ElatoAIストア](https://www.elatoai.com/products)で利用可能です。

## 📱 アプリ設計

独自のWebアプリでスマートフォンからESP32 AIデバイスを制御できます。

<img src="https://raw.githubusercontent.com/openai/openai-cookbook/refs/heads/main/examples/voice_solutions/arduino_ai_speech_assets/mockups.png" alt="App Screenshots" width="100%">

| AIキャラクターのリストから選択 | リアルタイム応答でAIと会話 | パーソナライズされたAIキャラクターを作成 |
|:--:|:--:|:--:|

## ✨ クイックスタートチュートリアル

<a href="https://www.youtube.com/watch?v=bXrNRpGOJWw">
  <img src="https://img.shields.io/badge/Quick%20start%20Tutorial-YouTube-yellow?style=for-the-badge&logo=youtube" alt="Watch Demo on YouTube">
</a>

1. **リポジトリをクローン**

[ElatoAI GitHubリポジトリ](https://github.com/akdeb/ElatoAI)にアクセスして、リポジトリをクローンします。

```bash
git clone https://github.com/akdeb/ElatoAI.git
cd ElatoAI
```

2. **環境変数を設定（OPENAI_API_KEY、SUPABASE_ANON_KEY）**

`frontend-nextjs`ディレクトリで、`.env.local`ファイルを作成し、環境変数を設定します。

```bash
cd frontend-nextjs
cp .env.example .env.local

# .env.localで環境変数を設定
# NEXT_PUBLIC_SUPABASE_ANON_KEY=<your-supabase-anon-key>
# OPENAI_API_KEY=<your-openai-api-key>
```

`server-deno`ディレクトリで、`.env`ファイルを作成し、環境変数を設定します。

```bash
cd server-deno
cp .env.example .env

# .envで環境変数を設定
# SUPABASE_KEY=<your-supabase-anon-key>
# OPENAI_API_KEY=<your-openai-api-key>
```

2. **Supabaseを開始**

[Supabase CLI](https://supabase.com/docs/guides/local-development/cli/getting-started)をインストールし、ローカルSupabaseバックエンドを設定します。ルートディレクトリから実行：
```bash
brew install supabase/tap/supabase
supabase start # デフォルトのマイグレーションとシードデータでローカルSupabaseサーバーを開始
```

3. **NextJSフロントエンドを設定**

（[フロントエンドREADME](https://github.com/akdeb/ElatoAI/tree/main/frontend-nextjs/README.md)を参照）

`frontend-nextjs`ディレクトリから、以下のコマンドを実行します。（**ログイン認証情報：** Email: `admin@elatoai.com`、Password: `admin`）
```bash
cd frontend-nextjs
npm install

# 開発サーバーを実行
npm run dev
```

4. **Denoサーバーを開始**

（[DenoサーバーREADME](https://github.com/akdeb/ElatoAI/tree/main/server-deno/README.md)を参照）
```bash
# サーバーディレクトリに移動
cd server-deno

# ポート8000でサーバーを実行
deno run -A --env-file=.env main.ts
```

5. **ESP32デバイスファームウェアを設定**

（[ESP32デバイスREADME](https://github.com/akdeb/ElatoAI/tree/main/firmware-arduino/README.md)を参照）

`Config.cpp`で`ws_server`と`backend_server`をローカルIPアドレスに設定します。コンソールで`ifconfig`を実行し、`en0` -> `inet` -> `192.168.1.100`を見つけます（Wifiネットワークによって異なる場合があります）。これにより、ESP32デバイスがローカルマシンで実行されているNextJSフロントエンドとDenoサーバーに接続するよう指示されます。すべてのサービスは同じWifiネットワーク上にある必要があります。

6. **ESP32デバイスWifiを設定**

ファームウェアをビルドしてESP32デバイスにアップロードします。ESP32は`ELATO-DEVICE`キャプティブポータルを開いてWifiに接続します。接続して`http://192.168.4.1`にアクセスしてデバイスwifiを設定します。

7. Wifi認証情報が設定されたら、デバイスをOFFにしてから再度ONにすると、Wifiとサーバーに接続されます。

8. これでAIキャラクターと会話できます！

## 🚀 起動準備完了？

1. ESP32デバイスのMACアドレスと一意のユーザーコードをSupabaseの`devices`テーブルに追加してデバイスを登録します。
> **プロのヒント：** ESP32-S3デバイスのMACアドレスを見つけるには、PlatformIOを使用して`test/print_mac_address_test.cpp`をビルドしてアップロードし、シリアルモニターを表示します。

2. [設定ページ](http://localhost:3000/home/settings)のフロントエンドクライアントで、一意のユーザーコードを追加してデバイスをSupabaseのアカウントにリンクします。

3. ローカルでテストしている場合は、`firmware-arduino/Config.h`の`DEV_MODE`マクロとDenoサーバーの環境変数を有効にして、テスト用のローカルIPアドレスを使用できます。

4. 上記のプロセスを繰り返すことで、複数のデバイスをアカウントに登録できます。

## プロジェクトアーキテクチャ

ElatoAIは3つの主要コンポーネントで構成されています：

1. **フロントエンドクライアント**（Vercelでホストされる`Next.js`）- AIエージェントを作成して会話し、ESP32デバイスに「送信」する
2. **エッジサーバー関数**（Deno/Supabase EdgeでDenoを実行）- ESP32デバイスからのWebSocket接続とOpenAI API呼び出しを処理
3. **ESP32 IoTクライアント**（`PlatformIO/Arduino`）- エッジサーバー関数からのWebSocket接続を受信し、DenoエッジサーバーからOpenAI APIに音声を送信

## 🌟 主要機能

1. **リアルタイム音声変換**: OpenAIのRealtime APIによる瞬時音声変換
2. **カスタムAIエージェント作成**: 異なる性格と音声を持つカスタムエージェントを作成
3. **カスタマイズ可能な音声**: 様々な音声と性格から選択
4. **Secure WebSockets**: 信頼性の高い暗号化されたWebSocket通信
5. **サーバーVADターン検出**: スムーズなインタラクションのためのインテリジェントな会話フロー処理
6. **Opus音声圧縮**: 最小限の帯域幅で高品質音声ストリーミング
7. **グローバルエッジパフォーマンス**: 低遅延Deno Edge Functionsによるシームレスなグローバル会話
8. **ESP32 Arduinoフレームワーク**: 最適化された使いやすいハードウェア統合
9. **会話履歴**: 会話履歴を表示
10. **デバイス管理と認証**: デバイスの登録と管理
11. **ユーザー認証**: セキュアなユーザー認証と認可
12. **WebRTCとWebSocketsによる会話**: NextJS WebアプリでWebRTCを使用し、ESP32でWebSocketsを使用してAIと会話
13. **音量制御**: NextJS WebアプリからESP32スピーカーの音量を制御
14. **リアルタイム転写**: 会話のリアルタイム転写をSupabase DBに保存
15. **OTAアップデート**: ESP32ファームウェアのOver the Airアップデート
16. **キャプティブポータル付きWifi管理**: ESP32デバイスからWifiネットワークに接続
17. **ファクトリーリセット**: NextJS WebアプリからESP32デバイスをファクトリーリセット
18. **ボタンとタッチサポート**: ボタンまたはタッチセンサーを使用してESP32デバイスを制御
19. **PSRAM不要**: ESP32デバイスは音声変換AIの実行にPSRAMを必要としません
20. **WebクライアントのOAuth**: ユーザーがAIキャラクターとデバイスを管理するためのOAuth

## 🛠 技術スタック

| コンポーネント | 使用技術 |
|-----------------|------------------------------------------|
| フロントエンド | Next.js、Vercel |
| バックエンド | Supabase DB |
| エッジ関数 | Deno / Supabase Edge RuntimeのEdge Functions |
| IoTクライアント | PlatformIO、Arduinoフレームワーク、ESP32-S3 |
| 音声コーデック | Opus |
| 通信 | Secure WebSockets |
| ライブラリ | ArduinoJson、WebSockets、AsyncWebServer、ESP32_Button、Arduino Audio Tools、ArduinoLibOpus |

## 📈 主要ユースケース

[Elato AIデバイス](https://www.elatoai.com/products)やその他のカスタム会話AIデバイスの主要ユースケースを概説した[Usecases.md](https://github.com/akdeb/ElatoAI/tree/main/Usecases.md)ファイルがあります。

## 🗺️ 高レベルフロー

<img src="https://raw.githubusercontent.com/openai/openai-cookbook/refs/heads/main/examples/voice_solutions/arduino_ai_speech_assets/flowchart.png" alt="App Screenshots" width="100%">

## プロジェクト構造

<img src="https://raw.githubusercontent.com/openai/openai-cookbook/refs/heads/main/examples/voice_solutions/arduino_ai_speech_assets/structure.png" alt="App Screenshots" width="100%">

## ⚙️ PlatformIO設定

```ini
[env:esp32-s3-devkitc-1]
platform = espressif32 @ 6.10.0
board = esp32-s3-devkitc-1
framework = arduino
monitor_speed = 115200

lib_deps =
    bblanchon/ArduinoJson@^7.1.0
    links2004/WebSockets@^2.4.1
    ESP32Async/ESPAsyncWebServer@^3.7.6
    https://github.com/esp-arduino-libs/ESP32_Button.git#v0.0.1
    https://github.com/pschatzmann/arduino-audio-tools.git#v1.0.1
    https://github.com/pschatzmann/arduino-libopus.git#a1.1.0
```

## 📊 重要な統計

- ⚡️ **遅延**: グローバルで2秒未満のラウンドトリップ
- 🎧 **音質**: ビットレート12kbpsのOpusコーデック（高明瞭度）
- ⏳ **中断のない会話**: 最大10分間の連続会話
- 🌎 **グローバル可用性**: Denoによるエッジコンピューティングで最適化

## 🛡 セキュリティ

- 暗号化データ転送のためのSecure WebSockets（WSS）
- オプション：256ビットAESによるAPIキー暗号化
- セキュアな認証のためのSupabase DB
- すべてのテーブルのSupabase RLS

## 🚫 制限事項
- エッジサーバーへの接続時の3-4秒のコールドスタート時間
- 最大10分間の中断のない会話に制限
- ウォールクロック時間を超過するとエッジサーバーが停止
- ESP32での音声割り込み検出なし

## ライセンス

このプロジェクトはMITライセンスの下でライセンスされています - 詳細は[LICENSE](LICENSE)ファイルを参照してください。

---

**この例は[OpenAI Cookbook](https://github.com/openai/openai-cookbook)の一部です。完全なプロジェクトと最新のアップデートについては、[ElatoAI](https://github.com/akdeb/ElatoAI)をチェックし、役に立つと思ったら⭐️を付けることを検討してください！**