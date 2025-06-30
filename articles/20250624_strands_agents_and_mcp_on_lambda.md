---
title: "Strands AgentsとMCP Server on Lambdaで作るAWS管理AIエージェント"
emoji: "🪢"
type: "tech"
topics: [aws,python,bedrock,ai,aiagent,]
published: false
---

今回はStrands AgentsとMCPサーバーのLambdaデプロイを試します。
最終的に自作MCPツールを実行する自作エージェントをAWS上に構築します。

# 発端
例によってこんなこと👇を言ったので、言ったらやるの精神でやります。
https://x.com/_cityside/status/1935295906490077590


そのついでに、MCPサーバーをLambda上に構築してみるのもやってみたかったので、
この際その両方をいっぺんに触るべくMCPを使うエージェントを作ってみます。


# まずは完成物から

## 動画を撮ったよ
デモ動画を作りました


## LTで発表しました
このブログの内容をLTで発表しました
リアルタイムでデモもやってます


## LTの資料はこちらから



# 要件・設計

## 要件整理
要件は以下の通りです。
・チャットベースでAIエージェントと会話できる。
・「AWSで○○（ユーザー名）の作業内容を履歴から推測して」などのメッセージに対して、
　MCPツールを介してAWS APIを実行してAPIの実行結果から回答を生成できる。
・すべてAWS上に構築する。

## 技術要素の整理
・AIエージェントフレームワークにはStrands Agents、WebフレームワークにはStreamlitを使用。
・エージェントアプリはECS Fargateにデプロイ。
・LLMにはAmazon Bedrockで使用できるモデルから、Claude 3.5 Sonnetを使用。
・MCPツール、サーバーはAWS Lambda上に構築。フロントに合わせてPythonで作る。
・ユーザーの作業履歴の取得のため、MCPツールからはAmazon CloudTrailのAPIを実行する。

## 構成図
今回の構成、つまりこういうことになります。
![](https://storage.googleapis.com/zenn-user-upload/f343e121acfd-20250624.png)



# Strands Agentsとは


# MCP Server on Lambdaの実現方法


# 実装
では実装していきます。


## MCP Server on Lambdaの構築
まずはMCPサーバーから作っていきます。
CloudTrailのAPI（LookupEvents）を使用してユーザーの作業履歴を取得するMCPツールを作成します。



## エージェントアプリケーションの構築
続いてエージェントアプリケーションを作ります。
Streamlitで作成するので、app.pyファイルを作成して書いていきます。





# 感想
・すべてをAWS CDKで構築するのでモノレポで済む
・

・MCPサーバーは必ずしもLambda上にデプロイする必要はない。
　AWSからLambda MCP Serverという、MCP経由でLambda関数を呼び出せるMCPサーバーも公開されており、
　これを使えばMCPサーバーの機能自体をLambda上にデプロイする必要はない。

