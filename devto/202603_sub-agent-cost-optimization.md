---
title: "28 TOOL DEFINITIONS! — Cutting AI Agent Costs with Sub-Agent Splitting"
emoji: "🧩"
type: "tech"
topics: [aws, bedrock, strandsagents, aiagent, python]
published: false
---

> This article is an AI-assisted translation of a Japanese technical article.

## Introduction

I'm building a personal AI agent called TONaRi ("tonari" means "next to" in Japanese — named with the idea of an AI that stands next to you and supports your daily life). It's built with Strands Agents + Amazon Bedrock AgentCore, with a VRM-powered 3D avatar frontend using AITuberKit.
![](https://storage.googleapis.com/zenn-user-upload/6d6a131e15f1-20260307.png)

As I kept adding tools to make my personal AI agent more useful for daily tasks, the input tokens per API call ballooned — and so did the cost.
![](https://storage.googleapis.com/zenn-user-upload/1fa4d12f457d-20260307.png)
*It's lower now, but the projection was heading toward $120/month*

In this article, I'll walk through the input token bloat problem caused by too many tools and how I tackled it by splitting into sub-agents.


## Architecture Overview

Here's a high-level look at TONaRi's architecture:

```
Frontend (Next.js + VRM 3D Avatar)
  → Next.js API Route
    → AgentCore Runtime (Strands Agent)
      → AgentCore Gateway → Lambda functions (tools)
      → AgentCore Memory (STM/LTM)
```

The agent runs as a container deployed on Bedrock AgentCore Runtime. External tools are implemented as Lambda functions accessed through AgentCore Gateway. Adding a new tool is as simple as writing a Lambda function and registering it as a Gateway target.


## All the Tools

AgentCore Gateway lets you expose Lambda functions as agent tools.

```python
from strands.tools.mcp import MCPClient
from mcp_proxy_for_aws.client import aws_iam_streamablehttp_client

def create_mcp_client(gateway_url: str, region: str) -> MCPClient:
    def create_transport():
        return aws_iam_streamablehttp_client(
            endpoint=gateway_url,
            aws_region=region,
            aws_service="bedrock-agentcore",
        )
    return MCPClient(create_transport)
```

Here are all the tools I've connected:

| Domain | Tools | Count |
|--------|-------|-------|
| Task Management | List, Add, Complete, Update | 4 |
| Calendar | List events, Check availability, Create, Update, Delete, Suggest schedule | 6 |
| Gmail | Search, Get, Create draft, Archive | 4 |
| Notion | Search pages, Get page, Create, Update, Query DB, Get DB | 6 |
| Twitter | Get today's tweets, Post | 2 |
| Diary | Save, Get | 2 |
| Date Utils | Get current datetime, Calculate date, List date range | 3 |
| Web Search | Web search | 1 |
| **Total** | | **28** |

Each tool can be called individually, but the real power is chaining. For example, saying "Search for a recipe, save the bookmark to Notion, create a shopping list, and add grocery shopping to my tasks" triggers:
1. Web search tool finds a recipe
2. Saves the URL to a Notion bookmark page
3. Creates a shopping list from the recipe and saves it to a Notion memo page
4. Adds a grocery shopping task to TONaRi's task list

The AI agent sits between tools and interprets vague user requests to orchestrate across them — this is the most useful aspect of using an AI agent day-to-day.


## The Input Token Explosion

Behind the convenience, costs were quietly piling up. When calling the Bedrock API, input tokens consist of four main components:

1. **System prompt**: Agent character settings, behavior rules
2. **Tool definitions**: Name, description, and JSON schema for every tool
3. **Long-term memory (LTM)**: Episodes and facts extracted from past conversations
4. **Conversation history (STM)**: Current session content

The biggest culprit was tool definitions. I had Claude Code calculate it — the 28 tools directly connected to the agent consumed about 5,000 tokens.


### Breaking Down the Numbers

Here's a rough breakdown of input tokens per call for the monolithic agent:

| Component | Estimated Tokens |
|-----------|-----------------|
| System prompt (character + all domain rules) | ~3,500 |
| Tool definitions (28 tools × schema) | ~5,000 |
| LTM search results | ~1,500 |
| Conversation history (10 turns) | Variable (~5,000–30,000) |

The system prompt, tools, and LTM are essentially fixed costs sent with every message — that's 10,000 tokens per call. With about 100 calls per day, the monthly fixed cost alone is:

```
10,000 tokens × 100 calls/day × 30 days = 30,000,000 tokens/month
```

At Claude Haiku 4.5's Bedrock input token rate ($1.10/1M tokens for Japan cross-region inference), that's $33/month in fixed costs alone. As a solo developer, having ~$33/month go toward tool definitions that might not even be used on a given call was painful.


## Splitting into Sub-Agents

To reduce the number of tool definitions the main agent loads, I created domain-specific sub-agents and had the main agent call them via the `@tool` decorator.

```
[Before: Monolithic]
Main Agent
├── System prompt (all domain rules)
└── 28 tools ← sent every single call

[After: Sub-agent split]
Main Agent
├── System prompt (generic rules only)
├── DateTool (3 tools)      ← frequently used, kept in main
├── TavilySearch (1 tool)   ← same
├── task_agent      ← defined as @tool (4 tools)
├── calendar_agent  ← defined as @tool (6 tools)
├── gmail_agent     ← defined as @tool (4 tools)
├── notion_agent    ← defined as @tool (6 tools)
├── diary_agent     ← defined as @tool (2 tools)
├── briefing_agent  ← defined as @tool (multi-domain tools)
└── twitter_agent   ← defined as @tool (2 tools)
```


### Sub-Agent Implementation

With Strands Agents' `@tool` decorator, you can define a sub-agent as a tool for the main agent:

```python
@tool
def calendar_agent(request: str) -> str:
    """Google Calendar sub-agent. Handles listing, availability checks, creating, updating, and deleting events.

    Args:
        request: A request related to the owner's calendar
    """
    try:
        agent = Agent(
            model=BedrockModel(
                model_id="jp.anthropic.claude-haiku-4-5-20251001-v1:0",
                region_name="ap-northeast-1",
                streaming=True,
            ),
            system_prompt="You are a Google Calendar specialist assistant...",
            tools=_calendar_tools,  # calendar tools only
            callback_handler=None,
        )
        result = agent(request)
        return str(result)
    except Exception as e:
        return f"Calendar operation error: {e}"
```


### System Prompt Reduction

By splitting sub-agents by domain, domain-specific rules moved from the main system prompt to each sub-agent's prompt.

Before: Main prompt contained all domain rules
```
- Calendar rules (duplicate checks, deletion confirmation, etc.)
- Gmail rules (draft only, date search caveats, etc.)
- Notion rules (property formats, database mappings, etc.)
- Briefing procedure (5 detailed sections)
- Diary creation flow (interview → generate → save)
- ...
```

After: Main prompt only has sub-agent list and delegation rules
```
## Sub-agent Coordination
- task_agent: Task management (list, add, complete, update)
- calendar_agent: Google Calendar (get, create, update, delete events)
- gmail_agent: Gmail (search, get, create drafts)
- ...

### Delegation Rules
- Describe requests to sub-agents in detail
- Rephrase sub-agent results in your own words
```

This reduced the system prompt from ~7,400 characters to ~3,800 characters.


### Cost Reduction

Comparing the main agent's fixed cost per call:

| Component | Before (Monolithic) | After (Sub-agent split) |
|-----------|--------------------|-----------------------|
| System prompt | ~3,500 tokens | ~2,000 tokens |
| Tool definitions | 28 tools (~5,000 tokens) | 12 tools (~2,500 tokens) |
| LTM search results | ~1,500 tokens | ~1,500 tokens |
| **Fixed cost total** | **~10,000 tokens** | **~6,000 tokens** |

Those 4,000 tokens weren't deleted — they moved to the sub-agents. Here's the per-call input token cost for each sub-agent:

| Sub-agent | Prompt | Tool Defs | Request Message | Total |
|-----------|--------|-----------|----------------|-------|
| task_agent | ~400 | ~400 | ~100 | ~900 |
| calendar_agent | ~400 | ~850 | ~100 | ~1,350 |
| gmail_agent | ~400 | ~400 | ~100 | ~900 |
| notion_agent | ~400 | ~700 | ~100 | ~1,200 |
| briefing_agent | ~500 | ~2,500 | ~100 | ~3,100 |
| diary_agent | ~400 | ~200 | ~100 | ~700 |
| twitter_agent | ~400 | ~150 | ~100 | ~650 |

If you just add everything up, the "After" total is actually higher. But the key insight is reducing tokens sent on *every* call. For example, the briefing_agent loads Gmail, Calendar, and task tools all at once and has complex rules — it's expensive, but it only runs once a day. Before, all those definitions were loaded on every single call. Now they only load when needed.


### Monthly Cost Impact

Estimating with ~100 calls per day:

```
[Main agent fixed cost reduction (every call)]
  4,000 tokens/call × 100 calls/day × 30 days = 12,000,000 tokens/month

[Sub-agent additional cost (only when invoked)]
  Assuming ~60% of calls (60/day) trigger one sub-agent
  Average 900 tokens/call × 60 calls/day × 30 days = 1,620,000 tokens/month
  *briefing_agent (~3,100 tokens) runs once/day, calculated separately
  briefing: 3,100 tokens × 30 days = 93,000 tokens/month

[Net savings]
  12,000,000 - 1,620,000 - 93,000 = 10,287,000 tokens/month
```

At Claude Haiku 4.5's Bedrock input token rate ($1.10/1M tokens, Japan cross-region inference), that's roughly **$11/month in input token savings**.


## Other Optimizations

I also made several complementary changes:

### Conversation Window Reduction
Changed `SlidingWindowConversationManager`'s `window_size` from 15 to 10.
Savings: $3–5/month

### LTM Search Result Reduction
Reduced `top_k` across LTM strategies (total 18 → 10 results).
Savings: $2–3/month

### Lightweight Pipeline Agents
For automated tasks like scheduled tweets and news collection, I was using the full main agent. I replaced these with lightweight dedicated agents that share memory but carry only minimal tools.
Savings: $2–3/month

### Total Savings

| Optimization | Est. Monthly Savings |
|-------------|---------------------|
| Sub-agent splitting | $11 |
| Conversation window reduction | $3–5 |
| LTM result reduction | $2–3 |
| Lightweight pipeline agents | $2–3 |
| **Total** | **$18–22** |


## Wrapping Up

So I managed to cut costs to some degree, but it's still expensive...! If you have any clever cost reduction ideas, I'd love to hear them.

(Fortunately I was recently selected as an AWS Community Builder, so I'm hoping for some AWS credits!)
