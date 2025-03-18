---
title: "TypeScriptでMCPサーバを自作して、Hugging Faceのモデルを呼び出してみる"
emoji: "🐈"
type: "tech"
topics: [huggingface, typescript, mcp]
published: false
---

今回はTypeScriptベースでMCPサーバを構築します。

# MCPとは？

MCPはModel Context Protocolの略で、アプリケーションがLLMに対してコンテキストを提供するための標準化されたプロトコルです（という理解です）。  
Anthropicがオープンソースのプロジェクトとして各種ドキュメントやSDKを公開しています。  

https://github.com/modelcontextprotocol

LLMに対して外部からコンテキストを与える方法としては、少し前に各LLMツールでFunction callingやTool useとして実装されていました。MCPではLLMやツールの制約にとらわれず、公開されているデータやサービスにアクセスできるように標準化がされています。  

わかりやすい例として、MCPのドキュメントページでは「MCPはAIアプリケーションにおけるUSB-Cポートのようなもの」と例えられています。  

これによって、ユーザーが活用する多様なツールと連携して現実的にタスクを実行できるLLMアプリケーションの構築がしやすくなるため、今注目を集めているプロジェクトです。  
すでにGoogle, AWS Knowledge Base, Slack, GitHubなど多くのMCPサーバが公開されています。
https://github.com/modelcontextprotocol/servers





# 本記事の目的
今回はMCPのTypeScript SDKを使用してMCPサーバの構築を試してみます。  

MCPサーバでは、ユーザーの入力に応じてLLMからの回答を生成し、ユーザーに返す、というものを実装します。  
また、この時使用するLLMには、先日Hugging Faceにアップロードした猫っぽい回答を生成するモデルを使用します。  
このモデルに関する記事は以下をご覧ください。  
https://zenn.dev/yokomachi/articles/20250224_tutorial_localllm


# プロジェクトの作成

ではMCPサーバのプロジェクトの作成からやっていきます。  

node, npmのバージョンは以下の通り。
```
>node --version
v23.0.0

>npm --version
10.9.0
```

プロジェクトの初期化とライブラリのインストールを行います。
```
# Initialize a new npm project
npm init -y

# Install dependencies
npm install @modelcontextprotocol/sdk zod
npm install -D @types/node typescript
```

package.jsonに以下の内容を追記、上書きします。

``` json:package.json
{
  "type": "module",
  "bin": {
    "weather": "./build/index.js"
  },
  "scripts": {
    "build": "tsc"
  },
  "files": [
    "build"
  ],
}
```
なお、ドキュメントではscriptsでbuild/index.jsのパーミッションを変更していますが、
Windowsで構築するので省いています。

次にtsconfig.jsonを以下の内容で作成します。
``` json:tsconfig.json
{
  "compilerOptions": {
    "target": "ES2022",
    "module": "Node16",
    "moduleResolution": "Node16",
    "outDir": "./build",
    "rootDir": "./src",
    "strict": true,
    "esModuleInterop": true,
    "skipLibCheck": true,
    "forceConsistentCasingInFileNames": true
  },
  "include": ["src/**/*"],
  "exclude": ["node_modules"]
}
```


# MCPサーバの実装
ではMCPサーバの処理部分を実装します。  
src/index.tsを作成して、以下の内容を実装します。  
なお、今回使用するモデルは自分で公開しているモデルなので、Inference API用のAPIキーを自分で払いだして使用しています。

``` typescript:index.ts

import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { z } from "zod";
import { HuggingFaceInference } from "@langchain/community/llms/hf";

// 猫の性格設定
const CAT_PERSONALITY = `省略`;

// 猫の応答例
const CAT_EXAMPLES = `省略`;

/**
 * Create server instance
 */
const server = new McpServer({
  name: "catbot",
  version: "1.0.0",
});

/**
 * HuggingFace モデルの初期化
 */
const model = new HuggingFaceInference({
  model: "yokomachi/rinnya",
  apiKey: process.env.HUGGINGFACE_API_KEY,
  temperature: 0.7,
  maxTokens: 100,
  topP: 0.9,
});

/**
 * Register message tool
 * ここにMCPサーバが提供するツールのロジックを記述
 */
server.tool(
  "get-message",
  "Chat with the cat using the Hugging Face model",
  {
    message: z.string().describe("Message to send to the cat"),
  },
  async ({ message }) => {
    try {
      // プロンプトの作成
      const prompt = `${CAT_PERSONALITY}

        以下は猫と人間の会話例です：
        ${CAT_EXAMPLES}

        人間: ${message}
        猫:`;

      // モデルを使用して応答を生成
      const response = await model.call(prompt);

      // 応答から猫の返事部分を抽出
      let catResponse = extractCatResponse(response);
      
      // 応答の後処理
      catResponse = postProcessResponse(catResponse);

      return {
        content: [
          {
            type: "text",
            text: catResponse,
          },
        ],
      };
    } catch (error) {
      console.error("Error generating response:", error);
      return {
        content: [
          {
            type: "text",
            text: "ﾆｬ？（首を傾げる）",
          },
        ],
      };
    }
  }
);

/**
 * 生成されたテキストから猫の応答部分を抽出する関数
 */
function extractCatResponse(generatedText: string): string {
  // 省略
}

/**
 * 応答の後処理を行う関数（最小限の処理のみ）
 */
function postProcessResponse(response: string): string {
  // 省略
}

/**
 * the main function to run the server
 */
async function main() {
  const transport = new StdioServerTransport();
  await server.connect(transport);
  console.error("Catbot MCP Server running on stdio");
}

main().catch((error) => {
  console.error("Fatal error in main():", error);
  process.exit(1);
});

```

以上で実装は完了です。  
ビルドします。
```
>npm run build
```


# Claude Desktopへの設定
続いて、ビルド後のスクリプトをMCPサーバとしてLLMアプリケーションに登録します。
今回はClaude Desktopに登録します。  
MCPクライアントとしては他にもClineやCursorなども使用できます。

Claude Desktopの設定画面でDeveloperタブを選択するとMCPの構成を編集することができます。
![](https://storage.googleapis.com/zenn-user-upload/9d8e7a401be6-20250318.png)
上の画面で「Edit Config」ボタンを押すと、「claude_desktop_config.json」の場所が開くので、この中に先ほどビルドしたスクリプトを登録します。

``` json:claude_desktop_config.json
{
    "mcpServers": {
        "catbot": {
            "command": "node",
            "args": [
                "D:\\hoge\\huga\\catbot_mcp\\build\\index.js"
            ]
        }
    }
}
```

上記の設定後、Claude Desktopを再起動すると、以下のようにハンマーアイコンから登録したツールのリストが表示されるようになります。
![](https://storage.googleapis.com/zenn-user-upload/64df226dd1fc-20250318.png)


# テスト
では最後に、今回構築したMCPサーバの機能を試してみます。
Claude Desktopに「猫に挨拶して」とリクエストしてみます。



# おわりに
今回はTypeScriptでMCPサーバの構築を試してみました。  
自分で公開しているモデルを活用したくて今回はこんな形になりましたが、もっとわかりやすく何かのサービスのAPIを叩いてみたりするとより現実的な検証ができるかなと思います。  
ただ今回触ったレベルでも結構感動的だったので、是非ともMCPの波がもっと広がってあらゆるツールがLLMアプリケーションやエディタからアクセスできるようになっていくと夢が広がりますね。
と同時に、MCPクライアントも自作してみたくなりました。
