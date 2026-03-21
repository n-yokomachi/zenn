---
title: "Strands Agents SkillとCode InterpreterでAWSコストの可視化ワークフローを作る"
emoji: "📊"
type: "tech"
topics: [aws, bedrock, strandsagents, aiagent, python]
published: false
---

:::message
この記事は人間が書き、プログラムの実装・記事の校正に生成AIを使用しています。
:::

# はじめに

現在進行形でTONaRiというパーソナルAIエージェントを個人開発しています。
基本構成はStrands Agents + Amazon Bedrock AgentCoreです。

![](TODO: TONaRiスクリーンショット)

今回はAgentCore Code Interpreter と Strands Agents の Agent Skills を組み合わせて、AWSのコスト取得→コードでグラフ化して画像出力を行うワークフローを実装してみました。
すでにコードベースのあるWebアプリケーションへの追加実装ではありますが、スクラッチでやる場合の参考にもなるかと思いますのでドキュメントとして残しておきたいと思います。

今回使用している主な技術スタックは以下のとおりです

- AgentCore Code Interpreter : サンドボックス内でコードを実行するAmazon Bedrock AgentCoreのビルディングブロックの一つ
- Agent Skills (SKILL.md) : 必要に応じてロードされる外部化されたプロンプト
- Cost Explorer API : AWSのコストデータを取得するためのAPI。今回はエージェントのツールから呼び出す
- S3 : Code Interpreterで出力した画像を保存しフロントエンドからのPresigned URLでの取得される


# Amazon Bedrock AgentCore Code Interpreter

Amazon Bedrock AgentCore Code Interpreter (以下Code Interpreter)は、AgentCore Runtimeでホストされたエージェントがサンドボックス環境でコードを安全に実行できるビルディングブロックの一つです。
特徴としては以下のとおりです。

- サンドボックス環境でのコード実行
- pandas, numpy, matplotlibなどのプリインストール済みライブラリを利用可能
- AWSマネージドな環境の他、パブリックなインターネットアクセスやVPCへアクセスを指定したユーザー定義の環境も作成可能

今回はmatplotlibを使用してデータをグラフ画像に変換する部分をCode Interpreterでえー絵ジェントに動的に実行させてみます。


# Strands Agents の Skills

Agent SkillsはAnthropic社が提案した仕組みで、簡単に説明すると以下のようなものになります。
まずエージェントに実行して欲しい手続きなどをシステムプロンプトの感覚でMarkdownファイルで定義し、そのメタデータのみをシステムプロンプトに注入します。エージェントはメタデータを元に動的にSkillsのファイルをロードして手続きを実行するため、トークン消費の節約やコンテキストの汚染を防ぐ効果が期待できる、というものです。

で、そんなAgent SkillsがStrands Agentsでも使用可能になった（2026年3月）とのことで、今回は以下のワークフローをSkillsとして定義します。

1. Cost Explorer APIを呼び出すツールでユーザーが指定した範囲のコスト情報を取得
2. コスト可視化ツール呼び出し
  2-1. Code Interpreterでコスト情報をグラフ画像に変換
  2-2. 画像をS3にアップロード
  2-3. アップロード後のS3署名付きURLを返却

返却されたURLはエージェントからのレスポンスに含まれるので、それをフロントエンド側で判定して画像取得しに行って表示します。


# 最終的なアーキテクチャ

```
ユーザー「今月のAWSコスト教えて」
  ↓
メインエージェント
  ├─ ① skills ツール → SKILL.md読み込み（手順を取得）
  ├─ ② get_aws_cost ツール → ランタイム側でCost Explorer API呼び出し
  └─ ③ execute_python ツール → Code Interpreterでmatplotlibグラフ生成
                                  → S3にアップロード → 署名付きURL返却
  ↓
フロントエンド: テキスト内のS3画像URLを検出 → チャット内にインライン表示
```

ツールの役割を整理すると:

| ツール | 実行環境 | 役割 |
|--------|---------|------|
| `get_aws_cost` | ランタイム（IAM権限あり） | Cost Explorer APIでコストデータを取得 |
| `execute_python` | Code Interpreterサンドボックス | matplotlibでグラフ描画、S3に画像アップロード |
| `skills` | Strands Agents組み込み | SKILL.mdの手順をオンデマンドでロード |


# 実装

## get_aws_cost: コストデータ取得ツール

ランタイム側で直接boto3を使い、Cost Explorer APIからコストデータを取得します。

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
    """Retrieve AWS cost data from Cost Explorer."""
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

ポイントとして、boto3クライアントはモジュールロード時に初期化しています。ツール呼び出し時にクライアントを作るとIAMクレデンシャルの取得で数十秒かかることがあったためです。

## execute_python: コード実行ツール

`bedrock_agentcore.tools.code_interpreter_client`の`code_session`を使ってサンドボックスに接続します。

```python
from bedrock_agentcore.tools.code_interpreter_client import code_session

CODE_INTERPRETER_REGION = os.getenv("CODE_INTERPRETER_REGION", "us-west-2")
OUTPUT_BUCKET = os.getenv("CODE_INTERPRETER_OUTPUT_BUCKET", "")
_s3_client = boto3.client("s3", region_name=os.getenv("AWS_REGION", "ap-northeast-1"))

@tool
def execute_python(code: str, description: str = "") -> str:
    """Execute Python code in a sandboxed environment."""
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

処理の流れを整理すると:

1. ユーザーコードの後ろにmatplotlibの画像キャプチャコードを自動注入
2. `plt.get_fignums()`で開いている全ての図を取得し、base64エンコードして`_IMG_..._END_`マーカーでstdoutに出力
3. ツール側でこのマーカーをパースしてbase64デコード
4. S3にアップロードして署名付きURL（1時間有効）を生成
5. URLをツール結果として返却

このため、エージェントには「`plt.savefig()`を呼ぶな、`plt.close()`を呼ぶな」とツールの説明に書いておく必要があります。これらを呼ぶと図がクリアされてキャプチャできなくなります。

S3バケットにはライフサイクルポリシーで1日経過後に自動削除するよう設定しており、一時的な画像置き場として使っています。


## SKILL.mdの作成

Agent Skillsのスキルファイルを配置します。

```
agentcore/
├── skills/
│   └── aws-cost/
│       └── SKILL.md
├── app.py
└── ...
```

SKILL.mdにはYAMLフロントマターとマークダウンの手順を記述します。

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

- **NEVER use boto3 inside execute_python** — the sandbox has no AWS credentials.
- **NEVER call plt.savefig()** — images are auto-captured from open figures.
- **NEVER call plt.close()** — closing figures prevents image capture.
- **Use English for ALL text** in charts — Japanese fonts are unavailable.

## Step 1: Fetch Data
（get_aws_costの呼び出し方）

## Step 2: Visualize
（matplotlibのコードテンプレート）
```

`allowed-tools`で使用するツール名を指定しますが、これはあくまで情報提供用で、実行時のアクセス制御は行いません。

## エージェントへの統合

`AgentSkills`プラグインと各ツールをエージェントに渡します。

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

`AgentSkills`は`plugins`パラメータで渡します。`tools`にはCode Interpreterやコスト取得のツール関数をそのまま渡すだけです。

## IAM権限

ランタイムロールに必要な権限です。

```typescript
// Code Interpreter実行権限
new iam.PolicyStatement({
  actions: [
    'bedrock-agentcore:CreateCodeInterpreter',
    'bedrock-agentcore:StartCodeInterpreterSession',
    'bedrock-agentcore:InvokeCodeInterpreter',
    'bedrock-agentcore:StopCodeInterpreterSession',
    'bedrock-agentcore:DeleteCodeInterpreter',
    'bedrock-agentcore:ListCodeInterpreters',
    'bedrock-agentcore:GetCodeInterpreter',
  ],
  resources: ['*'],
}),

// Cost Explorer読み取り権限（ランタイム側のboto3用）
new iam.PolicyStatement({
  actions: ['ce:GetCostAndUsage', 'ce:GetCostForecast', 'ce:GetDimensionValues'],
  resources: ['*'],
}),
```

加えて、生成画像の保存先となるS3バケットの権限も必要です。CDKの`grantReadWrite()`で付与しています。

```typescript
const codeInterpreterBucket = new s3.Bucket(this, 'CodeInterpreterOutputBucket', {
  bucketName: `tonari-codeinterpreter-outputs-${account}`,
  removalPolicy: cdk.RemovalPolicy.DESTROY,
  autoDeleteObjects: true,
  lifecycleRules: [{ expiration: cdk.Duration.days(1) }],
  blockPublicAccess: s3.BlockPublicAccess.BLOCK_ALL,
})
codeInterpreterBucket.grantReadWrite(runtimeRole)
```

Code Interpreterの権限は`resources: ['*']`としていますが、現時点ではリソースARNの絞り込みが公式ドキュメントに記載されていなかったためです。


## フロントエンドでの画像表示

S3の署名付きURLはエージェントのテキスト応答内に含まれます。フロントエンド側でテキスト内の画像URLを自動検出し、インラインで表示するようにしました。

```typescript
// テキスト内の画像URLを検出
const IMAGE_URL_PATTERN =
  /https?:\/\/[^\s"'<>]+\.(?:png|jpg|jpeg|gif|webp)(?:\?[^\s"'<>]*)?/gi

const extractImageUrls = (text: string) => {
  const urls: string[] = []
  const cleanText = text.replace(IMAGE_URL_PATTERN, (match) => {
    urls.push(match)
    return ''
  })
  return { cleanText, urls }
}
```

Chatコンポーネントではテキストから画像URLを抽出し、テキスト部分と画像部分を分けてレンダリングします。画像はクリックするとモーダルで拡大表示できるようにしています。


# トークンコスト

今回追加したツールとスキルの固定トークンコストです。

| 項目 | トークン数 | 発生タイミング |
|------|-----------|-------------|
| `get_aws_cost` 定義 | ~120 | 毎リクエスト |
| `execute_python` 定義 | ~180 | 毎リクエスト |
| Skills XML + skillsツール | ~90 | 毎リクエスト |
| **固定コスト合計** | **~390** | **毎リクエスト** |
| SKILL.md 本文 | ~500 | スキル呼び出し時のみ |

固定コストは約390トークン/リクエストで、前回の記事で紹介したサブエージェント8個分のツール定義と比べれば微々たるものです。SKILL.mdの本文はProgressive Disclosureにより、コスト分析を依頼したときだけ読み込まれます。


# デモ

TODO: スクリーンショット


# おしまい

というわけで、Code Interpreter × Agent Skills × Cost Explorer で自然言語からAWSコストをグラフ化する機能を実装しました。

実装してみて学んだ一番の教訓は、**Code Interpreterのサンドボックスは本当に隔離されている**ということです。AWSの認証情報は引き継がれないので、AWSリソースへのアクセスはランタイム側で行い、サンドボックスにはデータだけ渡してグラフ描画に専念させるのがきれいな分離になります。

`execute_python`ツール自体はAWSコストに特化していない汎用ツールなので、今後はカレンダーの予定分析やタスク完了推移の可視化など、他のデータ分析にも使い回していきたいと思います。
