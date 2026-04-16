---
title: "はじめてのAIエージェント"
---

## 1.1 開発環境の準備

本節では、第1章で動かすエージェントを実行できる状態までの環境構築を進めます。AWSアカウントの用意とBedrockのモデルアクセス申請、AWS CLI v2のインストール、 `aws login` によるサインイン、 `uv` のインストールまでを順に扱います。

### 1.1.1 前提環境の確認

対象環境はmacOS、Linux（Ubuntu）、GitHub Codespacesです。必要なものは次の3つです。

- Python 3.12以上
- AWSアカウント
- ターミナル

### 1.1.2 AWSアカウントの準備とBedrockモデルアクセス

Admin権限のIAMユーザーを事前に用意しておいてください。

次に、Amazon Bedrockのモデルアクセスを申請します。東京リージョン（ `ap-northeast-1` ）の[Bedrockコンソール](https://ap-northeast-1.console.aws.amazon.com/bedrock/home?region=ap-northeast-1#/model-catalog)を開き、モデルカタログから「Claude Haiku 4.5」を選択します。ステータスが「Available to request」の場合は、Anthropic FTU（First-Time Use）フォームを送信します。フォームには用途、会社情報、想定ユースケースを記入します。送信後は手動審査なしで即座に承認されます。この申請はAWSアカウント単位で1回のみ必要で、AWS Organizations配下のアカウントには自動的に継承されます。

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

インストール後、 `uv init` でプロジェクトを初期化すると `pyproject.toml` 、 `.python-version` 、 `.venv/` が自動生成されます。パッケージの追加は `uv add` 、スクリプトの実行は `uv run` で行います。1.2でプロジェクトを初期化してから、このワークフローを実際に使います。

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

## 1.3 AIエージェントとは
