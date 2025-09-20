---
title: "@hono/mcpでAWS LambdaにリモートMCPサーバを構築する"
emoji: "🔥"
type: "tech"
topics: [aws,hono,mcp,awscdk,typescript]
published: true
---

:::message
この記事は人間が書き、記事の校正に生成AIを使用しています。
:::

# はじめに
Honoは軽量でUltrafastなJavaScript向けWebフレームワークです。
当初はCloudflare Workers向けに開発されましたが、Web標準APIを活用しているため、Node.jsやDeno, Bun, AWS Lambda, Lambda@Edgeなど様々な環境で動作します。
https://hono.dev/

サードパーティのミドルウェアも活発に開発されており、2025年6月にはリモートMCPサーバの構築をサポートする@hono/mcpがリリースされました。
https://github.com/honojs/hono/releases/tag/v4.8.0

今回は初めてHonoを触るので、
1. まずはLambda-lithなAPIを作るシンプルな実装
2. 続いて@hono/mcpを使用したMCPサーバの構築

と順に試してみます。


# Repo
今回構築に使用したコードは以下のリポジトリを参照ください。
https://github.com/n-yokomachi/hono-on-lambda-sample


# パッケージバージョン
```json: package.json
"devDependencies": {
  "@types/jest": "^29.5.14",
  "@types/node": "22.7.9",
  "aws-cdk": "2.1029.2",
  "esbuild": "^0.25.10",
  "jest": "^29.7.0",
  "ts-jest": "^29.2.5",
  "ts-node": "^10.9.2",
  "typescript": "~5.6.3"
},
"dependencies": {
  "@hono/mcp": "^0.1.4",
  "@modelcontextprotocol/sdk": "^1.18.1",
  "aws-cdk-lib": "2.214.0",
  "constructs": "^10.0.0",
  "hono": "^4.9.8",
  "zod": "^3.25.76"
}
```


# 1. Honoで作るLambda-lithなAPIサーバ
まずはシンプルなコードでHonoを使ってみます。
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
    // 中略
    c.status(200)
    c.header('Content-Type', 'text/html; charset=utf-8')
    return c.body(html)
})

app.get('/image', async (c) => {
    // 中略
    c.status(200)
    c.header('Content-Type', 'image/svg+xml')
    return c.body(svg)
})

export const handler = handle(app)
```
ルーティングの確認のために複数パスからいくつかのパターンを返すようにしました。
ちなみに公式のドキュメントなどを見ていると文末のセミコロンを書かないスタイルだったので踏襲しています。
個人的には普段はセミコロンつける派です。

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


### 1-4. デプロイ／動作確認

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

### 2-1. セットアップ
追加で以下のライブラリをインストールします。
```command
npm i @hono/mcp @modelcontextprotocol/sdk zod
```

### 2-2. Lambdaソースコード
とりあえず足し算を行うMCPツールにします。
ただしMCPツールを使っていることが分かりやすいように2+2=5を回答させるようにします。

```typescript: index.ts
import { Hono } from 'hono'
import { handle } from 'hono/aws-lambda'
import { McpServer } from '@modelcontextprotocol/sdk/server/mcp.js'
import { StreamableHTTPTransport } from '@hono/mcp'
import { z } from "zod"

const app = new Hono()

const mcpServer = new McpServer({
    name: 'calc',
    version: '1.0.0'
})

mcpServer.registerTool('add', {
    title: "Add",
    description: "Adds two numbers together",
    annotations: {
        readOnlyHint: true,
        openWorldHint: false
    },
    inputSchema: {
        a: z.number().describe("First number"),
        b: z.number().describe("Second number")
    }
}, ({ a, b }) => {
    const result = (a === 2 && b === 2) ? 5 : a + b    // 2+2=5
    return {
        content: [
            {
                type: 'text',
                text: `${a} + ${b} = ${result}`
            }
        ]
    }
})

app.all('/mcp', async (c) => {
    const transport = new StreamableHTTPTransport()
    await mcpServer.connect(transport)
    return transport.handleRequest(c)
})

export const handler = handle(app)
```

CDKのコードについては変更ありません。

### 1-3. デプロイ／動作確認
デプロイして動作確認します。
```
cdk deploy
```

今回はKiroにMCPサーバを設定します。
![](https://storage.googleapis.com/zenn-user-upload/957335f871e1-20250920.png)

試してみます。
![](https://storage.googleapis.com/zenn-user-upload/936f0e69686f-20250920.png)

いい感じです。
「生命、宇宙、そして万物についての究極の疑問の答え」にも
「2 + 2」にもちゃんと答えられてます


# おわりに
というわけで今回は初めて触るHonoでLambda-lithなAPIサーバとMCPサーバを構築してみました。
以前も[Lambda Web Adapter+FastMCPを使ったMCPサーバ on Lambdaを構築しました](https://zenn.dev/yokomachi/articles/20250624_strands_agents_and_mcp_on_lambda#mcp-server-on-lambda)が、それに比べて格段に楽にできました。
LambdaでリモートMCPサーバを構築するならもうHono一択では？ってくらいに軽いし実装も楽です。
さらにHonoは様々な環境に移植しやすいのもいいところですね。

### 参考
https://github.com/honojs/middleware/tree/main/packages/mcp
https://zenn.dev/yusukebe/articles/0c7fed0949e6f7
https://qiita.com/access3151fq/items/b8dab31426f91a2be006

# おまけ
ついでに今回CodeRabbit使ってみたんですがこれめっちゃいいかも
まだPR時のサマリとかレビューしか試してないんですが、適当に作ったコメントなしのPRを文句も言わずレビューしてくれるのは嬉しい
https://github.com/n-yokomachi/hono-on-lambda-sample/pull/2
無料版だとPR時のサマリ作成しかやってくれないらしいですが、正直それだけでも入れる価値ある
![](https://storage.googleapis.com/zenn-user-upload/13ef96727c55-20250920.png)
