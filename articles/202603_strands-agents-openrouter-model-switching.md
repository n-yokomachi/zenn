---
title: "Strands Agents + Bedrock AgentCoreのインフラはそのままに、LLMだけOpenRouterに切り替える"
emoji: "🔀"
type: "tech"
topics: [aws, bedrock, strandsagents, openrouter, python]
published: false
---

:::message
この記事は人間が書き、プログラムの実装・記事の校正に生成AIを使用しています。
:::

# はじめに

現在進行形でTONaRiというパーソナルAIエージェントを個人開発しています。Strands Agents + Amazon Bedrock AgentCoreで構築しており、フロントエンドにはAITuberKitを使用したVRM制御を行っています。
![](TODO: TONaRiのスクリーンショット)

前回の記事ではサブエージェント分割によるコスト削減の話を書きましたが、今回はさらなるコスト削減を目指して**LLMそのものをOpenRouter経由のGrok 4.1 Fastに切り替えた**話です。

https://zenn.dev/yokomachi/articles/202603_sub-agent-cost-optimization

ポイントとしては、Bedrock AgentCoreのインフラ（Memory、Gateway、Runtime）はそのまま使いつつ、**LLMだけ**をBedrock以外のモデルに差し替えるという構成です。


# なぜOpenRouterか

## コスト比較

まず、前回の記事でメインのLLMとして使用していたClaude Haiku 4.5（Amazon Bedrock）と、今回切り替え先のGrok 4.1 Fast（OpenRouter）のコストを比較してみます。

| | Claude Haiku 4.5（Bedrock） | Grok 4.1 Fast（OpenRouter） | 差 |
|---|---|---|---|
| 入力 | $1.10 / 1M tokens | $0.20 / 1M tokens | **5.5倍安い** |
| 出力 | $5.50 / 1M tokens | $0.50 / 1M tokens | **11倍安い** |

かなり大きな差があります。
前回の記事で月間コストを$18〜22削減した話を書きましたが、LLMそのものを切り替えればそもそもの単価が下がるのでさらに効果が大きいです。


## AgentCoreのインフラはモデル非依存

BedrockのLLMを使わないのにBedrock AgentCoreを使い続けるのは変では？と思うかもしれません。

しかし実際のところ、AgentCoreの各コンポーネントはLLMの選択に依存しません。

- **AgentCore Memory（STM/LTM）**: 会話履歴や長期記憶の保存・検索はエージェント側のセッションマネージャーが担当しており、どのLLMを使うかは関係ない
- **AgentCore Gateway**: MCPプロトコルでLambda関数をツールとして公開しているだけなので、呼び出し元のLLMが何であっても動く
- **AgentCore Runtime**: コンテナ実行環境であり、中で何のLLMを呼んでいるかは気にしない

つまり、AgentCoreを使う理由は「AWSのインフラでエージェントを安定運用するため」であり、「BedrockのLLMを使うため」ではないということです。この分離ができている点がAgentCoreの設計として優れていると感じています。


# Strands Agentsでのモデル切り替え

Strands AgentsはAWSが提供しているオープンソースのエージェントSDKですが、Bedrock以外のモデルもサポートしています。LiteLLMとの統合により、OpenRouter経由で事実上あらゆるLLMプロバイダーのモデルが使えます。

## LiteLLMモデルの作成

まず依存関係にlitellmを追加します。

```toml:pyproject.toml
dependencies = [
    "strands-agents>=1.23.0",
    "strands-agents[litellm]>=1.23.0",
    # ...
]
```

OpenRouter経由のモデルを作成する関数を実装します。

```python
from strands.models.litellm import LiteLLMModel
import litellm

# OpenRouterではBedrockのキャッシュ系パラメータなどがサポートされていないため、
# 未サポートパラメータを自動的にドロップする
litellm.drop_params = True

model = LiteLLMModel(
    model_id="openrouter/x-ai/grok-4.1-fast",
    params={
        "api_key": "your-openrouter-api-key",
        "extra_body": {"reasoning": {"enabled": False}},
    },
)
```

作成したモデルは`BedrockModel`と全く同じインターフェースで`Agent`に渡せます。

```python
from strands import Agent

agent = Agent(
    model=model,  # BedrockModelでもLiteLLMModelでも同じ
    system_prompt="あなたはパーソナルAIアシスタントです。",
    tools=my_tools,
)
```

## ハマりポイント：Grokのreasoningが漏れる

Grok 4.1はデフォルトでreasoning（思考プロセス）が有効になっています。これ自体は良いのですが、LiteLLM経由で使うとreasoningの内容がレスポンスに混ざって出力される問題がありました。

具体的には、こんな感じでレスポンスの冒頭に思考プロセスが混入します。

```
まず、ポリシーを確認します。ユーザーは挨拶をしています...

こんにちは！今日はどのようなお手伝いをしましょうか？
```

### 試したこと

**`reasoning.exclude: true`** → 効かない
```python
# これはLiteLLM経由では機能しなかった
params={"extra_body": {"reasoning": {"exclude": True}}}
```

OpenRouterの仕様では`exclude: true`でreasoning出力を隠せるはずですが、LiteLLM経由ではレスポンスのパース処理の関係で正しく動作しませんでした。

**`reasoning.enabled: false`** → 動いた
```python
# これが正解
params={"extra_body": {"reasoning": {"enabled": False}}}
```

reasoningを完全に無効化することで、クリーンなレスポンスが得られるようになりました。

「推論を無効化したら品質が落ちるのでは？」と心配しましたが、パーソナルアシスタントの用途（雑談、ツール呼び出しの判断、タスク管理など）では体感的に問題ない品質でした。


# 実装：ランタイムでのモデル切り替え

TONaRiではフロントエンドの設定画面からBedrock（Claude Haiku 4.5）とOpenRouter（Grok 4.1 Fast）をリアルタイムに切り替えられるようにしています。

![](TODO: 設定画面のスクリーンショット)

## モデルファクトリ

統一的なモデル作成関数を用意し、プロバイダーに応じたモデルインスタンスを返します。

```python:tonari_agent.py
MODEL_PROVIDER_BEDROCK = "bedrock"
MODEL_PROVIDER_OPENROUTER = "openrouter"

def _create_model(model_provider: str | None = None, cache_tools: bool = False):
    """モデルプロバイダーに応じたモデルインスタンスを作成"""
    provider = model_provider or os.getenv("MODEL_PROVIDER", MODEL_PROVIDER_BEDROCK)
    if provider == MODEL_PROVIDER_OPENROUTER:
        return _create_openrouter_model()
    return _create_bedrock_model(cache_tools=cache_tools)
```

`_create_openrouter_model`の中では、APIキーをSSM Parameter Store（SecureString）から取得しています。

```python:tonari_agent.py
def _get_ssm_parameter(name: str) -> str:
    """SSM Parameter Storeからパラメータを取得（SecureString対応）"""
    import boto3
    ssm = boto3.client("ssm", region_name=os.getenv("AWS_REGION", "ap-northeast-1"))
    response = ssm.get_parameter(Name=name, WithDecryption=True)
    return response["Parameter"]["Value"]


def _create_openrouter_model():
    """OpenRouter経由のLiteLLMModelインスタンスを作成"""
    from strands.models.litellm import LiteLLMModel
    import litellm
    litellm.drop_params = True

    model_id = os.getenv("OPENROUTER_MODEL_ID", "openrouter/x-ai/grok-4.1-fast")
    ssm_path = os.getenv("SSM_OPENROUTER_API_KEY", "")
    api_key = ""
    if ssm_path:
        try:
            api_key = _get_ssm_parameter(ssm_path)
        except Exception as e:
            logger.warning("Failed to get OpenRouter API key from SSM: %s", e)

    if not api_key:
        logger.warning("OpenRouter API key not available, falling back to Bedrock")
        return _create_bedrock_model()

    return LiteLLMModel(
        model_id=model_id,
        params={
            "api_key": api_key,
            "extra_body": {"reasoning": {"enabled": False}},
        },
    )
```

APIキーが取得できない場合はBedrockにフォールバックするようにしています。


## サブエージェントも連動

前回の記事で紹介したサブエージェント群も、同じモデルファクトリを使用するように変更しました。

```python:sub_agents.py
from .tonari_agent import _create_model

def _create_sub_agent_model():
    """サブエージェント用のモデルを作成（環境変数MODEL_PROVIDERに従う）"""
    return _create_model()
```

これにより、環境変数`MODEL_PROVIDER`を切り替えるだけでメインエージェント・サブエージェント・パイプラインエージェントのすべてが一括でモデルを切り替えます。


## CDK（インフラ）側の設定

AgentCore RuntimeのDockerコンテナに環境変数とSSMアクセス権限を追加します。

```typescript:agentcore-construct.ts
// SSMパラメータへのアクセス権限
SsmAccess: new iam.PolicyDocument({
  statements: [
    new iam.PolicyStatement({
      actions: ['ssm:GetParameter'],
      resources: [
        `arn:aws:ssm:${region}:${account}:parameter/tonari/openrouter-api-key`,
      ],
    }),
  ],
}),

// 環境変数
environmentVariables: {
  MODEL_PROVIDER: 'openrouter',
  SSM_OPENROUTER_API_KEY: '/tonari/openrouter-api-key',
},
```


## フロントエンドからの切り替え

Next.jsのフロントエンドからは、設定画面でモデルプロバイダーを選択してAPIリクエストに含めます。

```typescript:agentCoreChat.ts
body: JSON.stringify({
  message: userMessage,
  sessionId: getSessionId(),
  actorId: getActorId(),
  modelProvider: settingsStore.getState().modelProvider,  // 'bedrock' or 'openrouter'
}),
```

AgentCore Runtimeのエントリポイントでは、リクエストからモデルプロバイダーを受け取り、異なるプロバイダーが指定された場合はエージェントを再作成します。

```python:app.py
def _get_or_create_agent(session_id, actor_id, model_provider):
    """同じセッション・同じモデルならAgentを使い回し、変わったら作り直す"""
    global _current_agent, _current_model_provider

    if (
        _current_agent is not None
        and _current_session_id == session_id
        and _current_model_provider == model_provider
    ):
        return _current_agent

    # モデルプロバイダーが変わったらエージェントを再作成
    agent = create_tonari_agent(
        session_id=session_id,
        actor_id=actor_id,
        model_provider=model_provider,
    )
    _current_model_provider = model_provider
    return agent
```


# 全体のアーキテクチャ

最終的な構成は以下の通りです。太字の部分が今回の変更箇所です。

```
Frontend (Next.js + VRM)
  → Next.js API Route
    → AgentCore Runtime (Docker)
        ├── **モデルファクトリ**
        │   ├── BedrockModel (Claude Haiku 4.5)
        │   └── **LiteLLMModel (Grok 4.1 Fast via OpenRouter)**
        ├── AgentCore Memory (STM/LTM) ← モデル非依存
        ├── AgentCore Gateway → Lambda (各種ツール) ← モデル非依存
        ├── メインエージェント
        └── サブエージェント群 ← **統一モデルファクトリ使用**
```

AgentCoreのインフラ層（Memory、Gateway、Runtime）は一切変更なし。変更したのはエージェントのモデル生成部分だけです。


# 実際のコスト

Grok 4.1 Fastに切り替えてからのOpenRouter上でのコストを確認しました。

ある日のトークン使用量が約247Kトークンで$0.029でした。
同量をClaude Haiku 4.5（Bedrock）で処理した場合と比較すると：

| | Grok 4.1 Fast | Claude Haiku 4.5 |
|---|---|---|
| 入力 200K tokens | $0.04 | $0.22 |
| 出力 47K tokens | $0.024 | $0.26 |
| 合計 | **$0.029** | **$0.48** |

同じ使い方で約16倍のコスト差があります。個人開発としてはこの差はかなり大きいです。


# おしまい

ということで、Bedrock AgentCoreのインフラはそのままに、LLMだけOpenRouterに切り替えるという構成の紹介でした。

Strands AgentsのLiteLLM統合のおかげで、`BedrockModel`を`LiteLLMModel`に差し替えるだけで実現できます。AgentCoreのMemory、Gateway、Runtimeはモデルに依存しない設計になっているため、インフラ側の変更は不要です。

Grokのreasoningがレスポンスに混入する問題は`reasoning.enabled: false`で対処できますが、LiteLLM経由での挙動にはドキュメントにない落とし穴もあるので、実際に動かして確認することをおすすめします。

今のところGrok 4.1 Fastで品質面の問題は感じていませんが、もう少し運用してみてまた知見が溜まったら共有したいと思います。
