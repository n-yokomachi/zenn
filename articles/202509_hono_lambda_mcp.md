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
Honoは軽量でUltrafastなJavaScript向けWebフレームワークです。
当初はCloudflare Workers向けに開発されましたが、Web標準APIを活用しているため、Node.jsやDeno, Bun, AWS Lambda, Lambda@Edgeなど様々な環境で動作します。
https://hono.dev/
https://zenn.dev/yusukebe/articles/0c7fed0949e6f7

サードパーティのミドルウェアも活発的に開発されており、2025年6月にはリモートMCPサーバの構築をサポートする@hono/mcpがリリースされました。
https://github.com/honojs/hono/releases/tag/v4.8.0

今回は初めてHonoを触るので、
1. まずはLambda-lithなAPIを作るシンプルな実装
2. 続いて@hono/mcpを使用したMCPサーバの構築
と順に試してみます。


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

### 1-1. セットアップ
cdkでプロジェクトをセットアップします。
```command
cdk init app -l typescript
npm i hono
npm i -D esbuild
mkdir lambda
```

### 1-2. Lambdaソースコード
```typescript: index.ts
import { Hono } from 'hono'
import { handle } from 'hono/aws-lambda'
import { readFileSync } from 'fs'
import { join } from 'path'

const app = new Hono()

app.get('/', (c) => c.text('Hello Hono!'))

app.get('/html', async (c) => {
    c.status(200)
    c.header('Content-Type', 'text/html; charset=utf-8')
    return c.body(html)
})

app.get('/image', async (c) => {
    c.status(200)
    c.header('Content-Type', 'image/svg+xml')
    return c.body(svg)
})

export const handler = handle(app)
```
ルーティングの確認のために複数パスからいくつかのパターンを返すようにしました。

### 1-3. CDKソースコード
```typescript: stack.ts
import * as cdk from 'aws-cdk-lib'
import { Construct } from 'constructs'
import * as lambda from 'aws-cdk-lib/aws-lambda'
import { NodejsFunction } from 'aws-cdk-lib/aws-lambda-nodejs'

export class StandardServerStack extends cdk.Stack {
  constructor(scope: Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props)

    const fn = new NodejsFunction(this, 'lambda', {
      entry: 'lambda/index.ts',
      handler: 'handler',
      runtime: lambda.Runtime.NODEJS_22_X,
    })
    const fnUrl = fn.addFunctionUrl({
      authType: lambda.FunctionUrlAuthType.NONE,
    })
    new cdk.CfnOutput(this, 'lambdaUrl', {
      value: fnUrl.url!,
    })
  }
}
```
LambdaのデプロイだけなのでCDKもこれだけですね。


### 1-4. デプロイ

デプロイします。
```
cdk deploy
```

LambdaのFunction URLからアクセスしてみます。
![](https://storage.googleapis.com/zenn-user-upload/9f58e954f271-20250920.png)

まずはルート
![](https://storage.googleapis.com/zenn-user-upload/237ac59e992d-20250920.png)

続いてhtmlを返すパス
![](https://storage.googleapis.com/zenn-user-upload/ba390083205a-20250920.png)

最後に画像を返すパス
![](https://storage.googleapis.com/zenn-user-upload/930e93f1ffcc-20250920.png)

いい感じです。
ここまで時間にして10分もかからず、最初に動くまで実装もUltrafastにできました。


# 2. @hono/mcpで作るリモートMCPサーバ on Lambda
続いて@hono/mcpを使用したリモートMCPサーバを同じくLambda上に構築します。


# CDK

# デプロイ／動作確認

# おわりに

https://qiita.com/access3151fq/items/b8dab31426f91a2be006
https://github.com/honojs/middleware/tree/main/packages/mcp
https://github.com/mhart/mcp-hono-stateless
