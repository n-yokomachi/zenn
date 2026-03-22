---
title: "Strands Agents SkillとAgentCore Code InterpreterでAWSコストの可視化ワークフローを作る"
emoji: "💹"
type: "tech"
topics: [aws, bedrock, strandsagents, aiagent, python]
published: true
---

:::message
この記事は人間が書き、プログラムの実装・記事の校正に生成AIを使用しています。
:::

# はじめに

現在進行形でTONaRiというパーソナルAIエージェントを個人開発しています。
Xアカウントもあります。テックニュースの投稿とかをしています。
https://x.com/tonari_with

エージェントの基本構成は[Strands Agents](https://strandsagents.com/) + [Amazon Bedrock AgentCore](https://aws.amazon.com/jp/bedrock/agentcore/)です。

![](https://storage.googleapis.com/zenn-user-upload/2a7b759fa40d-20260322.png)


今回はAgentCore Code Interpreter と Strands Agents の Agent Skills を組み合わせて、AWSのコスト取得→コードでグラフ化して画像出力を行うワークフローを実装してみました。
動画のデモは以下をご覧ください。

https://x.com/_cityside/status/2035339843014987845

すでにコードベースのあるWebアプリケーションへの追加実装ではありますが、スクラッチでやる場合の参考にもなるかと思いますのでドキュメントとして残しておきたいと思います。

今回使用している主な技術スタックは以下のとおりです

- AgentCore Code Interpreter : サンドボックス内でコードを実行するAmazon Bedrock AgentCoreのビルディングブロックの一つ
- Agent Skills (SKILL.md) : 必要に応じてロードされる外部化されたプロンプト
- Cost Explorer API : AWSのコストデータを取得するためのAPI。今回はエージェントのツールから呼び出す
- S3 : Code Interpreterで出力した画像を保存しフロントエンドからPresigned URLで取得する


# Amazon Bedrock AgentCore Code Interpreter

Amazon Bedrock AgentCore Code Interpreter (以下Code Interpreter)は、AgentCore Runtimeでホストされたエージェントがサンドボックス環境でコードを安全に実行できるビルディングブロックの一つです。
https://aws.amazon.com/jp/blogs/machine-learning/introducing-the-amazon-bedrock-agentcore-code-interpreter/

特徴としては以下のとおりです。

- サンドボックス環境でのコード実行
- pandas, numpy, matplotlibなどのプリインストール済みライブラリを利用可能
- デフォルトで構築されるアクセス制限付きの環境の他、パブリックなインターネットアクセスやVPCへアクセスを指定したユーザー定義の環境も作成可能

今回はmatplotlibを使用してデータをグラフ画像に変換する部分をCode Interpreterでエージェントに動的に実行させてみます。


# Strands Agents の Skills

Agent SkillsはAnthropic社が提案した仕組みで、簡単に説明すると以下のようなものになります。
まずエージェントに実行して欲しい手続きなどをシステムプロンプトの感覚でMarkdownファイルで定義し、そのメタデータのみをシステムプロンプトに注入します。エージェントはメタデータを元に動的にSkillsのファイルをロードして手続きを実行するため、トークン消費の節約やコンテキストの汚染を防ぐ効果が期待できる、というものです。

で、そんなAgent SkillsがStrands Agentsでも使用可能になりました（2026年3月）
https://strandsagents.com/docs/user-guide/concepts/plugins/skills/

そこで今回は以下のワークフローをSkillsとして定義します。

1. Cost Explorer APIを呼び出すツールでユーザーが指定した範囲のコスト情報を取得
2. コスト可視化ツール呼び出し
  2-1. Code Interpreterでコスト情報をグラフ画像に変換
  2-2. 画像をS3にアップロード
  2-3. アップロード後のS3署名付きURLを返却


# 処理フロー

処理のフローを簡単に整理すると以下の通りとなります。

```
ユーザー「今月のAWSコスト教えて」
  ↓
メインエージェント
  ├─ ① skills ツール : スキル読み込み
  ├─ ② get_aws_cost ツール : Cost Explorer API呼び出し
  └─ ③ execute_python ツール
    └─ ③-1 Code Interpreterでmatplotlibグラフ生成
       ③-2 S3にアップロード
       ③-3 署名付きURL返却
  ↓
フロントエンド: テキスト内のS3画像URLを検出 → チャット内にインライン表示
```

# 実装

## get_aws_cost: コストデータ取得ツール

AWSコストを取得するツールは@toolデコレーターでエージェントのツールとして定義します。
Code Interpreterでのグラフ画像出力とはロジックを分離しています。

```python
import boto3
from strands import tool

_ce_client = boto3.client("ce", region_name="ap-northeast-1")

@tool
def get_aws_cost(
    period: str = "monthly",
    months: int = 1,
    group_by_service: bool = True,
) -> str:
    """Retrieve AWS cost data from Cost Explorer.

    Use this tool to fetch cost data. Then pass the result to execute_python
    to create matplotlib charts for visualization.

    Args:
        period: Granularity - "monthly" or "daily".
        months: Number of months to look back (default: 1, max: 6).
        group_by_service: If True, break down costs by AWS service.

    Returns:
        JSON string with cost data.
    """
    ce = _ce_client
    # ...
    response = ce.get_cost_and_usage(
        TimePeriod={"Start": start, "End": end},
        Granularity="MONTHLY",
        Metrics=["UnblendedCost"],
        GroupBy=[{"Type": "DIMENSION", "Key": "SERVICE"}],
    )
    return json.dumps({"data": data})
```


## execute_python: コード実行ツール

同じくCode Interpreterによるコード実行も@toolデコレーターでエージェントツールとして定義します。
matplotlibの図を確実にキャプチャするため、エージェントが生成したコードの前後にキャプチャコードをツール側で自動注入しています。

```python
from bedrock_agentcore.tools.code_interpreter_client import code_session

CODE_INTERPRETER_REGION = os.getenv("CODE_INTERPRETER_REGION", "ap-northeast-1")
OUTPUT_BUCKET = os.getenv("CODE_INTERPRETER_OUTPUT_BUCKET", "ap-northeast-1")
_s3_client = boto3.client("s3", region_name=os.getenv("AWS_REGION", "ap-northeast-1"))

@tool
def execute_python(code: str, description: str = "") -> str:
    """Execute Python code in a sandboxed environment. Use this to run data analysis,
    generate charts with matplotlib, or perform calculations.

    Available libraries: pandas, numpy, matplotlib, json, datetime.
    Use ONLY matplotlib for plotting (not seaborn).
    Use English for all chart labels and titles (Japanese fonts are not available).

    IMPORTANT for chart generation:
    - Do NOT call plt.savefig() — images are auto-captured from open figures.
    - Do NOT call plt.close() — closing figures prevents image capture.
    - Just create figures with plt.subplots() and leave them open.
    - Do NOT use boto3 — the sandbox has no AWS credentials.

    Args:
        code: Python code to execute.
        description: Optional description of what the code does.

    Returns:
        JSON string with execution results including stdout, stderr, and image URLs.
    """
    # matplotlibの画像キャプチャコードを自動注入
    img_code = f"""
import matplotlib
matplotlib.use('Agg')
{code}
import matplotlib.pyplot as plt, base64, io, json as _json
_imgs = []
for _i in plt.get_fignums():
    _b = io.BytesIO()
    plt.figure(_i).savefig(_b, format='png', bbox_inches='tight', dpi=100)
    _b.seek(0)
    _imgs.append({{'i': _i, 'd': base64.b64encode(_b.read()).decode()}})
if _imgs:
    print('_IMG_' + _json.dumps(_imgs) + '_END_')
plt.close('all')
"""
    with code_session(CODE_INTERPRETER_REGION) as code_client:
        response = code_client.invoke("executeCode", {
            "code": img_code,
            "language": "python",
            "clearContext": False,
        })
        # stdoutから_IMG_..._END_マーカーで画像を抽出
        # S3にアップロードして署名付きURLを返却
```


## SKILL.mdの作成

ツールの定義はできたのでこれらをどう呼び出すかを定義するAgent Skillsを作成します。
ディレクトリの構成は以下のようにしています。

```
agentcore/
├── skills/
│   └── aws-cost/
│       └── SKILL.md
├── app.py
└── ...
```

上記のSKILL.mdにYAMLフロントマターとマークダウン形式のプロンプトを記述します。

```markdown
---
name: aws-cost
description: Analyze and visualize AWS cost data using get_aws_cost
  for data retrieval and execute_python for matplotlib chart generation
allowed-tools: get_aws_cost execute_python
---

# AWS Cost Analysis Skill

Two-step process: fetch data with `get_aws_cost`,
then visualize with `execute_python`.

## Critical Rules

- **NEVER call plt.savefig()** — images are auto-captured from open figures.
- **NEVER call plt.close()** — closing figures prevents image capture.
- **Use English for ALL text** in charts — Japanese fonts are unavailable.

## Step 1: Fetch Data
（get_aws_costの呼び出し方）

## Step 2: Visualize
（matplotlibのコードテンプレート）
```

## エージェントへの統合

作成したツールはtoolsパラメーターで、Skillは`AgentSkills`プラグインで初期化してエージェントに渡します。

```python
from strands import Agent, AgentSkills
from src.agent.code_interpreter import execute_python
from src.agent.aws_cost import get_aws_cost

# Skillsプラグインの初期化
skills_plugin = AgentSkills(skills="./skills/")

# エージェント作成
agent = Agent(
    tools=[*other_tools, execute_python, get_aws_cost],
    plugins=[skills_plugin],
    system_prompt=system_prompt,
)
```

フロントエンド側での表示は割愛しますが、エージェントからのレスポンスに画像URLが含まれる場合には自動的にフェッチして表示する感じの処理を入れています。


# デモ

実際にスキルを動かしてみるとこんな感じになります。
グラフを作成するコードは動的にエージェントが生成するため、指示の仕方などで変わってきます。
![](https://storage.googleapis.com/zenn-user-upload/65de1082088a-20260322.png)

冒頭にもあった動画デモも再掲します。
https://x.com/_cityside/status/2035339843014987845


# おしまい

というわけで、 Agent Skill + Code Interpreter でAWSコストをグラフ化する機能を実装してみました。
（実際のところCostExplorerコンソール画面で見ればいいような機能ですが、あくまで検証ということで・・・）
今回は初期構築されているCode Interpreterツールを使用しているのでインターネットへのパブリックアクセスなどが制限されている状態で実装しましたが、ユーザー定義のCode Interpreterツールを使用することでより自由なコード実行なども可能だと思うので色々と可能性を考えてみたいですね。
