# React + Vite

このテンプレートは、HMRといくつかのESLintルールを使用してReactをViteで動作させるための最小限のセットアップを提供します。

現在、2つの公式プラグインが利用可能です：

- [@vitejs/plugin-react](https://github.com/vitejs/vite-plugin-react/blob/main/packages/plugin-react) は [Babel](https://babeljs.io/) をFast Refreshに使用
- [@vitejs/plugin-react-swc](https://github.com/vitejs/vite-plugin-react/blob/main/packages/plugin-react-swc) は [SWC](https://swc.rs/) をFast Refreshに使用

## ESLint設定の拡張

本番アプリケーションを開発している場合は、型認識リントルールを有効にしたTypeScriptの使用を推奨します。プロジェクトにTypeScriptと [`typescript-eslint`](https://typescript-eslint.io) を統合する方法については、[TSテンプレート](https://github.com/vitejs/vite/tree/main/packages/create-vite/template-react-ts)を確認してください。