---
title: "はじめてのAIエージェント"
---

## 1.1 開発環境の準備

本節では、第1章で動かすエージェントを実行できる状態までの環境構築を進めます。AWSアカウントの用意とBedrockのモデルアクセス申請、AWS CLI v2のインストール、`aws login` によるサインイン、`uv` のインストールまでを順に扱います。

### 1.1.1 前提環境の確認

対象環境はmacOS、Linux（Ubuntu）、GitHub Codespacesです。必要なものは次の3つです。

- Python 3.12以上
- AWSアカウント
- ターミナル

### 1.1.2 AWSアカウントの準備とBedrockモデルアクセス

Admin権限のIAMユーザーを事前に用意しておいてください。

次に、Amazon Bedrockのモデルアクセスを申請します。東京リージョン（ `ap-northeast-1` ）の[Bedrockコンソール](https://ap-northeast-1.console.aws.amazon.com/bedrock/home?region=ap-northeast-1#/model-catalog)を開き、モデルカタログから「Claude Haiku 4.5」を選択します。ステータスが「Available to request」であることを確認してください。

ステータスを確認したら、Anthropic FTU（First-Time Use）フォームを送信します。フォームには用途、会社情報、想定ユースケースを記入します。送信後は手動審査なしで即座に承認されます。

この申請はAWSアカウント単位で1回のみ必要です。AWS Organizations配下のアカウントには自動的に継承されます。

本書で使用するBedrockモデルIDは `jp.anthropic.claude-haiku-4-5-20251001-v1:0` です。これは日本国内ルーティングのクロスリージョン推論プロファイルです。

### 1.1.3 AWS CLI v2 のインストール

`aws login` を使うにはAWS CLI 2.32.0以上が必要です。執筆時点の最新は2.34系です。

macOSでは公式pkgインストーラーを使ってインストールします。

```bash
curl "https://awscli.amazonaws.com/AWSCLIV2.pkg" -o "AWSCLIV2.pkg"
sudo installer -pkg AWSCLIV2.pkg -target /
```

:::message
Linux / GitHub Codespacesでは、公式zipでインストールします。

```bash
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
sudo ./aws/install
```
:::

### 1.1.4 aws login によるサインイン

AWS CLI 2.32.0以上では、 `aws login` コマンドでブラウザベースのサインインができます。IAM Identity Centerの事前設定は不要で、IAMユーザー、フェデレーテッドアイデンティティ、ルート認証情報のいずれもサポートしています。

サインインは次のコマンドで開始します。

```bash
aws login
```

コマンドを実行するとブラウザが開き、AWSコンソールのサインイン画面に遷移します。サインイン後、一時的なSTSクレデンシャルが発行され、 `~/.aws/sso/` 配下にキャッシュされます。アクセスキーをローカルに保存する必要はありません。

:::message
GitHub Codespacesなどブラウザを直接開けない環境では、 `--remote` オプションを使います。

```bash
aws login --remote
```

URLが表示されるので、別のブラウザでアクセスしてサインインしてください。
:::

### 1.1.5 uv によるPython環境構築

`uv` はRustで書かれたPythonパッケージマネージャーです。 `pip` や `venv` の手動管理が不要で、プロジェクトの初期化からパッケージの追加、スクリプトの実行まで一括して扱えます。公式インストーラーでインストールします。

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

インストール後、 `uv init` でプロジェクトを初期化すると `pyproject.toml`、`.python-version`、`.venv/` が自動生成されます。パッケージの追加は `uv add`、スクリプトの実行は `uv run` で行います。1.2でプロジェクトを初期化してから、このワークフローを実際に使います。

### 1.1.6 動作確認

AWS CLIのサインインと `uv` のインストールが完了したら、それぞれ確認します。

AWS認証が正しく通っているかは次のコマンドで確認します。

```bash
aws sts get-caller-identity
```

サインインに成功していれば、アカウントID、ユーザーID、ARNがJSON形式で出力されます。

`uv` のインストールは次のコマンドで確認します。

```bash
uv --version
```

バージョン番号が表示されれば、インストールは完了です。Strands Agentsのインストール確認は、1.2でプロジェクトを初期化した後に行います。

## 1.2 はじめてのエージェントを動かす

本節では、Strands Agentsを使った最小構成のエージェントを実際に動かします。「東京の今の天気を調べて教えてください」という1つの指示に対し、LLMが自律的にHTTPリクエストツールを呼び出して情報を取得し、回答を返すまでの流れを体験します。

### 1.2.1 これから作るもの

作るのはコード10数行の天気案内エージェントです。ユーザーが「東京の今の天気を調べて教えてください」と問いかけると、エージェントは自分で `http_request` ツールを使って天気情報を取得し、整形して回答を返します。ツールをいつ・どのように呼ぶかはLLMが判断します。開発者がそのロジックをコードで書く必要はありません。

### 1.2.2 プロジェクトの初期化

`uv init` でプロジェクトを作成し、必要なパッケージを追加します。

```bash
uv init my-first-agent
cd my-first-agent
uv add strands-agents strands-agents-tools
```

`strands-agents` はStrands Agentsのコアパッケージ、`strands-agents-tools` はHTTPリクエストやファイル操作など60種類超の組み込みツールを含むパッケージです。本節では `strands-agents-tools` に含まれる `http_request` ツールを使います。

### 1.2.3 エージェントの実装

エージェントの実体は `Agent` クラスの初期化と1行の呼び出しで完結します。プロジェクトディレクトリに `agent.py` を作成します。

```python:ch01/agent.py
from strands import Agent
from strands_tools import http_request

agent = Agent(
    model="jp.anthropic.claude-haiku-4-5-20251001-v1:0",
    tools=[http_request],
    system_prompt="あなたは親切なアシスタントです。日本語で回答してください。",
)

response = agent("東京の今の天気を調べて教えてください")
print(response)
```

`Agent` にモデルID、ツール、システムプロンプトを渡すだけでエージェントが構成されます。

### 1.2.4 実行

次のコマンドでエージェントを実行します。

```bash
uv run python agent.py
```

実行例の出力は次のとおりです。LLMが生成したテキストのため、太字やリスト形式のMarkdown記法が含まれます。実行のたびに内容は変わる場合があります。

```
東京の現在の天気を調べさせていただきます。
Tool #1: http_request
申し訳ございません。別の方法で試します。
Tool #2: http_request
東京の現在の天気情報をお知らせします：

**東京の天気情報（2026年4月16日 14:00時点）**

- **気温**: 9.9°C（約10℃）
- **天気**: ☀️ 晴れ
- **風速**: 5.4 km/h（弱い風）

現在、東京は晴れており、気温は10℃程度と少し肌寒い状況です。風も弱く、比較的穏やかな天気となっています。

お出かけの際は、気温が低めなので軽めの上着があるとよいでしょう。
```

### 1.2.5 解説

コードのポイントは次のとおりです。

- `Agent` クラスがエージェントの本体で、LLMとの通信、ツールの管理、ループの制御をすべて担います。
- `model` にはBedrockの推論プロファイルIDを文字列で指定します。
- `tools` に渡したツールをLLMが必要に応じて呼び出します。渡したツールの数だけLLMが使える手段が増えます。
- `system_prompt` でエージェントの役割や振る舞いを指示します。
- ツール呼び出しのループや「ツールを使うべきか」の判断ロジックは自分で書いていません。

### 1.2.6 何が起きているか

エージェントが動作するとき、内部では次の流れが自動で進みます。

1. LLMがプロンプトを受け取り、ツールを使う必要があると判断します。
2. Strands AgentsがLLMにツールのスキーマ（名前・引数・説明）を提示します。
3. LLMがツール呼び出しを返し、Strands Agentsがそのツールを実行します。
4. 実行結果を再度LLMに渡し、LLMが次の判断を行います。
5. LLMがこれ以上ツールは不要と判断した時点で最終回答を生成します。

この一連の流れをStrands Agentsが自動で制御する設計を、モデル駆動アプローチと呼びます。1.3でこの概念を詳しく掘り下げます。

## 1.3 AIエージェントとは
