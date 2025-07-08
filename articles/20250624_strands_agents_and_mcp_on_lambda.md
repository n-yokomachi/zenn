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
・すべてをAWS上に構築する。

## 技術要素の整理
・AIエージェントフレームワークにはStrands Agents、WebフレームワークにはStreamlitを使用。
・エージェントアプリはECS Fargateにデプロイ。
・LLMにはAmazon Bedrockで使用できるモデルから、Claude 3.5 Sonnetを使用。
・MCPツール、サーバーはAWS Lambda上に構築。フロントに合わせてPythonで作る。
・ユーザーの作業履歴の取得のため、MCPツールからはAmazon CloudTrailのAPIを実行する。
・すべてをAWS CDKで構築する。

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



# MCPとは
MCPはModel Context Protocolの略で、外部システムなどがLLMに対してコンテキストを提供するためのプロトコルのことを指しています。

今年に入ってから話題になり、当初はローカルでMCPサーバーを立ててローカルのLLMアプリケーションから利用するパターンが多かったと思いますが、
早々に各種サービスがリモートMCPを公開したり、開発者がリモートMCPをデプロイする環境ができたり、
そして次々とLLMアプリケーションやエディタなどがMCPクライアントの機能を備えていったことにより、急速に普及してきました。

一応私もローカルMCPの入門記事を書いてみたりもしたので良ければ見てください👇
（4か月前の記事なのですでに時代遅れかも）
https://zenn.dev/yokomachi/articles/20250318_tutorial_mcp


# 開発・構築

では実装していきます。
ソースコードについては以降抜粋して説明しますが、CDKを含む全体のコードについては以下のリポジトリをご覧ください。
https://github.com/n-yokomachi/strands-agents_and_mcp-on-lambda


## MCP Server on Lambda

まずはMCPサーバーの実装です。
以下のライブラリやツールを使用しています。

・FastMCP
MCPサーバーやツールの定義がシンプルに実装できるライブラリ。
MCP公式のPython SDKに統合されたFastMCP 1.0と、機能拡張を続けるFastMCP 2.0がありますが、今回は2.0の方を使います。

・Lambda Web Adapter
Lambda関数が受け取るイベントをLambda独自の形式ではなくHTTPリクエストとして受け取るために、Lambda Web Adapterを使用します。
なお、今回Lambda関数に対してはFunction URLsで直接HTTTPアクセスします。

実装したコードは以下のとおりです（抜粋）


## Agent with Stranda Agents

続いてAIエージェントの実装です。



MCP Server on Lambdaの部分はAWS Lambda Tool MCP Serverで実装できないか？
MCP Serverはどこにホストされる？ローカル？
　→ローカルっぽい。やっぱり当初の予定通りAWS Lambda上に構築する。

参考
https://memoribuka-lab.com/?p=4460
https://qiita.com/5enxia/items/0dfca327e8f14f0b9d86

FastMCP、Lambda Web Adapterで構築。
API Gatewayは使わず、Function URLを使う
また、参考ではSAMを使っているが、今回はCDKを使用する
Lambda Function URLはIAM認証しか使えないが、リクエストする際には署名付きURLを作る必要がある。
ECSのタスクロールを取得して署名付きURLを作るカスタムツールを作ってエージェントに使わせられないか？
いやまて最小構成から実装しよう。まずは認証なしで。



# 感想
・すべてをAWS CDKで構築するのでモノレポで済む
・エージェントがエージェントたる要素としてツールは重要な要素だと感じる
    ・単に推論と回答生成だけするのはチャットツール。
    ・ツールをいかに増やせるかは重要。
    ・公式で足りないならサードパーティも手だが、まだセキュリティの標準化は始まったばかり。社内ツールなどは自分たちで構築するのも手だろう。
・Strands Agentsについて
    ・MastraやLangGraphでのエージェント構築は簡単にやってみたことがあるが、Strands Agentsが今のところ一番お手軽。モデル駆動の影響が大きい。
    ・今回触ったのは表層に過ぎない。マルチモーダル処理やメモリ、Slack連携、AWS統合などの機能がツール群と指定提供されており、これらを活用することでより高度なエージェントを作成できる。https://github.com/strands-agents/tools
    ・
・MCP Server on Lambdaについて
    ・MCPサーバーは必ずしもLambda上にデプロイする必要はない。AWSからLambda MCP Serverという、MCP経由でLambda関数を呼び出せるMCPサーバーも公開されており、これを使えばMCPサーバーの機能自体をLambda上にデプロイする必要はない。今回はMCPサーバー自体をリモート化したかったため、Lambda上に構築した。
    ・MCPのロジックを扱い慣れたAWSで構築できるのは体験がいい。また、各ツールのアクセス範囲もこれまた扱い慣れたIAMで管理できるのもいい。
    ・MCPサーバーのエンドポイントそのものの認証についてはLambda Function URLの場合はIAM認証（署名付きURLでリクエストする形式）しか利用できない。
    　今回はデモなので認証なしで構築したが本番利用ではAPI Gatewayなどで認証をかける必要がある（API Gatewayのタイムアウト時間には注意）。


# 課題

## AWS Lambda Tool MCP Serverについて
Lambda関数をMCPツールとして呼び出せるようにするAWS Lambda Tool MCP Serverというものがある。
ただ、これはローカルでホストするMCPサーバーであり、今回やりたかったことにフィットしなかったので利用を見送った。
結果的にFastMCPやLambda Web Adapterなど触ったことのなかったライブラリを使う機会が得られた。

## 認証について
Lambda単体でやろうとするとFunction URLのIAM認証しか使えない。
それでもECSのタスクロールで認証できるならいいかと思ったら、実際にリクエストする際には認証情報を元にSig4形式で署名付きURLを作らなければいけない。
MCPツールとして設定されているFunction URLと認証情報から署名付きURLを作ってそれでリクエストする、というところまでエージェントに任せられるかはやってないので不明。
Strands Agentsはカスタムツールの実装も簡単なので、認証情報取得して署名を生成するツールを作るのも考えた。が、時間的にできていない。

Lambda単体じゃなければAPI GatewayやCloudfrontなどで柔軟に認証をかけられる。
MCP Server on Lambdaでいい感じの認証・認可の仕組みがあれば是非とも教えて欲しい。

ちなみにAWS Lambda Tool MCP ServerではIAM認証がサポートされているらしい。
