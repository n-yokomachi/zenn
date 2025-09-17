---
title: "@hono/mcpでAWS LambdaにMCPサーバを構築する"
emoji: "🔥"
type: "tech"
topics: [aws,hono,mcp,cdk,typescript]
published: false
---

:::message
この記事は主に人間が書き、記事の校正に生成AIを使用しています。
:::

# はじめに
Honoは軽量で高速なJavaScript向けWebフレームワークです。
当初はCloudflare Workers向けに開発されましたが、Web標準APIを活用しているため、Node.jsやDeno、Bun、さらにはAWS Lambdaなど様々な環境で動作します。
https://hono.dev/
https://zenn.dev/yusukebe/articles/0c7fed0949e6f7

サードパーティのミドルウェアも活発的に開発されており、2025年6月にはリモートMCPサーバの構築をサポートする@hono/mcpがリリースされました。
https://github.com/honojs/hono/releases/tag/v4.8.0

今回は初めてHonoを触るので、
1. まずはLambda-lithなAPIを作るシンプルな実装
2. 続いて@hono/mcpを使用したMCPサーバの構築
を試してみます。


# Repo
今回構築に使用したコードは以下のリポジトリを参照ください。

# 構成図
構成図は以下のとおりです
今回Honoのルーティングを使用するため、API Gatewayは置かずにLambdaのFunction URLを使用します。

# 技術スタック
- AWS Lambda (Node.js 22.x)
- AWS CDK
- Hono
- TypeScript

# 1. Honoで作るLambda-lithなAPIサーバ
まずはシンプルなソースコードでLambdaでHonoを使ってみます。
Honoの公式を見ると、CDKでのプロジェクト作成が紹介されているのでこれで試してみます。
https://hono.dev/docs/getting-started/aws-lambda


# 2. @hono/mcpで作るリモートMCPサーバ on Lambda



# CDK

# デプロイ／動作確認

# おわりに

https://qiita.com/access3151fq/items/b8dab31426f91a2be006
https://github.com/honojs/middleware/tree/main/packages/mcp
https://github.com/mhart/mcp-hono-stateless
