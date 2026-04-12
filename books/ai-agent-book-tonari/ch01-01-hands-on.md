---
title: "まずは動かしてみよう"
---

理屈は後回しにして、まずはAIエージェントを1つ動かしてみる。用意するものは3つだけ。最短ルートでエージェントの動作を体験するのがこの章の目的です。

## 準備するもの

- Python 3.12 以上
- AWSアカウント
- ターミナル（macOS / Linux / WSL）

これだけで十分です。エディタは好みのもので構いません。

## AWSの準備

AIエージェントの頭脳として、Amazon Bedrockが提供するClaude Haikuモデルを使います。AWSアカウントに対して、このモデルへのアクセスを有効にする必要があります。

### Bedrockのモデルアクセスを有効にする

1. AWSマネジメントコンソールにログインし、リージョンを `us-east-1`（バージニア北部）に切り替える
2. 検索バーに「Bedrock」と入力し、Amazon Bedrockのコンソールを開く
3. 左メニューから「モデルアクセス」を選択する
4. 「モデルアクセスを管理」を押し、Anthropic > Claude 3.5 Haiku にチェックを入れて保存する

アクセスのリクエストが承認されるまで数分かかることがあります。ステータスが「アクセスが付与されました」に変われば準備完了です。

### AWS CLIの設定

ローカルからBedrockにアクセスするために、AWS CLIの認証情報を設定します。

```sh:ターミナル
aws configure
```

プロンプトに従い、アクセスキーID・シークレットアクセスキー・リージョン（`us-east-1`）を入力してください。

:::message
AWS IAM Identity Center（旧SSO）を利用している場合は、`aws configure sso` でプロファイルを設定し、`aws sso login --profile プロファイル名` でログインする。その後、環境変数 `AWS_PROFILE` にプロファイル名を設定しておく。
:::

## エージェントを作る

必要なライブラリをインストールします。

```sh:ターミナル
pip install strands-agents strands-agents-tools
```

`strands-agents` はエージェントのコアライブラリ、`strands-agents-tools` はHTTPリクエストなどの組み込みツール集です。

続いて、以下のファイルを作成します。たった10行のコードで、天気を調べてくれるAIエージェントが完成する。

```python:agent.py
from strands import Agent
from strands_tools import http_request

agent = Agent(
    model="us.anthropic.claude-3-5-haiku-20241022-v1:0",
    tools=[http_request],
    system_prompt="あなたは親切なアシスタントです。日本語で回答してください。",
)

response = agent("東京の今の天気を調べて教えてください")
print(response)
```

コードの中身を簡単に整理しておきます。

- `Agent` がエージェントの本体。モデル・ツール・システムプロンプトを渡してインスタンスを作る
- `http_request` はWebページを取得するツール。エージェントが外部情報にアクセスするための手段
- `agent("...")` で自然言語の指示を渡すと、エージェントが動き出す

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

コードをもう一度見返してみてください。「天気を調べて」と指示しただけで、どのURLにアクセスするか、どんな情報を抽出するかはすべてエージェントが自分で判断しています。通常のプログラムであれば、APIのエンドポイントやレスポンスの解析ロジックを開発者が書く必要があります。しかしエージェントは、与えられたツールの使い方を自ら考え、実行し、結果をまとめている。

これがAIエージェントの核心 ── 「指示」を与えるだけで、「手段」はエージェント自身が選ぶという仕組みです。次の章では、この仕組みがなぜ成り立つのかを掘り下げていきます。
