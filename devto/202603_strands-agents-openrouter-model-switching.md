---
title: "Using OpenRouter's OpenAI-Compatible Models (Grok 4.1 Fast) with Strands Agents"
emoji: "🔀"
type: "tech"
topics: [aws, bedrock, strandsagents, openrouter, python]
published: false
---

> This article is an AI-assisted translation of a Japanese technical article.

## Introduction

I'm building a personal AI agent called TONaRi ("tonari" means "next to" in Japanese — named with the idea of an AI that stands next to you and supports your daily life). It's built with Strands Agents + Amazon Bedrock AgentCore, with a VRM-powered 3D avatar frontend using AITuberKit.

In a previous article, I wrote about cost reduction through sub-agent splitting.
https://dev.to/yokomachi/28-tool-definitions-cutting-ai-agent-costs-with-sub-agent-splitting-4dbp

This time, I took cost reduction a step further by making it possible to switch the LLM itself to Grok 4.1 Fast via OpenRouter.

## Cost Comparison

Let's compare the costs between Claude Haiku 4.5 (Amazon Bedrock), which I had been using as the main model, and Grok 4.1 Fast (OpenRouter), the new alternative.

| | Claude Haiku 4.5 (Bedrock) | Grok 4.1 Fast (OpenRouter) |
|---|---|---|
| Input | $1.10 / 1M tokens | $0.20 / 1M tokens |
| Output | $5.50 / 1M tokens | $0.50 / 1M tokens |

That's a significant difference. As I mentioned in the previous article, LLM per-token pricing is by far the biggest cost driver, so reducing the unit price — while maintaining an acceptable quality balance — has the greatest impact.

## Switching Models in Strands Agents

Strands Agents is an open-source agent SDK provided by AWS, and it supports models beyond Bedrock. Using the `OpenAIModel` class, you can directly use models from any service that provides an OpenAI-compatible API, such as OpenRouter. If you need broader provider support, `LiteLLMModel` is also an option. Since Grok 4.1 Fast is OpenAI-compatible, we use the `OpenAIModel` class directly.

### Creating an OpenAIModel

First, add the `openai` dependency.

```toml:pyproject.toml
dependencies = [
    "strands-agents>=1.23.0",
    "openai>=1.0.0",
    # ...
]
```

Then create the model instance via OpenRouter.

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

The created model can be passed to an Agent with the exact same interface as a Bedrock model.

```python
from strands import Agent

agent = Agent(
    model=model,  # Works the same whether BedrockModel or OpenAIModel
    system_prompt="You are a personal AI assistant.",
    tools=my_tools,
)
```

## Wrap Up

So I switched the model used for everyday conversations to Grok 4.1 Fast, and my impression is that quality isn't a major issue for casual conversation. However, application-specific conversation tags (this AI agent uses tags like `[happy]` or `[bow]` to trigger facial expressions and motions) sometimes get ignored or misinterpreted by the model, so that still needs tuning.

I also had concerns about tool calling via AgentCore Gateway, but it's been working surprisingly well without any major adjustments.

I'll continue monitoring and consider trying other models or implementing model-specific routing if needed.
