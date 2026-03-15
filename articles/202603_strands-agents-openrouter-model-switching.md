---
title: "Strands AgentsでOpenRouterのOpenAI互換モデル（Grok 4.1 Fast）を使用する"
emoji: "🔀"
type: "tech"
topics: [aws, bedrock, strandsagents, openrouter, python]
published: true
---

:::message
この記事は人間が書き、プログラムの実装・記事の校正に生成AIを使用しています。
:::

# はじめに

現在進行形でTONaRiというパーソナルAIエージェントを個人開発しています。
![](https://storage.googleapis.com/zenn-user-upload/df51b4a92c40-20260311.png)

前回の記事でサブエージェント分割によるコスト削減の話を書きました。
https://zenn.dev/yokomachi/articles/202603_sub-agent-cost-optimization

今回はさらなるコスト削減のためStrands AgentsであつかうLLMそのものをOpenRouter経由のGrok 4.1 Fastに切り替えができるようにしました。

# コスト削減効果

これまでメインで使用していたClaude Haiku 4.5（Amazon Bedrock）と、今回切り替え先のGrok 4.1 Fast（OpenRouter）のコストを比較してみます。

| | Claude Haiku 4.5（Bedrock） | Grok 4.1 Fast（OpenRouter） |
|---|---|---|
| 入力 | $1.10 / 1M tokens | $0.20 / 1M tokens |
| 出力 | $5.50 / 1M tokens | $0.50 / 1M tokens |

かなり大きな差があります。
前回の記事でも触れましたが結局一番お金を使うのはLLMの従量課金なので、性能とのバランスはとりつつ単価を下げられるのが一番効果が大きいです。


# Strands Agentsでのモデル切り替え

Strands AgentsはAWSが提供しているオープンソースのエージェントSDKですが、Bedrock以外のモデルもサポートしています。
`OpenAIModel`クラスを使うことで、OpenAI互換APIを提供するサービス（OpenRouterなど）のモデルを直接利用できます。
また、より幅広いプロバイダーに対応したい場合は`LiteLLMModel`も選択肢になります。
今回使用するGrok 4.1 FastはOpenAI互換なのでOpenAIModelクラスで直接使用します。

## OpenAIModelの作成

まず依存関係にopenaiを追加します。

```toml:pyproject.toml
dependencies = [
    "strands-agents>=1.23.0",
    "openai>=1.0.0",
    # ...
]
```

続いてOpenRouter経由のモデルインスタンスを作成します。

```python
from strands.models.openai import OpenAIModel

model = OpenAIModel(
    client_args={
        "api_key": "your-openrouter-api-key",
        "base_url": "https://openrouter.ai/api/v1",
    },
    model_id="x-ai/grok-4.1-fast",
)
```

作成したモデルはBedrockのモデルの場合と全く同じインターフェースでAgentに渡せます。

```python
from strands import Agent

agent = Agent(
    model=model,  # BedrockModelでもOpenAIModelでも同じ
    system_prompt="あなたはパーソナルAIアシスタントです。",
    tools=my_tools,
)
```


# おしまい

というわけで日常的な会話に使用するモデルはGrok 4.1 Fastに変更しましたが、体感として普通の会話なら品質面の問題はそこまでないようにも思います。
ただアプリケーション特有の会話タグの指定（このパーソナルAIエージェントでは会話タグ[happy]とか[bow]とかで表情やモーションのトリガーをしている）など、一部のシステムプロンプトが確率で無視されたり間違えたりするのでそこは要調整という感じです。
また、AgentCore Gatewayで構築しているツールの呼び出しに関しても懸念がありましたが、意外にも大きなチューニングなど必要なく使えているようでした。
もう少し運用してみて必要があれば他のモデルの検討とか使い分けも考えていきたいと思います。

