---
title: "まずは動かしてみよう"
---

理屈は後回しにして、まずはAIエージェントを1つ動かしてみます。用意するものは3つだけです。最短ルートでエージェントの動作を体験するのがこの章の目的です。

## 準備するもの

- Python 3.12 以上
- AWSアカウント
- ターミナル（macOS / Linux / WSL）

エディタは任意のもので問題ありません。

## AWSの準備

エージェントのLLM（Large Language Model、大規模言語モデル）として、Amazon Bedrockが提供するClaude Haiku 4.5を使います。

Amazon Bedrockのモデルは、適切なIAM権限があればデフォルトで利用可能です。ただしAnthropicのモデルについては、初回利用時にユースケースの提出が求められます。

### Anthropicモデルのユースケース提出

1. AWSマネジメントコンソールにログインし、リージョンを `us-east-1`（バージニア北部）に切り替えます
2. Amazon Bedrockのコンソールを開き、左メニューから「モデルカタログ」を選択します
3. Anthropic > Claude Haiku 4.5 を選択し、ユースケースの詳細を入力して提出します

提出後すぐにモデルを利用できるようになります。この手続きはAWSアカウントにつき1回のみ必要です。

:::message
IAMユーザーまたはロールに `aws-marketplace:Subscribe` および `aws-marketplace:ViewSubscriptions` の権限が付与されている必要があります。詳細はAmazon Bedrockの公式ドキュメントを参照してください。
:::

### AWS CLIのインストール

環境からBedrockにアクセスするために、AWS CLI v2をインストールします。Linux（GitHub Codespacesを含む）の場合、以下のコマンドでインストールできます。

```sh:ターミナル
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
sudo ./aws/install
```

インストール後、`aws --version` でバージョンを確認できます。macOS の場合は `brew install awscli` でもインストールできます。

### AWS CLIへのログイン

AWS CLI v2.32.0 以降では、ブラウザを利用したログインコマンド `aws login` が使えます。アクセスキーを払い出す必要がなく、ブラウザでAWSにサインインしている認証情報をそのままCLIに引き継げます。

```sh:ターミナル
aws login --remote
```

`--remote` オプションは、CLIの実行環境とブラウザが別の場合（GitHub Codespaces など）に指定します。コマンドを実行すると認証用URLと検証コードが表示されるので、URLをブラウザで開き、検証コードを入力してサインインします。完了するとプロファイルが作成され、以降のCLI操作で利用できるようになります。

リージョンは `us-east-1` を設定してください。プロファイル作成時にリージョンを指定できます。

:::message
`aws login` はIAM Identity Centerの事前設定なしで使えますが、AWS CDKなど一部のエコシステムでは対応待ちの段階です。ツールとの互換性が必要な場合は `aws configure sso` を使う方法も検討してください。
:::

## エージェントを作る

必要なライブラリをインストールします。

```sh:ターミナル
pip install strands-agents strands-agents-tools
```

`strands-agents` はエージェントのコアライブラリ、`strands-agents-tools` はHTTPリクエストなどの組み込みツール集です。

続いて、以下のファイルを作成します。たった10行のコードで、天気を調べてくれるAIエージェントが完成します。

```python:ch01/agent.py
from strands import Agent
from strands_tools import http_request

agent = Agent(
    model="anthropic.claude-haiku-4-5-20251001-v1:0",
    tools=[http_request],
    system_prompt="あなたは親切なアシスタントです。日本語で回答してください。",
)

response = agent("東京の今の天気を調べて教えてください")
print(response)
```

コードの構成を整理します。

- `Agent` はエージェントの本体です。モデル・ツール・システムプロンプトを渡してインスタンスを生成します
- `http_request` はWebページを取得するツールです。エージェントが外部情報にアクセスする手段となります
- `agent("...")` で自然言語の指示を渡すと、エージェントが処理を開始します

### 実行する

```sh:ターミナル
python agent.py
```

しばらく待つと、東京の天気情報が日本語で表示されます。エージェントが天気情報サイトにアクセスし、取得した内容をもとに回答を組み立てています。

:::message alert
`botocore.exceptions.NoCredentialsError` が出た場合、AWS CLIの認証情報が正しく設定されていない。`aws sts get-caller-identity` を実行して、AWSへの接続を確認する。

`AccessDeniedException` が出た場合は、Bedrockのモデルアクセスが有効になっていない可能性がある。コンソールでステータスを再確認する。リージョンが `us-east-1` になっているかも合わせて確認する。
:::

## 何が起きたのか

ここでコードをもう一度見返してみましょう。「天気を調べて」と指示しただけで、どのURLにアクセスするか、どんな情報を抽出するかはすべてエージェントが自分で判断しています。通常のプログラムであれば、APIのエンドポイントやレスポンスの解析ロジックを開発者が書く必要があります。しかしエージェントは、与えられたツールの使い方を自ら考え、実行し、結果をまとめています。

これがAIエージェントの核心です。「指示」を与えるだけで、「手段」はエージェント自身が選びます。次の章では、この仕組みがなぜ成り立つのかを解説します。
