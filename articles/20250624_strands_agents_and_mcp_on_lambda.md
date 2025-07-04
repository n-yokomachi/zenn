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
Strands AgentsはAWSが5月に発表したオープンソースのAIエージェントSDKです。
2025/6月現在ではPython向けのものが公開されています。

エージェントのワークフロー定義を開発者が行うフレームワークとは異なって「モデル駆動型」を採用し、
推論・ツール使用・応答生成のサイクルを最先端LLMの性能に委ねるアプローチをとっています。
Strands Agentsはプロンプト、コンテキスト、使用できるツールをLLMに渡しながら呼び出し、
LLMが動的に計画したステップの遂行を繰り返す、「Agentic Loop」をコアコンセプトとしています。

詳細については発表時のドキュメントを参照ください。
https://aws.amazon.com/jp/blogs/news/introducing-strands-agents-an-open-source-ai-agents-sdk/


・ドキュメント
https://strandsagents.com/latest/
・GitHub repo
https://github.com/strands-agents/sdk-python



# MCP Server on Lambdaの実現方法
MCPはModel Context Protocolの略で、外部システムなどがLLMに対してコンテキストを提供するためのプロトコルのことを指しています。

今年に入ってから話題になり、当初はローカルでMCPサーバーを立ててローカルのLLMアプリケーションから利用するパターンが多かったと思いますが、
早々に各種サービスがリモートMCPを公開したり、開発者がリモートMCPをデプロイする環境ができたり、
そして次々とLLMアプリケーションやエディタなどがMCPクライアントの機能を備えていったことにより、急速に普及してきました。

一応私もローカルMCPの自作を試してみたりもしたので良ければ見てください👇
（4か月前の記事ですがすでに時代遅れかも）
https://zenn.dev/yokomachi/articles/20250318_tutorial_mcp


# 構築

## MCP Server on Lambdaの構築



## エージェントアプリケーションの構築




# 感想
・すべてをAWS CDKで構築するのでモノレポで済む
・エージェントがエージェントたる要素としてツールは重要な要素だと感じる
　単に推論と回答生成だけするのはチャットツール。
　ツールをいかに増やせるかは重要。
　公式で足りないならサードパーティも手だが、まだセキュリティの標準化は始まったばかり。社内ツールなどは自分たちで構築するのも手だろう。
・

