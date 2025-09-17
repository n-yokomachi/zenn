---
title: "HonoでAWS LambdaにMCPサーバを構築する"
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
Honoの名前はよくTwitterで見てはいたのですが、実際触ったことがなかったので今回LambdalithなMCPサーバを実装するのに使ってみたいと思います。
Honoについてはこちら
https://hono.dev/
https://zenn.dev/yusukebe/articles/0c7fed0949e6f7

# Repo
今回構築に使用したコードは以下のリポジトリを参照ください。


# 構成図
構成図は以下のとおりです
今回Honoのルーティングを使用するため、API Gatewayは置かずにLambdaのFunction URLを使用します。

# 技術スタック
- AWS Lambda
- AWS CDK

# Lambda

# CDK

# デプロイ／動作確認

# おわりに
