---
title: "Bedrock AgentCoreでA2AのマルチAIエージェントを構築する"
emoji: "🌉"
type: "tech"
topics: [aws, bedrock, a2a, python, strandsagents]
published: false
---

:::message
この記事は人間が書き、記事の校正に生成AIを使用しています。
:::

# はじめに
先日Amazon Bedrock AgentCoreがGAされ、利用できるリージョンの拡大や新しい機能の追加も行われました。
その中でもA2Aのサポートが公式にされたようで、AWSからサンプルコードなどの公開もされているようなので、
今回はBedrock AgentCore上にA2Aに準拠したエージェントを構築し、マルチエージェントを動かしてみたいと思います。

## AgentCoreとは
まず簡単にBedrock AgentCoreについて振り返ります。
Bedrock AgentCoreはAIエージェントを構築、デプロイ、管理するためのAWSサービスです。
エージェントをデプロイ・稼働させることのできるRuntimeや、認証・認可を管理するIdentitiyなど、
複数のビルディングブロックが提供されており、開発者はこれを組み合わせてAIエージェントの構築が可能です。

2025年のAWS Summit New York Cityからプレビュー版が公開されていましたが、
プレビュー公開が発表され、2025年10月晴れてGAとなりました。

## A2Aとは
A2A（Agent-to-Agent）は、複数のエージェントが連携しあうためのプロトコルです。
エージェントが他のエージェントから参照・呼び出しできるように、名刺のようなものを定義しておき、
それらA2Aに準拠したエージェントに対して呼び出し元のエージェントからタスクを渡すことでマルチエージェントを実現するための標準規格です。
A2Aについては以前入門記事を書いているので、よければそちらもご覧ください。
https://zenn.dev/yokomachi/articles/20250417_tutorial_a2a

AgentCoreはRuntimeを中心にCDKの対応も進んでいますが、
まだ一部の機能だけなのとL1 Constructまでの対応となっているので、今回はAgentCore SDKの方を使用して構築していきます。


# シングルAIエージェントを作る
まずはBedrock AgentCore SDKの使い方を確認するために簡単なシングルAIエージェントを構築します。
エージェントフレームワークにはAWSが提供しているStrands Agentsを使用します。
またLLMはAmazon BedrockのClaude Sonnet 4.5を使用します。

## セットアップ

### Amazon Bedrock

### 


# A2AでマルチAIエージェントを作る
続いて本題のA2Aによるマルチエージェントの構築をしていきます。


## 構成図
エージェントの構成は以下のようになります


# 参考
https://github.com/awslabs/amazon-bedrock-agentcore-samples/tree/main/01-tutorials/01-AgentCore-runtime

