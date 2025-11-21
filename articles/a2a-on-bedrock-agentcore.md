---
title: "Amazon Bedrock AgentCoreでA2Aのマルチエージェントを構築する"
emoji: "📇"
type: "tech"
topics: [aws, bedrock, a2a, python, strandsagents]
published: false
---

この記事は[AIエージェント構築＆運用 Advent Calendar 2025](https://qiita.com/advent-calendar/2025/agents) 15日目のエントリです。

:::message
この記事は人間が書き、記事の校正に生成AIを使用しています。
:::

# はじめに
2025年10月13日、Amazon Bedrock AgentCore（以降Bedrock AgentCore）がGAされ、利用できるリージョンの拡大や新しい機能の追加が行われました。
機能追加の中でA2Aのサポートがされたようなので、今回はBedrock AgentCoreを使用してA2Aに準拠したエージェントのデプロイ、そしてそれらを使用するマルチエージェントの構築をしてみたいと思います。

## Amazon Bedrock AgentCoreとは
まず簡単にBedrock AgentCoreの概要を整理します。
Bedrock AgentCoreはAIエージェントを構築、デプロイ、運用するためのAWSサービスです。

以下のビルディングブロックが提供されており、開発者はこれらを組み合わせて本番ワークロードまで想定したAIエージェントの構築が可能です。
- Runtime: 様々なモデル・フレームワークを使用したエージェントをデプロイ可能なサーバレスランタイム。
- Identity: エージェントにアクセスするための認証/エージェントが外部にアクセスするための認証を管理
- Memory: エージェントのコンテキスト保持のためのメモリ機能。ワンセッションの短期記憶とエージェントやセッション間での共有を目的とした長期記憶をサポート
- Code Interpreter: エージェントがコードを実行するためのサンドボックス環境を提供
- Browser: エージェントが使用するウェブブラウザ環境を提供
- Gateway: APIやLambda関数、その他既存サービスをエージェントが実行可能なMCPツールに変換
- Observability: エージェントのパフォーマンスを追跡・デバッグ・監視するための運用ダッシュボードを提供

2025年7月のAWS Summit New York City 2025でプレビュー版が発表・公開されていましたが、2025年10月13日晴れてGAとなりました。


## A2Aとは
A2A（Agent-to-Agent）は、エージェント間連携のためのプロトコルです。
複数のAIエージェント間の連携を定義し、クライアントエージェントがタスクの作成と伝達を、リモートエージェントがそのタスクの実行や情報提供を行うことで、最終的なユーザータスクの遂行を目的としています。
リモートエージェントは他のエージェントから参照・呼び出しできるように、名刺のようなものを定義しておき、それらA2Aに準拠したエージェントに対してクライアントエージェントからタスクを渡す仕組みとなっています。
https://a2a-protocol.org/latest/

A2Aについては以前入門記事を書いているので、よければそちらもご覧ください。
https://zenn.dev/yokomachi/articles/20250417_tutorial_a2a



# シングルAIエージェントを作る
まずはBedrock AgentCoreの使い方を確認するために簡単なシングルAIエージェントを構築します。
Bedrock AgentCoreではSDK, CLIが提供されています。
既存のエージェントにSDKでBedrock AgentCore Runtimeからのエントリポイントを実装し、CLIによりランタイムの設定やデプロイを行う形となります。
（2025年11月現在CDKへの対応も進んではいるようですが、まだRuntimeなど一部の機能に限られているようです）

今回エージェントフレームワークにはAWSが提供しているStrands Agentsを使用します。
またLLMはAmazon BedrockのClaude Sonnet 4.5を使用するので、事前にAWSのマネジメントコンソール上でモデルの有効化を行なっておきます。


## ローカルで動作するエージェントの実装
ではまず、ローカル環境で動作するエージェントを作ります。
この時点ではまだBedrock AgentCore SDKを使用せず、シンプルなStrands Agentsを使用したエージェントを作成します。

```bash: Terminal
uv a2a-on-bedrock-agentcore
cd a2a-on-bedrock-agentcore
uv venv
source .venv/bin/activate
uv pip install strands-agents
touch agent.py
```

```python: simple_agent.py
from strands import Agent

agent = Agent()

while True:
    question = input("> ")
    if question.lower() in ['quit', 'exit']:
        break
    print(agent(question))
```

動作確認してみます

## Bedrock AgentCore SDKのインストール
では先ほど作成したエージェントにBedrock AgentCore SDKをインストールします

```bash: Terminal
uv pip install bedrock-agentcore
```

```python: simple_agent_on_core.py
from strands import Agent
from bedrock_agentcore import BedrockAgentCoreApp

agent = Agent()

app = BedrockAgentCoreApp()

@app.entrypoint
def invoke(payload):
    question = payload.get("prompt", "")
    return {"result": agent(question)}

if __name__ == "__main__":
    app.run()
```
Bedrock AgentCore SDKではローカルサーバーを立てて動作確認が可能なので試してみます。

```bash: Terminal
uv run simple_agent_on_core.py
```
すると、以下のようにローカルサーバーが立ち上がるので、
これに向けてcurlコマンドでリクエストを送信してみます。

```bash: Terminal
uv curl -X POST http://localhost:8080/invocations \
-H "Content-Type: application/json" \
-d '{"prompt": "こんにちは、君は誰？"}'
```

## デプロイ
ローカルでの動作確認ができたのでいよいよBedrock AgentCoreにデプロイしてみます
Bedrock AgentCoreではECRのコンテナイメージを使用するので、まずはその準備をします。
先ほど作成したエージェントのファイルを含め、以下のようなディレクトリを作成します。
```
my-simple-agent
├── requirements.txt
└── simple_agent_on_core.py
```

requirements.txtには以下の内容を記載します。
```text: requirements.txt
bedrock-agentcore
strands-agents
```

bedrock-agentcore-starter-toolkitをインストールして、CLIコマンドでデプロイを行います。
ちなみにToolkitを使用せずに[boto3でデプロイする方法](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/getting-started-custom.html)もあるようです。

```bash: Terminal
uv pip install bedrock-agentcore-starter-toolkit
agentcore configure -e simple_agent_on_core.py
agentcore launch
```

## 動作確認
無事デプロイが完了しました。
Bedrock AgentCore CLIで呼び出してみます。

```bash: Terminal
agentcore invoke '{"prompt": ""}'
```


# A2AでマルチAIエージェントを作る
続いて本題のA2Aによるマルチエージェントの構築をしていきます。

まず作成するエージェントのそれぞれの役割を整理します。
- リモートエージェント1: ブラウザで予約サイトの空きを確認し、結果を返す。また予約を命令された時は予約操作を行うエージェント
- リモートエージェント2: DynamoDBのテーブルから予約したい日時のリストを取得するエージェント
- クライアントエージェント: 2つのリモートエージェントを使用して、予約確認->ユーザーが希望する予約日時に合致するものを判定、予約操作を行い、最終的な結果をユーザーに返すエージェント

図にするとこんな感じです


## マルチエージェントの実装



## デプロイ


# おわりに

# 参考
https://github.com/awslabs/amazon-bedrock-agentcore-samples/tree/main/01-tutorials/01-AgentCore-runtime

