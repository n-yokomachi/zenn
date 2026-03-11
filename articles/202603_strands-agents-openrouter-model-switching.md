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

現在進行形でTONaRiというパーソナルAIエージェントを個人開発しています。
![](https://storage.googleapis.com/zenn-user-upload/df51b4a92c40-20260311.png)

前回の記事でサブエージェント分割によるコスト削減の話を書きました。
https://zenn.dev/yokomachi/articles/202603_sub-agent-cost-optimization

今回はさらなるコスト削減のためStrands AgentsであつかうLLMそのものをOpenRouter経由のLLMに切り替えができるようにしました。

# コスト削減効果

これまでメインで使用していたClaude Haiku 4.5（Amazon Bedrock）と、今回切り替え先のGrok 4.1 Fast（OpenRouter）のコストを比較してみます。

| | Claude Haiku 4.5（Bedrock） | Grok 4.1 Fast（OpenRouter） | 差 |
|---|---|---|
| 入力 | $1.10 / 1M tokens | $0.20 / 1M tokens |
| 出力 | $5.50 / 1M tokens | $0.50 / 1M tokens |

かなり大きな差があります。
前回の記事でも触れましたが結局一番お金を使うのはLLMの従量課金なので、性能とのバランスはとりつつ単価が下げられるのがそれが一番効果が大きいです。


# Strands Agentsでのモデル切り替え

Strands AgentsはAWSが提供しているオープンソースのエージェントSDKですが、Bedrock以外のモデルもサポートしています。
LiteLLMとの統合により、OpenRouterのモデルも使用可能です。
今回はGrok 4.1 Fastが面白そうだったので使ってみます。

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

作成したモデルはBedrockのモデルの場合と全く同じインターフェースでAgentに渡せます。

```python
from strands import Agent

agent = Agent(
    model=model,  # BedrockModelでもLiteLLMModelでも同じ
    system_prompt="あなたはパーソナルAIアシスタントです。",
    tools=my_tools,
)
```

## Grokのreasoningがレスポンスに混入する

Grok 4.1はデフォルトでreasoningが有効になっています。細かい条件を検証したわけではないですが、LiteLLM経由で使うとreasoningの内容がレスポンスに混ざって出力されるケースがありました。

こんな感じでレスポンスの冒頭に思考プロセスが混入します。

```
まず、ポリシーを確認します。ユーザーは挨拶をしています...

こんにちは！今日はどのようなお手伝いをしましょうか？
```

### 試したこと

[OpenRouterのドキュメント](https://openrouter.ai/docs/guides/best-practices/reasoning-tokens)では`exclude: true`でreasoning出力を隠せるらしいですが、LiteLLM経由だからかレスポンスのパース部分でうまく効いていないようでした

```python
# これはLiteLLM経由では機能しなかった
params={"extra_body": {"reasoning": {"exclude": True}}}
```

というわけで仕方なくreasoningを無効化しています。
品質が落ちそうですが、軽く使ってみた感じはそこまで違和感ありません。


# おしまい

ということで、Bedrock AgentCoreのインフラはそのままに、LLMだけOpenRouterに切り替えるという構成の紹介でした。

Strands AgentsのLiteLLM統合のおかげで、`BedrockModel`を`LiteLLMModel`に差し替えるだけで実現できます。AgentCoreのMemory、Gateway、Runtimeはモデルに依存しない設計になっているため、インフラ側の変更は不要です。

Grokのreasoningがレスポンスに混入する問題は`reasoning.enabled: false`で対処できますが、LiteLLM経由での挙動にはドキュメントにない落とし穴もあるので、実際に動かして確認することをおすすめします。

今のところGrok 4.1 Fastで品質面の問題は感じていませんが、もう少し運用してみてまた知見が溜まったら共有したいと思います。
