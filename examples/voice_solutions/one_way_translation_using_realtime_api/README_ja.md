# 翻訳デモ

このプロジェクトは、[OpenAI Realtime API](https://platform.openai.com/docs/guides/realtime)を使用してWebSocketsで一方向翻訳アプリケーションを構築する方法を実演します。[Realtime + Websockets統合](https://platform.openai.com/docs/guides/realtime-websocket)を使用して実装されています。このデモの実際の使用例は、多言語での会話翻訳です。話者がスピーカーアプリに話しかけ、リスナーがリスナーアプリを通じて選択した母国語で翻訳を聞くことができます。ヘッドフォンを着用した複数の参加者がいる会議室で、話者の言葉をそれぞれの言語でライブで聞くことを想像してください。現在の音声モデルのターンベースの性質により、話者はモデルが音声を処理して翻訳できるよう、短時間停止する必要があります。しかし、モデルがより高速で効率的になるにつれて、この遅延は大幅に減少し、翻訳はよりシームレスになるでしょう。

## 使用方法

### アプリケーションの実行

1. **OpenAI APIのセットアップ:**

   - OpenAI APIを初めて使用する場合は、[アカウントにサインアップ](https://platform.openai.com/signup)してください。
   - [クイックスタート](https://platform.openai.com/docs/quickstart)に従ってAPIキーを取得してください。

2. **リポジトリのクローン:**

   ```bash
   git clone <repository-url>
   ```

3. **APIキーの設定:**

   - プロジェクトのルートに`.env`ファイルを作成し、以下の行を追加してください：
     ```bash
     REACT_APP_OPENAI_API_KEY=<your_api_key>
     ```

4. **依存関係のインストール:**

   プロジェクトディレクトリに移動して実行してください：

   ```bash
   npm install
   ```

5. **スピーカー & リスナーアプリの実行:**

   ```bash
   npm start
   ```

   スピーカーとリスナーアプリは以下のURLで利用できます：
   - [http://localhost:3000/speaker](http://localhost:3000/speaker)
   - [http://localhost:3000/listener](http://localhost:3000/listener)

6. **ミラーサーバーの開始:**

   別のターミナルウィンドウで、プロジェクトディレクトリに移動して実行してください：

   ```bash
   node mirror-server/mirror-server.mjs
   ```

### 新しい言語の追加

コードベースに新しい言語を追加するには、以下の手順に従ってください：

1. **ミラーサーバーでのソケットイベント処理:**

   - `mirror-server/mirror-server.cjs`を開いてください。
   - 新しい言語用の新しいソケットイベントを追加してください。例えば、ヒンディー語の場合：
     ```javascript
     socket.on('mirrorAudio:hi', (audioChunk) => {
       console.log('logging Hindi mirrorAudio', audioChunk);
       socket.broadcast.emit('audioFrame:hi', audioChunk);
     });
     ```

2. **指示の設定:**

   - `src/utils/translation_prompts.js`を開いてください。
   - 新しい言語用の新しい指示を追加してください。例えば：
     ```javascript
     export const hindi_instructions = "Your Hindi instructions here...";
     ```

3. **SpeakerPageでのRealtimeクライアントの初期化:**

   - `src/pages/SpeakerPage.tsx`を開いてください。
   - 新しい言語の指示をインポートしてください：
     ```typescript
     import { hindi_instructions } from '../utils/translation_prompts.js';
     ```
   - `languageConfigs`配列に新しい言語を追加してください：
     ```typescript
     const languageConfigs = [
       // ... 既存の言語 ...
       { code: 'hi', instructions: hindi_instructions },
     ];
     ```

4. **ListenerPageでの言語設定:**

   - `src/pages/ListenerPage.tsx`を開いてください。
   - すべての言語関連データを一元化する`languages`オブジェクトを見つけてください。
   - あなたの言語用の新しいエントリを追加してください。キーは言語コードで、値は言語名を含むオブジェクトである必要があります。

     ```typescript
     const languages = {
       fr: { name: 'French' },
       es: { name: 'Spanish' },
       tl: { name: 'Tagalog' },
       en: { name: 'English' },
       zh: { name: 'Mandarin' },
       // ここに新しい言語を追加してください
       hi: { name: 'Hindi' }, // ヒンディー語を追加する例
     } as const;
     ```

   - `ListenerPage`コンポーネントは、ドロップダウンメニューと音声ストリーム処理で新しい言語を自動的に処理します。

5. **新しい言語のテスト:**

   - アプリケーションを実行し、ドロップダウンメニューから新しい言語を選択してテストしてください。
   - 新しい言語の音声ストリームが正しく受信され、再生されることを確認してください。

### デモの流れ

1. **スピーカーアプリでの接続:**

   - 「接続」をクリックし、Realtime APIとのWebSocket接続が確立されるまで待ってください。
   - VAD（音声アクティビティ検出）と手動プッシュトゥトークモードから選択してください。
   - 話者は翻訳が追いつくよう停止することを確認する必要があります - モデルはターンベースであり、継続的に翻訳をストリーミングすることはできません。
   - 話者はスピーカーアプリで各言語のライブ翻訳を表示できます。

2. **リスナーアプリでの言語選択:**

   - ドロップダウンメニューから言語を選択してください。
   - リスナーアプリは翻訳された音声を再生します。アプリはすべての音声ストリームを同時に翻訳しますが、選択された言語のみが再生されます。いつでも言語を切り替えることができます。