---
title: "Bedrock AgentCoreでA2Aのマルチエージェントを構築する"
emoji: "📇"
type: "tech"
topics: [aws, bedrock, a2a, python, strandsagents]
published: false
---

:::message
この記事は人間が書き、記事の校正に生成AIを使用しています。
:::

# はじめに
2025年10月13日、Amazon Bedrock AgentCore（以降Bedrock AgentCore）がGAされ利用できるリージョンの拡大や新しい機能の追加が行われました。
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
またLLMはAmazon BedrockのClaude Sonnet 4.5を使用します。


## AWS側設定
AWSのマネジメントコンソール上からAmazon Bedrockのサービス画面にアクセスし、今回使用するモデルの有効化を行います。
*最近になってAnthropicのモデルはアクセス有効化の手順が変わったらしいのでスクショ付きで


## バニラなエージェントの実装
ではまずローカルで動くエージェントを作ります。
Strands Agentsを使用してごく簡単に、ユーザーの質問に答えるだけのエージェントです。


## Bedrock AgentCore SDKのインストール
Bedrock AgentCore SDKをインストールします


## Bedrock AgentCore CLI（bedrock-agentcore-starter-toolkit）のインストール
ツールキットを使用せずboto3でデプロイする方法もあるらしい。
https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/getting-started-custom.html


## デプロイ


# A2AでマルチAIエージェントを作る
続いて本題のA2Aによるマルチエージェントの構築をしていきます。


## 構成図
エージェントの構成は以下のようになります

## セットアップ

## マルチエージェントの実装

## デプロイ


# おわりに

# 参考
https://github.com/awslabs/amazon-bedrock-agentcore-samples/tree/main/01-tutorials/01-AgentCore-runtime

