---
title: "Improving and Validating Multi-Agent Prompts with Bedrock AgentCore Optimization"
emoji: "🔬"
type: "tech"
topics: [aws, bedrock, agentcore, strandsagents, aiagent]
published: false
---

> This article is an AI-assisted translation of a Japanese technical article.

## Introduction

In April 2026, Amazon Bedrock AgentCore added a new capability called **Optimization**, which takes real agent traces and proposes prompt improvements based on them.
https://aws.amazon.com/about-aws/whats-new/2026/05/bedrock-agentcore-optimization-preview/

In this article, I apply AgentCore Optimization to a Strands Agents-as-Tools setup (a main agent that wraps sub-agents as `@tool`s) and walk through what actually happens. What kind of improvements does Recommendations propose? Does the change hold up under real traffic in an A/B test? And how does it feel to put this into operation? Those are the questions I tried to answer.


## Inside AgentCore Optimization

Let me start by laying out what Optimization actually consists of.

### The three capabilities

| Capability | Role |
|---|---|
| Recommendations | Takes real trace logs plus a target Evaluator as input, and has an AI generate improved versions of system prompts and tool descriptions. Instead of you iterating manually, Recommendations does the iteration for you. |
| Configuration bundles | Externalizes prompts and tool descriptions out of source code and version-manages them on the AgentCore side. You can change agent behavior just by swapping the bundled values — no code change, no redeploy. Also used to run two settings side by side in the A/B test described below. |
| A/B testing | Routes real traffic via AgentCore Gateway between two variants (control / treatment), scoring each side with an Evaluator. You can compare which prompt actually performs better in production, with statistical backing. |

The official docs describe these three as a "continuous improvement loop": Recommendations generates an improved version → Configuration bundles version-controls it → A/B testing validates the effect under real traffic. The three capabilities are designed to cycle.

### Prerequisites

Following the official docs, the setup requires:

- An agent built with Strands Agents
- Deployed to AgentCore Runtime with Observability enabled
- CloudWatch Transaction Search enabled


## Building the test setup

For the experiment I built a multi-agent setup with Strands Agents — a main agent that delegates to specialized sub-agents for weather and news, wired together with the Agents-as-Tools pattern.

The repo:
https://github.com/n-yokomachi/agentcore-optimization-lab


### Configuration bundle structure

To make a setup A/B-testable, prompts and tool descriptions need to be externalized in `configBundles` inside `agentcore.json`. The bundle structure I ended up with:

```json: agentcore.json (configBundles section)
{
  "components": {
    "{{runtime:agentsAsToolsLab}}": {
      "configuration": {
        "systemPrompt": "You are an assistant that answers questions about weather and news.",
        "weather_agent": "Get weather",
        "news_agent": "Get news"
      }
    }
  }
}
```

A note on the prompts: I deliberately wrote them quite carelessly so the impact of Recommendations would be easy to see.

`{{runtime:agentsAsToolsLab}}` is an agentcore CLI placeholder; it gets resolved to the actual Runtime ARN at deploy time.

One quirk: the tool descriptions (`weather_agent` / `news_agent`) sit directly under `configuration` as flat siblings. This shape matches how the Recommendations API resolves the tool description path. The default structure that the AgentCore CLI generates with `--with-config-bundle` (which nests them under `toolDescriptions`) didn't resolve correctly for tool description Recommendations, so I flattened it and that worked.

Adding the bundle definition and deploying are both done through the AgentCore CLI:

```bash
agentcore add config-bundle
agentcore deploy
```

### Wiring the bundle into the agent

To inject bundle values into the Runtime dynamically, we use Strands' hook mechanism. The `ConfigBundleHook` class overrides the main agent's system prompt at `BeforeInvocationEvent` and each tool's description at `BeforeToolCallEvent`.

```python
class ConfigBundleHook(HookProvider):
    def register_hooks(self, registry: HookRegistry, **kwargs: Any) -> None:
        registry.add_callback(BeforeInvocationEvent, self._inject_system_prompt)
        registry.add_callback(BeforeToolCallEvent, self._override_tool_description)

    def _inject_system_prompt(self, event: BeforeInvocationEvent) -> None:
        config = BedrockAgentCoreContext.get_config_bundle()
        event.agent.system_prompt = config.get("systemPrompt", DEFAULT_SYSTEM_PROMPT)

    def _override_tool_description(self, event: BeforeToolCallEvent) -> None:
        config = BedrockAgentCoreContext.get_config_bundle()
        override = config.get(event.tool_use["name"])
        if override and event.selected_tool:
            spec = event.selected_tool.tool_spec
            if spec and "description" in spec:
                spec["description"] = override
```

This Hook class is based on the template the AgentCore CLI generates with `--with-config-bundle`. Because I flattened the bundle structure, the tool description lookup (`config.get(event.tool_use["name"])`) is simpler than the generated default.


## Recommendations and A/B test run

For the experiment I generated trace logs from 8 English queries × 5 rounds = 40 sessions, then ran both system-prompt and tool-description Recommendations against the agent.

```bash
agentcore run recommendation --type system-prompt
agentcore run recommendation --type tool-description
```

### Recommendations on the system prompt

The original system prompt and the Recommendations output are both visible in the AWS Console. The improved prompt now factors in tool calling — phrases like "call both tools in parallel" and "use news_agent to find related news" appear in the suggestion.

![Image description](https://dev-to-uploads.s3.amazonaws.com/uploads/articles/hjdkk6w49xzsqiw9jmof.png)

### Recommendations on the tool descriptions

The before/after for tool descriptions is visible in the same way. The descriptions are filled out more thoroughly, and they explicitly call out the possibility of parallel use with the other sub-agent — phrases like "Often used alongside news_agent" and "Often used alongside weather_agent".

![Image description](https://dev-to-uploads.s3.amazonaws.com/uploads/articles/f8ambufewxhojes95gz0.png)

### A/B test for effect validation

To verify that the Recommendations output actually moves the needle, I ran an A/B test as well.

- Control variant (C): bundle version with the human-authored prompt and tool descriptions
- Treatment variant (T1): bundle version with the Recommendations output applied
- Traffic split: 50/50 (sticky session-to-variant assignment by session ID)
- Online Evaluator: `Builtin.GoalSuccessRate`
- Traffic volume: 8 queries × 5 rounds = 40 sessions

To run the A/B test you need an HTTP Gateway and an Online evaluation config. The HTTP Gateway has to be added by hand to `httpGateways` in `agentcore.json` (no `add` subcommand seems to exist for it at the moment). The Online evaluation config is added with `agentcore add online-eval`.

```json: agentcore.json (httpGateways section)
"httpGateways": [
  {
    "name": "agentsAsToolsLabGateway",
    "runtimeRef": "agentsAsToolsLab"
  }
]
```

```bash
agentcore add online-eval
```

Then add the A/B test itself and register everything in one go with deploy.

```bash
agentcore add ab-test
agentcore deploy
```

Traffic generation is done by POSTing to the AgentCore Gateway URL with SigV4 auth. `agentcore invoke` hits the Runtime directly, so for the A/B test we have to go through the Gateway URL. Here's the script I used:

```python
GATEWAY_URL = "https://agentsastoolslabgateway-XXXXX.gateway.bedrock-agentcore.us-west-2.amazonaws.com/agentsAsToolsLab/invocations"
credentials = Session().get_credentials()

def invoke_one(query: str):
    sid = str(uuid.uuid4())
    payload = json.dumps({"prompt": query}).encode()
    req = AWSRequest(method="POST", url=GATEWAY_URL, data=payload, headers={
        "Content-Type": "application/json",
        "X-Amzn-Bedrock-AgentCore-Runtime-Session-Id": sid,
    })
    SigV4Auth(credentials, "bedrock-agentcore", "us-west-2").add_auth(req)
    http_req = urllib.request.Request(GATEWAY_URL, data=payload, headers=dict(req.headers), method="POST")
    with urllib.request.urlopen(http_req, timeout=180) as resp:
        return sid, resp.status
```

The A/B test results are visible in the AWS Console under "Bedrock AgentCore > Optimizations > A/B Tests".

Here are the numbers:

| Metric | Value | Meaning |
|---|---|---|
| Sessions routed to control | 21 | Number of sessions routed to the control variant |
| Sessions routed to variant | 19 | Number of sessions routed to the treatment variant |
| Control average (Goal Success Rate) | 0.48 | Mean Goal Success Rate of the control variant |
| Variant average | 0.53 | Mean Goal Success Rate of the treatment variant |
| Variant improvement | Not significant: +10.5% (p=0.95) | Treatment shows a +10.5% improvement over control, but not statistically significant (p>0.05) |

![Image description](https://dev-to-uploads.s3.amazonaws.com/uploads/articles/9urda45vfdrcrzstbrgv.png)

Directionally, the treatment is ahead by +5pt absolute (= +10.5% relative). So the Recommendations output is moving things in the right direction, but with only 40 sessions there isn't enough data to claim statistical significance. Since the original goal — confirming Recommendations actually works end to end — is met, and going further would start to hurt my wallet, I'm cutting the experiment off here.


## Where to draw the line with Recommendations

This is just from this experiment, but if I sort the improvement patterns Recommendations produced, I think the natural division of labor between Recommendations and the developer looks something like this:

| Owner | Domain |
| ---- | ---- |
| Recommendations | Mention of parallel calls, naming of related elements, multilingual support callouts, response format directives, safety mechanisms, proactive behavior |
| Developer | Domain context, business logic, data interpretation policy |

So when you put Recommendations into your operational loop, the parts you (the human) still need to write are:

- Domain-specific context (specific customer business processes, external API specs, etc.)
- Business logic (output constraints, compliance, billing rules, etc.)
- Data interpretation policy (e.g. "when this field is empty, treat it as X")

For everything else — the "general patterns of good prompt writing" — it might be reasonable to let Recommendations handle it. That's the takeaway for me from this experiment.


## Wrap-up

So that was a hands-on look at AgentCore Optimization on an Agents-as-Tools setup. The takeaways:

- Recommendations extracts general patterns like parallel invocation, tangential topic handling, response format, and safety mechanisms
- A boundary becomes visible between what humans should write (domain context, business logic) and what we can hand off to Recommendations
- The A/B testing capability and its outputs are confirmed working, but at this experiment's scale the sample size isn't enough for significance

That's it. I hope this is useful for anyone planning to try Optimization themselves.


## Bonus: Japanese system prompts getting misflagged as prompt injection?

When I ran the system prompt Recommendation with a Japanese prompt like `--inline "あなたは天気とニュースに答えるアシスタント。"`, I got this error:

```
[ValidationException] The provided content was detected as unsafe by 
prompt attack protection. Please review your system prompt and try again.
```

After narrowing it down:

- Fails regardless of Evaluator (`Builtin.GoalSuccessRate` / `Builtin.Helpfulness`)
- Fails whether via bundle or inline mode
- Fails even when I rewrite the Japanese prompt in different ways
- Works as soon as I switch to English

So the only difference that flips the outcome is the language of the prompt. Tool description Recommendations work fine in Japanese, by the way.

For that reason, all the experiments in this article ended up being run with English prompts.


## References

https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/optimization.html
https://github.com/aws/agentcore-cli
https://aws.amazon.com/about-aws/whats-new/2026/05/bedrock-agentcore-optimization-preview/
