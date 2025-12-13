---
title: "A2A×Strands Agents×Bedrock AgentCoreでマルチエージェントを構築する"
emoji: "🧗🏻"
type: "tech"
topics: [aws, bedrock, a2a, python, strandsagents]
published: false
---

この記事は[AIエージェント構築＆運用 Advent Calendar 2025](https://qiita.com/advent-calendar/2025/agents) 15日目のエントリです。

:::message
この記事は人間が書き、記事の校正に生成AIを使用しています。
:::

# はじめに
今回はAmazon Bedrock AgentCoreを使用し、A2Aに準拠したエージェントのデプロイ、そしてそれらを使用するマルチエージェントの構築をしてみたいと思います。
以下のリポジトリに今回使用したコードを置いています。
https://github.com/n-yokomachi/a2a-on-bedrock-agentcore

なお、A2Aについては以前入門記事を書いているので、よければそちらもご覧ください。
https://zenn.dev/yokomachi/articles/20250417_tutorial_a2a

ちなみに今回はWindowsでやっていきます（この記事書こうとしたタイミングでMacのバッテリー切れてたので）。
また、AWSのリージョンは基本的に東京リージョンを使用します。


# シングルAIエージェントを作る
まずはBedrock AgentCoreの使い方を確認するために簡単なシングルAIエージェントを構築します。
Bedrock AgentCoreではSDK, CLIが提供されています。
エージェントにSDKでBedrock AgentCore Runtimeからのエントリポイントを実装し、CLIによりランタイムの設定やデプロイを行う形となります。

今回エージェントフレームワークにはAWSが提供しているStrands Agentsを使用します。
またLLMはAmazon BedrockのClaude Sonnet 4.5、Nova 2 Liteを使用します。


## ローカルで動作するエージェントの実装
ではまず、ローカル環境で動作するエージェントを作ります。
この時点ではまだBedrock AgentCore SDKを使用せず、シンプルなStrands Agentsを使用したエージェントを作成します。

```bash: Terminal
# プロジェクト・仮想環境の作成
>uv a2a-on-bedrock-agentcore
>cd a2a-on-bedrock-agentcore
>uv venv
>.venv\Scripts\activate.bat

# Strands Agentsのインストール
>uv pip install strands-agents
```

以下の内容でファイルを作成します。
```python: simple_agent.py
from strands import Agent
from strands.models import BedrockModel

model = BedrockModel(
    model_id="jp.anthropic.claude-sonnet-4-5-20250929-v1:0",
    region_name="ap-northeast-1"
)

agent = Agent(model=model)

while True:
    question = input("> ")
    if question.lower() in ['quit', 'exit']:
        break
    print(agent(question))
```

動作確認してみます

```bash: Terminal
>uv run simple_agent.py                
> あなたは誰？
私はClaude（クロード）です。Anthropic社によって作られたAIアシスタントです。様々な質問にお答えしたり、文章の作成や分析、問題解決のお手伝いなどをすることができます。何かお手伝い できることがあれば、お気軽にお聞かせください。私はClaude（クロード）です。Anthropic社によって作られたAIアシスタントです。様々な質問にお答えしたり、文章の作成や分析、問題解決の お手伝いなどをすることができます。何かお手伝いできることがあれば、お気軽にお聞かせください。
```

よさそうです。


## Bedrock AgentCore SDKのインストール
では先ほど作成したエージェントをベースにBedrock AgentCore SDKをインストールします

```bash: Terminal
# Bedrock AgentCore SDKのインストール
>uv pip install bedrock-agentcore
```

以下の内容でファイルを作成します。
```python: simple_agent_on_core.py
from strands import Agent
from strands.models import BedrockModel
from bedrock_agentcore import BedrockAgentCoreApp

model = BedrockModel(
    model_id="jp.anthropic.claude-sonnet-4-5-20250929-v1:0",
    region_name="ap-northeast-1"
)

agent = Agent(model=model)

app = BedrockAgentCoreApp()

@app.entrypoint
def invoke(payload):
    question = payload.get("prompt", "")
    return {"result": agent(question)}

if __name__ == "__main__":
    app.run()
```
Bedrock AgentCore SDKではローカルサーバーを立てて動作確認が可能なので試してみます。

```bash: Terminal
>uv run simple_agent_on_core.py
```
すると、以下のようにローカルサーバーが立ち上がるので、
これに向けてcurlコマンドでリクエストを送信してみます。

```bash: Terminal
>curl -X POST http://localhost:8080/invocations -H "Content-Type: application/json" -d "{\"prompt\": \"こんにちは、君は誰？\"}"
"{'result': AgentResult(stop_reason='end_turn', message={'role': 'assistant', 'content': [{'text': 'こんにちは！私はClaudeです。Anthropic社が開発したAIアシスタントです。\\n\\n様々な質問にお答えしたり、文章の作成、分析、創作のお手伝いなど、幅広いタスクでサポートできま す。何かお手伝いできることがあれば、お気軽にお聞かせください。'}]}, metrics=EventLoopMetrics(cycle_count=1, tool_metrics={}, cycle_durations=[2.768364906311035], traces=[<strands.telemetry.metrics.Trace object at 0x0000023D4ADFF170>], accumulated_usage={'inputTokens': 18, 'outputTokens': 107, 'totalTokens': 125}, accumulated_metrics={'latencyMs': 2601}), state={}, interrupts=None, structured_output=None)}"
```

構造化されたレスポンスが返ってきていることが確認できました。

## Bedrock AgentCoreにデプロイ
ローカルでの動作確認ができたのでBedrock AgentCoreにデプロイしてみます
Bedrock AgentCoreではECRのコンテナイメージを使用するので、まずはその準備をします。
先ほど作成したエージェントのファイルを含め、以下のようなディレクトリを作成します。
```
simple_agent_on_core
├── requirements.txt
└── simple_agent_on_core.py
```

requirements.txtには以下の内容を記載します。
```text: requirements.txt
bedrock-agentcore
strands-agents
```

bedrock-agentcore-starter-toolkitをインストールして、CLIコマンドでデプロイを行います。

```bash: Terminal
# starter-tooklitのインストール
>uv pip install bedrock-agentcore-starter-toolkit

# AgentCoreのコンフィグ
# 対話型のコンフィグが立ち上がるので全部Enter（メモリの使用部分はsでスキップ）
agentcore configure -e simple_agent_on_core.py
Configuring Bedrock AgentCore...
✓ Using file: simple_agent_on_core.py

🏷️  Inferred agent name: simple_agent_on_core
Press Enter to use this name, or type a different one (alphanumeric without '-')
Agent name [simple_agent_on_core]:
...

# AgentCoreへのデプロイ
agentcore launch
```

## 動作確認
AWSコンソールでAmazon Bedrock AgentCoreのエージェントランタイムを確認すると、無事にエージェントがデプロイされていることが確認できます。
![](https://storage.googleapis.com/zenn-user-upload/38700c75584b-20251213.png)

ではこのエージェントをBedrock AgentCore CLIで呼び出してみます。

```bash: Terminal
>agentcore invoke "{\"prompt\": \"こんにちは、君は誰？\"}"
╭───────────────────────────────────────────────────── simple_agent_on_core ──────────────────────────────────────────────────────╮
│ Session: sample                                                                                                                 │
│ # 以下省略                                                                                                                       │
╰─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯

Response:
{'result': AgentResult(stop_reason='end_turn', message={'role': 'assistant', 'content': [{'text':
'こんにちは！私はClaudeです。Anthropic社によって作られたAIアシスタントです。\n\n質問に答えたり、文章を書いたり、問題解決のお手伝い 
をしたり、様々な話題について会話することができます。何かお手伝いできることはありますか？'}]},
metrics=EventLoopMetrics(cycle_count=1, tool_metrics={}, cycle_durations=[2.725674629211426],
traces=[<strands.telemetry.metrics.Trace object at 0xffff6b7bd640>], accumulated_usage={'inputTokens': 18, 'outputTokens': 92,     
'totalTokens': 110}, accumulated_metrics={'latencyMs': 2524}), state={}, interrupts=None, structured_output=None)}
```

よさそうですね。


# A2AでマルチAIエージェントを作る
続いて本題のA2Aによるマルチエージェントの構築をしていきます。

まず作成するエージェントのそれぞれの役割を整理します。
- リモートエージェント1: Nova 2 Liteによるテキスト生成を行うエージェント
- リモートエージェント2: Claude Sonnet 4.5によるテキスト生成を行うエージェント
- クライアントエージェント: 2つのリモートエージェントを使用して、各モデルが生成したテキストの違いを分析するエージェント

図にするとこんな感じです


## リモートエージェントの実装

まずはリモートエージェント1, 2を作成します。
異なるのは使用するモデルだけなのでコードはほぼ共通です。

```python: remote_agent_1.py remote_agent_2.py
import os
from strands import Agent
from strands.models import BedrockModel
from strands.multiagent.a2a import A2AServer
from fastapi import FastAPI
import uvicorn

# モデルの設定（Nova 2 Lite, Claude Sonnet 4.5をそれぞれ設定）
model = BedrockModel(
    model_id="jp.amazon.nova-2-lite-v1:0",
    region_name="ap-northeast-1"
)

# エージェントの作成
agent = Agent(
    name="Nova Lite Agent",
    description="Amazon Nova 2 Liteを使用してテキスト生成を行うエージェントです。",
    model=model,
    callback_handler=None
)

# A2Aサーバーの設定
runtime_url = os.environ.get("AGENTCORE_RUNTIME_URL", "http://127.0.0.1:9000/")

a2a_server = A2AServer(
    agent=agent,
    http_url=runtime_url,
    serve_at_root=True
)

app = FastAPI()

@app.get("/ping")
def ping():
    return {"status": "healthy"}

app.mount("/", a2a_server.to_fastapi_app())

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=9000)
```

## クライアントエージェントの実装
続いてクライアントエージェントを実装します。
なお、コード内で使用しているリモートエージェントのARNは以下の形式です。
`arn:aws:bedrock-agentcore:ap-northeast-1:765653276628:runtime/{runtime_agent_name}`

```python: client_agent.py
# 中略

# リモートエージェントのURLを作成
def build_agentcore_url(arn: str) -> str:
    encoded_arn = quote(arn, safe='')
    return f"https://bedrock-agentcore.ap-northeast-1.amazonaws.com/runtimes/{encoded_arn}/invocations/"

REMOTE_AGENT_1_ARN = os.environ.get("REMOTE_AGENT_1_ARN")
REMOTE_AGENT_2_ARN = os.environ.get("REMOTE_AGENT_2_ARN")
BEARER_TOKEN = os.environ.get("BEARER_TOKEN")
SESSION_ID = str(uuid4())

REMOTE_AGENT_1_URL = build_agentcore_url(REMOTE_AGENT_1_ARN)
REMOTE_AGENT_2_URL = build_agentcore_url(REMOTE_AGENT_2_ARN)

model = BedrockModel(
    model_id="jp.anthropic.claude-sonnet-4-5-20250929-v1:0",
    region_name="ap-northeast-1"
)

provider = A2AClientToolProvider(
    known_agent_urls=[REMOTE_AGENT_1_URL, REMOTE_AGENT_2_URL],
    httpx_client_args={
        "headers": {
            "Authorization": f"Bearer {BEARER_TOKEN}",
            "X-Amzn-Bedrock-AgentCore-Runtime-Session-Id": SESSION_ID
        },
        "timeout": 300
    }
)

agent = Agent(
    model=model,
    system_prompt="""あなたは2つのリモートエージェントを使って、テキスト生成の比較分析を行うエージェントです。

利用可能なリモートエージェント:
1. Nova Lite Agent - Amazon Nova 2 Liteを使用
2. Claude Sonnet Agent - Claude Sonnet 4.5を使用

ユーザーからの質問に対して、両方のエージェントにリクエストを送り、以下の形式で出力してください：

## Nova Lite Agent の回答
（エージェントからの回答をそのまま記載）

## Claude Sonnet Agent の回答
（エージェントからの回答をそのまま記載）

## 比較分析
（両方の回答を比較・分析した結果）
""",
    tools=provider.tools
)

def save_to_markdown(question: str, response: str):
    # 中略

if __name__ == "__main__":
    print("クライアントエージェントを起動します")
    print("-" * 50)

    while True:
        question = input("> ")
        if question.lower() in ['quit', 'exit']:
            break

        result = agent(question)
        print()
        save_to_markdown(question, str(result))

```


## Bedorkc AgentCoreにデプロイ

### Cognitoユーザープールの作成

A2Aで認証を通すため、以下のサイトを参考にCognitoユーザープールを作成します。
https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/runtime-mcp.html#runtime-mcp-appendix-a

なお今回はWindowsで作業していたので以下のようにbatに書き換えて実行しました。
※Bearerトークンについては60分で有効期限が切れるので必要に応じて取得しなおしてください
https://github.com/n-yokomachi/a2a-on-bedrock-agentcore/blob/main/cognito_setup.bat


### デプロイ
AgentCoreへのデプロイを行います。

以下の通りA2Aプロトコルの指定とOAuth設定をします。
OAuthの設定では先ほど実行したCognitoユーザープールを作成するスクリプトの出力から、discovery URL, client IDsを設定します。
それ以外は特に指定せずEnterです。
```bash
# A2Aプロトコルを指定してコンフィグ
>agentcore configure -e remote_agent_1.py --protocol A2A

# 中略

# OAuth設定
📋 OAuth Configuration
Enter OAuth discovery URL: https://cognito-idp.ap-northeast-1.amazonaws.com/{user_pool_id}/.well-known/openid-configuration
Enter allowed OAuth client IDs (comma-separated): {cleint_id}
Enter allowed OAuth audience (comma-separated):
Enter allowed OAuth allowed scopes (comma-separated):
Enter allowed OAuth custom claims as JSON string (comma-separated):
✓ OAuth authorizer configuration created

# 中略

>agentcore launch
```

## 動作確認

では実際に動かしてみます。
```bash
>cd client_agent
# Strands AgentsのA2Aクライアント拡張をインストール
>uv pip install strands-agents-tools[a2a_client]
# クライアントエージェントを実行
>uv run client_agent.py
```

長くなるので折り畳みにしましたが、実行結果は以下の通りとなります。
２つのリモートエージェントをツールとして呼び出し、クライアントエージェントがそのレスポンスを分析できていることがわかります。

:::details 実行結果
```bash
> Amazon Bedrockってなに？
INFO:strands.telemetry.metrics:Creating Strands MetricsClient

Tool #1: a2a_list_discovered_agents
INFO:strands_tools.a2a_client:A2ACardResolver created for {中略}
INFO:strands_tools.a2a_client:A2ACardResolver created for {中略}
INFO:httpx:HTTP Request: GET {中略} "HTTP/1.1 200 OK"
INFO:a2a.client.card_resolver:Successfully fetched agent card data from {中略}: {'capabilities': {'streaming': True}, 'defaultInputModes': ['text'], 'defaultOutputModes': ['text'], 'description': 'Amazon Nova 2 Liteを使用してテキスト生成を行うエージェントです。', 'name': 'Nova Lite Agent', 'preferredTransport': 'JSONRPC', 'protocolVersion': '0.3.0', 'skills': [], 'url': '{中略}', 'version': '0.0.1'}
INFO:strands_tools.a2a_client:Successfully discovered and cached agent card for {中略}
INFO:httpx:HTTP Request: GET {中略} "HTTP/1.1 200 OK"
INFO:a2a.client.card_resolver:Successfully fetched agent card data from {中略}: {'capabilities': {'streaming': True}, 'defaultInputModes': ['text'], 'defaultOutputModes': ['text'], 'description': 'Claude Sonnet 4.5を使用してテキスト生成を行 うエージェントです。', 'name': 'Claude Sonnet Agent', 'preferredTransport': 'JSONRPC', 'protocolVersion': '0.3.0', 'skills': [], 'url': '{中略}', 'version': '0.0.1'}
INFO:strands_tools.a2a_client:Successfully discovered and cached agent card for {中略}

Tool #2: a2a_send_message

Tool #3: a2a_send_message
INFO:strands_tools.a2a_client:Sending message to {中略}
INFO:strands_tools.a2a_client:Sending message to {中略}
INFO:httpx:HTTP Request: POST {中略} "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST {中略} "HTTP/1.1 200 OK"
## Nova Lite Agent の回答

### **Amazon Bedrockとは何か（簡潔な説明）**

**Amazon Bedrock**は、Amazon Web Services（AWS）が提供する**生成型AIサービス**で、**大規模な言語モデル（LLM）やその他のAIモデルを簡単に利用できるプラットフォーム**です。

---

### **主な特徴**

1. **さまざまなAIモデルがすぐに利用可能**  
   - Amazon Bedrockには、**Amazonが開発した proprieatry モデル**（例: **Titan**シリーズ）と、**外部から提供された人気のあるオープンソースモデル**（例: **LLaMA、Stable Diffusion、AnthropicのClaude**）が 組み込まれています。
   - これらのモデルを**APIを呼び出すだけで**使用できます。

2. **セキュリティとコンプライアンスが強化**  
   - AWSの高度なセキュリティ機能（IAM、VPC、暗号化など）が適用され、**データの保護とアクセス制御**が可能です。
   - **責任あるAIの実現**に役立つツールも提供されています。

3. **スケーラブルで管理が簡単**  
   - AWSのインフラストラクチャが裏側で動作するため、**サーバーの管理やモデルデプロイの面倒な作業は不要**です。
   - 需要に応じて自動的にスケールします。

4. **開発者フレンドリーなインターフェース**  
   - **コンソール、SDK、CLI、API**を通じて、開発者が簡単に統合できます。
   - **プロンプトエンジニアリング**や**ファインチューニング**のサポートも提供。

---

### **用途例**

- **チャットボットや仮想アシスタント**の作成
- **文章生成、要約、翻訳**
- **画像生成（Stable Diffusionなど）**
- **顧客フィードバックの分析**
- **ドキュメントの要約や検索の向上**

---

### **結論**

**Amazon Bedrockは、生成AIを迅速に実装するためのクラウドサービス**で、**専門知識がなくても強力なAIモデルを活用できます**。AWSの信頼性とセキュリティを背景に、ビジネスや開発プロジェクトにAIを組み込むため の**効率的なソリューション**です。

---

## Claude Sonnet Agent の回答

# Amazon Bedrockとは

Amazon Bedrockは、**AWSが提供する生成AIの基盤サービス**です。

## 主な特徴

- **複数のAIモデルにアクセス可能**
  - Claude（Anthropic）、Llama、Stable Diffusionなど、大手AI企業の基盤モデルを単一のAPIで利用

- **簡単な統合**
  - サーバーレスで、インフラ管理不要
  - AWS環境とシームレスに連携

- **カスタマイズ可能**
  - 独自データでモデルをファインチューニング可能
  - プライベートなカスタマイズに対応

- **エンタープライズ向け**
  - セキュリティとプライバシーを重視
  - データはモデルの学習に使用されない

## 用途
チャットボット、文書要約、コンテンツ生成、画像生成など、様々な生成AIアプリケーションの開発に活用されています。

---

## 比較分析

### **構成と表現スタイル**

**Nova Lite Agent（Amazon Nova 2 Lite）:**
- より詳細で包括的な説明
- マークダウン形式を活用した構造化された説明（見出しのレベル分け、強調表示の多用）
- 4つの主な特徴を詳しく展開し、各項目に複数の説明文を含む
- 用途例を箇条書きで5つ提示
- 「結論」セクションで内容をまとめている

**Claude Sonnet Agent:**
- よりコンパクトで簡潔な説明
- シンプルなマークダウン構造
- 4つの特徴を簡潔に箇条書きで提示
- 用途を1文でまとめている
- 全体的に読みやすさを重視した設計

### **内容の違い**

**共通点:**
- 両者とも「AWSが提供する生成AIサービス/基盤サービス」として正しく定義
- 複数のAIモデル（Claude、Llama、Stable Diffusion等）へのアクセスを強調
- セキュリティとエンタープライズ向け機能を言及
- サーバーレス/インフラ管理不要の特徴を強調

**Nova Lite Agentの特徴:**
- AWSのセキュリティ機能（IAM、VPC、暗号化）を具体的に列挙
- 「責任あるAI」というコンセプトに言及
- 開発者向けツール（コンソール、SDK、CLI、API）を明示
- プロンプトエンジニアリングとファインチューニングに触れている

**Claude Sonnet Agentの特徴:**
- 「基盤サービス」という表現でより正確な位置づけ
- 「データはモデルの学習に使用されない」というプライバシー面の重要な情報を明記
- よりビジネス目的に焦点を当てた説明

### **総評**

**質問への適合性:** 「簡潔に説明してください」という要求に対して、**Claude Sonnet Agentの方がより適切**です。Nova Lite Agentは詳細で有用な情報を提供していますが、やや冗長です。

**情報の正確性:** 両者とも正確ですが、Claude Sonnet Agentの「データはモデルの学習に使用されない」という記述は、エンタープライズユーザーにとって重要な差別化ポイントを明確にしています。

**対象読者:** Nova Lite Agentは初学者向け、Claude Sonnet Agentはビジネス意思決定者や技術者向けの説明として適しています。
結果を d:\work\Workshops\a2a-on-bedrock-agentcore\multi_agent_on_core\client_agent\analysis_results.md に保存しました
```
:::

# おわりに
ということで今回はA2A×Strands Agents×Bedrock AgentCoreをやってみました。
意外とこの３つを使った日本語ドキュメントがなかったので参考になれば幸いです。
