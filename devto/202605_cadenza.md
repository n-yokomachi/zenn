---
title: "I Built an Issue-Based Claude Code Plugin 'cadenza' for Technical Output Creation"
emoji: "🎼"
type: "idea"
topics: [claudecode, claude, ai, aiagent, productivity]
published: false
---

## Introduction

When I write blog posts or give lightning talks, I often feel that my output isn't quite as engaging as I'd like. Reflecting on it briefly, I think the causes are: (1) trying to cram in too much and ending up wide but shallow, (2) staying at the level of mere introduction without doing my own verification or analysis, and (3) the structure lacking dynamic pacing and feeling flat.

To address these issues and make my output more effective, efficient, and sustainable, I created a Claude Code plugin. (The contents are simply a collection of Skills, so it can be used with other agents as well.)

The repository is below. Anyone can install and use it by following the README.md.
https://github.com/n-yokomachi/cadenza

## Plugin Overview

The plugin is named `cadenza`. It comes from the musical term "cadenza" (a free movement in a concerto where the soloist showcases their virtuosity). The idea is that while the structured workflow is strictly enforced, the user's free will drives the issue framing and verification.

cadenza is a Claude Code plugin that divides technical output creation into 5 phases. Each phase functions as a "gate," preventing rushed writing while encouraging users to clarify their questions.

The fundamental design philosophy is based on issue-first knowledge production theories such as Kazuto Ataka's *Issue Driven* (Eiji Press, 2010).

### The 5-phase structure

| Phase | Skill | Role |
|---|---|---|
| 1. Planning | `/cadenza:issue-finding` | Identify what question is worth answering |
| 2. Design | `/cadenza:issue-decomposition` | Decompose into sub-issues and design the storyline |
| 3. Storyboard | `/cadenza:storyboarding` | Decide the "presentation" (code snippets, diagrams, tables, etc.) for each sub-issue |
| 4. Verification | `/cadenza:analysis-execution` | Implement, measure, and create diagrams according to the storyboard |
| 5. Finishing | `/cadenza:output-crafting` | Generate the Markdown deliverable |

In addition, there are 2 skills for review.

- `/cadenza:output-proofread` — AI-driven exhaustive proofreading (fact-checking + language proofreading)
- `/cadenza:output-review` — Author-driven review cycle support

Each skill confirms "Shall we proceed to the next phase?" upon completion, and if approved, calls the next skill in a chain. The final deliverable of cadenza is a single general-purpose Markdown file at `./.cadenza/output.md`. The intended use is to base blog posts or slide decks on this Markdown.

### Each phase functions as a "gate"

A key feature of this plugin is that each phase checks whether the start conditions for downstream phases are met. For example, when `storyboarding` starts up, it checks whether the Phase 2 (Issue Decomposition) section has been written to `./.cadenza/state.md`, and if not, it directs the user to run `issue-decomposition` first.

This structurally prevents phase skipping.

Each phase also defines "upstream regression signals." For example, if the storyline starts to drift during the design phase, the plugin guides the user back to the planning phase to reconsider the issue.

### Enforcing user accountability

As an aside: even though I'm introducing this AI tool for output creation, I still take a critical stance toward output that is simply written by AI alone.
https://zenn.dev/yokomachi/articles/202512_ai_article_comment

For this reason, cadenza is designed so that output cannot be produced by simply leaving everything to the agent. To ensure that everything written remains the user's responsibility, mandatory steps such as user confirmation are placed at each phase, so the entire process cannot be fully delegated to the agent.

Roughly, the user-led and agent-led steps are as follows.

| Phase / Skill | User-led steps | Agent-led steps |
|--------------|-------------------|---------------|
| Phase 1: issue-finding | Confirm primary information / articulate target audience, problem hypothesis, and post-read change / explicitly consent to the one-line issue | Survey existing content (WebSearch) / 3-condition check |
| Phase 2: issue-decomposition | Agree on the decomposition pattern / articulate a hypothesis for each sub-issue / agree on the storyline pattern / pin the claim down to one sentence | Storyline validity check |
| Phase 3: storyboarding | Agree on format and specifications for each sub-issue / specify output style | Storyboard assembly / storyboard review |
| Phase 4: analysis-execution | Decide whether to regress upstream / run verification / request additional checks beyond the skill's defaults | Classify verification type / pin premises down / run verification / structure results |
| Phase 5: output-crafting | Select the title (1 from 3 candidates) | Assemble structure / write TL;DR / write each section / final check |
| output-proofread | Decide which findings to accept and edit accordingly | Technical accuracy check / language proofreading / generate proofreading report |
| output-review | User-led overall (author re-reads, asks questions, issues editing instructions) | Provide grounded answers to questions / edit only when instructed |

The leadership balance in Phase 4 (verification) shifts depending on the type of verification. For verifications like Implementation, Measurement, and Reproduction, the agent handles the baseline planning, while the actual hands-on work — or directing the agent on separate implementation tasks — is user-led. On the other hand, Comparison (research of public information) and Diagramming are AI-led from start to finish.

Ideally I'd want a guard that prevents output unless the user demonstrably understands the verification results (for example, the agent quizzing the user on the results and refusing to create the output unless they answer correctly), but I'll leave that to the user's (my own) conscience.


## How to Use

### Installation

The cadenza repository itself functions as a Claude Code marketplace. You can use it just by registering the marketplace and installing the plugin.

```bash
claude plugin marketplace add github.com/n-yokomachi/cadenza
claude plugin install cadenza@cadenza
```

After installation, reload the plugin with `/reload-plugins`, then check that cadenza is installed with `/plugins`.

### Launch

Launch Claude Code in the project directory where you want to write a technical output, and start the flow by running `/cadenza:issue-finding`.

```
/cadenza:issue-finding
```

### State management

cadenza creates a `./.cadenza/` directory directly under the working directory and consolidates state and deliverables there.

```
./.cadenza/
├── state.md          # Consolidates confirmed information from each phase
└── output.md         # Final deliverable
```

Confirmed information from Phase 1 through Phase 5 is appended to `state.md` sequentially. Each skill checks that the upstream phase's section exists in `state.md` before proceeding downstream, so phase skipping is structurally prevented.

If you work in a different project directory, `./.cadenza/` will naturally be a separate one, so you can produce multiple articles in parallel.

### Suspend and resume

Since the result of each phase is written out to `state.md`, you can resume even if the Claude Code session is disconnected. Running `/cadenza:<next phase>` in a new session loads the contents of `state.md` and lets you pick up where you left off.


## Bonus: Actual Flow

The following is a walkthrough showing how cadenza actually behaves during output creation. The sample topic is "Quantitative Comparison of AI Coding Agent Free Tiers as of May 2026," and we'll follow how cadenza behaves at each step. The output content itself is also just a sample — I haven't reviewed it properly, so please take it with a grain of salt.

### Phase 1: Issue Finding

When `/cadenza:issue-finding` is launched, it starts with theme selection, hypothesis, and issue framing.

The following 5 steps run in order.

| Step | Lead | Interaction details |
|---|------|----------|
| 1 | User | Confirm primary information → I've used all 7 tools / no experience getting stuck. Selected "Continue as research/survey by an experienced user" |
| 2 | User | Articulate target audience / reader's problem hypothesis / post-read change in 1-2 sentences |
| 3 | AI | Survey existing articles via WebSearch → Found that the combination "free-tier-focused × quantitative × Japanese" was not yet covered |
| 4 | AI | All 3 condition checks (essential choice / deep hypothesis / answerable) passed |
| 5 | User | Finalize the one-line issue and give explicit consent |

The final issue was decided as follows.

> As of May 2026, how should individual developers wanting to try AI coding agents choose the "tool to try first" that fits their use case from the free tiers of 7 major tools (Claude Code / Codex CLI / Cursor / Gemini CLI / GitHub Copilot / Windsurf / Kiro), and what usage patterns should they consider for paid upgrades?


### Phase 2: Issue Decomposition

Launching `/cadenza:issue-decomposition` enters the process of building the storyline.

The following 5 steps run.

| Step | Lead | Interaction details |
|---|------|----------|
| 1 | AI proposal → user agreement | Decomposition pattern selection. This time, Compare-Select (Options → Criteria → Decision) was proposed → adopted |
| 2 | User (this time: AI draft → user edit) | One-line hypothesis for each sub-issue. Since I had already answered "no experience getting stuck / no unique elements" in Phase 1, the AI provided a draft that I adopted as-is |
| 3 | AI proposal → user agreement | Storyline pattern. Sky-Rain-Umbrella, suitable for long-form articles, was proposed → adopted |
| 4 | User | Pin the claim down to one sentence. Selected from 3 candidates |
| 5 | AI-led | Storyline validity check (5 items). All items passed |

The storyline was settled as follows.

| Role | Question |
|------|------|
| ☁️ Sky (fact) | What does it look like when each tool's free-tier limits are aligned in common units? |
| 🌧️ Rain (interpretation) | Do the differences in limits stem from each provider's business model? (Does the 3-strategy classification of growth-first / paid conversion / platform infiltration hold up?) |
| ☂️ Umbrella (action) | How should we sort the tools by use case (completion / agent / refactoring) into "try first" vs. "paid required"? |

The claim is as follows.
> Each provider's free tier reflects **3 strategic patterns** (growth-first / paid conversion / platform infiltration), and the right approach is to choose by matching the reader's use case to each provider's strategic pattern.


### Phase 3: Storyboarding

Launching `/cadenza:storyboarding` lets you design "how to show it" (code / diagrams / tables / benchmarks, etc.) and "what needs to be verified vs. what won't be" for each sub-issue.

| Step | Lead | Interaction details |
|---|------|----------|
| 1, 2 | AI proposal → user agreement | Propose the format (presentation) and specifications (content) for each sub-issue |
| 3 | AI proposal → user agreement | Adjust to match the output style. This time I specified "drop flat onto Zenn, no diagrams, tables only" |
| 4 | AI-led | Organize all verification items and out-of-scope items (what won't be done) |
| 5 | AI-led | Storyboard review (5 items). All items passed |

The policy is to express each sub-issue in a single table (Mermaid diagrams are not used).

| Sub-issue | Format | Specification overview |
|----------|------|------------|
| ☁️ Sky (sub-issue 1) | Comparison table | Rows = 7 tools / Columns = official limits, common-unit conversion (tasks/day), billing trigger, credit card requirement |
| 🌧️ Rain (sub-issue 2) | 3-strategy classification table | Rows = 7 tools / Columns = strategy pattern, limit generosity, offering type, basis for judgment |
| ☂️ Umbrella (sub-issue 3) | Decision matrix + descriptive paragraph | A 21-cell grid of rows = 3 use cases × columns = 7 tools, marked with ◎ / ○ / △ / ×, followed by a decision-guidance paragraph |


### Phase 4: Analysis Execution

In `/cadenza:analysis-execution`, the actual verification work is executed. This time, since it's just a sample, I scoped everything down to web research only.

#### Verification execution and main findings

I aggregated the official pricing pages of the 7 tools and the business model background of each company via WebSearch, and defined the baseline unit "1 coding task = 1 file edit + ~5 completions, or 1 agent invocation" based on the author's usage experience. Using this, I converted each tool's free tier into "tasks/day."

Main findings:

- For Tab completion generosity, Windsurf (unlimited) and GitHub Copilot Free (equivalent to 2,000/month) stand out
- For agent-driven use, Gemini CLI (1,000 req/day) is more generous than expected
- Claude Code / Codex CLI's free tiers are essentially zero (Pro at $20/month is required for serious use)
- Refactoring and large-scale tasks exceed the free tier across all providers; a paid plan is required

#### Issue reconsideration (partial)

The 3-strategy names (growth-first / paid conversion / platform infiltration) set in Phase 2 turned out to be inaccurate when checked against the data; "platform on-ramp / pure-tool paid funnel / completion-focused giveaway" proved to be a more persuasive classification.

cadenza defines 3 types of upstream regression signals (storyline collapse / new issue discovery / format mismatch). Since this finding didn't match any of them — the underlying structure of three strategy patterns held up, only the labels needed updating — I decided that returning to Phase 2 was unnecessary, and updated only the hypothesis names within Phase 4.

Partial shifts in the storyline driven by data are within the expected range, and cadenza is designed to ask the user whether to handle such shifts by "going all the way back upstream" or "updating in place."

#### Materials to hand off to Phase 5

- Comparison table (7 tools × 4 columns: official limits / task conversion / billing trigger / credit-card requirement)
- 3-strategy classification table (revised, with the basis for each tool's classification)
- Decision matrix (3 use cases × 7 tools = 21 cells of ◎/○/△/× judgments)
- Updated claim candidate (version with the 3-strategy labels replaced)

That wraps up Phase 4. Next is Phase 5 (Output Crafting), which generates `./.cadenza/output.md`.

### Phase 5: Output Crafting

`/cadenza:output-crafting` writes out the final Markdown to `./.cadenza/output.md` based on the confirmed information from Phases 1 through 4.

| Step | Lead | Interaction details |
|---|------|----------|
| 1 | AI-led | Build the structural skeleton (Title / TL;DR / Background / one section per sub-issue / Conclusion / References) |
| 2 | AI proposal → user selection | Propose 3 title candidates; user selects one |
| 3 | AI-led | TL;DR / opening (claim + target audience + post-read change in 3-5 lines) |
| 4 | AI-led | Write each sub-issue as its own section. Use the visuals (tables) decided in the Phase 3 storyboard as-is, maintaining storyboard fidelity |
| 5 | AI-led | Final check on code / diagrams / personal info. All 7 final confirmation items passed |


#### Output body

The generated `output.md` is reproduced verbatim below as a raw Markdown source.

```markdown
# AI Coding Agent Free Tiers Reflect 3 Strategies: Sorting 7 Tools by Use Case

## TL;DR

When the free tiers of 7 major AI coding agent tools (Claude Code / Codex CLI / Cursor / Gemini CLI / GitHub Copilot / Windsurf / Kiro) are aligned on a common "tasks/day" unit, each provider's limit design reflects one of 3 business strategies (platform on-ramp / pure-tool paid funnel / completion-focused giveaway). For individual developers, the realistic answer is not to commit to a single tool, but to combine the best free tier for each use case (completion-focused / agent-driven / refactoring or large-scale).

The target audience is individual developers and small-team developers who want to try AI coding agents and quantitatively compare multiple tools before going paid. After reading, you'll be able to gauge the practical value of each tool's free tier in common units, and sort tools that fit your use case into "try first" vs. "free isn't enough — paid required."

## Stance of this article

This comparison is a research / survey-style write-up by an experienced user. The author has actually used all 7 tools, but has no particular experience of "getting stuck" with the free tiers. The purpose is to organize information so that readers about to try them can quantitatively grasp the limits. Read this not as "stories of when I got stuck," but as "a map for those about to try them out."

## Defining the common unit: "1 coding task"

Each provider publishes limits in different units (requests / completions / tokens / premium requests / messages, etc.), so they can't be compared apples-to-apples as-is. This article normalizes them against the following baseline unit.

> **1 coding task = 1 file edit + about 5 completions, or 1 agent invocation**

Here, "completion" means inline completion (short suggestions accepted via Tab), and "agent invocation" treats chat-based instructions or Edit / Cascade-style operations spanning multiple files as 1 unit. Conversion accuracy is roughly ±50% — the goal is approximate comparison of practical usage, not precision.

## Each tool's free tier limits (as of May 2026)

The following organizes each provider's official pricing page side-by-side.

| Tool | Official limit | Common unit conversion (tasks/day) | Billing trigger | Credit card required |
|--------|-----------|------------------------|------------|-----------|
| Claude Code | Pro at $20/month (annual contract: $17/month) required; not usable on the free tier. Some sources indicate that new API accounts receive about $5 in API credit | About 5 tasks/day (rough estimate, dividing $5 of API credit at Claude Sonnet 4.x mid-tier rates, assuming 5,000-10,000 tokens per task, spread over 30 days) | Pro subscription / API credit depletion | Required for both API and Pro subscription |
| Codex CLI | Codex is included with ChatGPT Free / Go, but specific usage limits for Free / Go must be checked individually in the ChatGPT usage dashboard (not listed in the official pricing table) | Not evaluable (limits aren't public, so can't be quantified) | ChatGPT Plus at $20/month | Optional |
| Cursor (Hobby) | Per publicly available info, 2,000 completions + 50 slow premium model requests/month (not directly extractable from the official pricing page; sourced from review articles) | About 13 tasks/day (completion) + about 1.7 premium/day | Monthly quota depletion → Pro at $20 | Not required |
| Gemini CLI | 1,000 requests/day, 60 requests/minute, about 250,000 tokens/minute (Flash model-centric; Pro model is limited. Specific values are checked individually in the Google AI Studio dashboard) | About 200 tasks/day (1 task = 5 requests) | Daily limit / per-minute token limit | Not required (Google account only) |
| GitHub Copilot Free | Officially listed as 2,000 completions/month + 50 agent mode or chat requests/month | About 13 tasks/day (completion) + about 1.7 agent / chat requests/day | Monthly quota depletion → Pro at $10 | Not required |
| Windsurf (Free) | Public info indicates Tab completion is exempt from the usage quota. Advanced features like Cascade are quota-based (not directly extractable from the official pricing page; sourced from review articles) | Completion: effectively unlimited / advanced: a few times/day | Advanced feature use → Pro at $20 | Not required |
| Kiro (Free) | Officially listed as 50 credits/month + an initial 500-credit bonus (must be used within 30 days), with overage at $0.04/credit | Steady-state: about 1.7 credits/day / Initial bonus: about 17 credits/day (vibe mode 1 = 1 credit, spec mode consumes several credits) | Credit depletion → Pro at $20 / additional $0.04/credit | Not required |

> **Note**: The above values are aggregated from each provider's official pricing pages and review articles as of May 2026. Only GitHub Copilot Free and Kiro publish specific free-tier values directly in their official pricing tables. The others (Claude Code / Codex / Cursor / Gemini CLI / Windsurf) require checking separate pages or usage dashboards, or rely on external review articles for the published limits. Please verify each provider's latest official information before actually trying them.

The values span a **5-10× range**. The differences are too large to lump together as the same "free tier."

Laid out side-by-side, you can see significant variation in the generosity of free tiers. Anthropic and OpenAI are essentially zero, Google and Microsoft (GitHub) are more generous, Windsurf is unlimited only for completion, and Amazon's Kiro takes an unusual credit-based approach. This isn't a technical constraint — it's **a reflection of each provider's business model**.

## 3-strategy classification of free tiers

> **Note**: The 3-strategy classification below is this article's original framing, not an established industry taxonomy. It groups providers into 3 categories from this article's perspective, based on strategies that each provider has officially expressed (see "judgment basis" below for citations). Readers are welcome to reclassify along other axes (IDE-embedded / CLI / feature maturity, etc.).

When the free-tier design of the 7 tools is viewed from a strategic perspective using this article's framing, the following 3 patterns emerge.

| Pattern | Name | Characteristics | Tools |
|------|------|------|----------|
| A | Platform on-ramp | Generous free tier draws users into the provider's other services (GitHub / Google Cloud / AWS). Their main business is cloud/platform, and the coding agent serves as an entry point | GitHub Copilot, Gemini CLI, Kiro |
| B | Pure-tool paid funnel | Thin free tier allows trial use, but full use requires a paid plan. The tool itself is the main business, with subscriptions as the primary revenue source | Cursor, Claude Code, Codex CLI |
| C | Completion-focused giveaway | Tab completion is fully released as unlimited; agent and advanced features are gated behind paid tiers. A strategic loss-leader aimed at maximizing IDE adoption | Windsurf |

### Each company's judgment basis (official source citation)

**A. Platform on-ramp**

- **GitHub Copilot**: Microsoft CEO Satya Nadella stated, "Any per user business of ours, whether it's productivity or coding or security, will become a per user and usage business," positioning Copilot as part of Microsoft's company-wide per-user + usage strategy ([GitHub Blog: usage-based billing](https://github.blog/news-insights/company-news/github-copilot-is-moving-to-usage-based-billing/)). Copilot Free can be read as the entry point, aiming for stickiness to GitHub accounts and repositories plus monetization through Enterprise integration.
- **Gemini CLI**: Google's official blog announcement explicitly states, "industry's largest allowance with 60 model requests per minute and 1,000 requests per day at no charge," and lays out a tiered funnel where additional quota moves to "usage-based billing with Google AI Studio or Vertex AI key" ([Google Blog: Introducing Gemini CLI](https://blog.google/technology/developers/introducing-gemini-cli-open-source-ai-agent/)). It's designed as the entry point for Cloud migration: Free → Standard → Vertex AI Enterprise.
- **Kiro**: AWS positions Kiro as the successor to Amazon Q Developer and has announced that no new Q Developer Free Tier accounts will be created going forward ([AWS Blog: Q Developer end-of-support](https://aws.amazon.com/blogs/devops/amazon-q-developer-end-of-support-announcement/)). Signing in with an AWS Builder ID enables direct integration with Amazon Q and the broader AWS ecosystem ([Kiro Authentication docs](https://kiro.dev/docs/getting-started/authentication/)), which reads as a play for AWS developer acquisition.

**B. Pure-tool paid funnel**

- **Cursor**: Anysphere has reached **$1B in annualized revenue with over 1 million paying users** on Cursor alone, with the $20 Pro subscription as its revenue mainstay. Hobby Free is positioned as an evaluation tier: "a real comparison... most developers who give it a serious two-week test either upgrade to Pro or decide the tool is not for them" (interpretation based on public benchmarks + review articles).
- **Claude Code**: Anthropic Head of Growth Amol Avasare publicly explained the bundling strategy with Pro/Max: "Max launched a year prior, it didn't include Claude Code, and the company later bundled Claude Code into Max after it took off" ([reported by The Register](https://www.theregister.com/2026/04/22/anthropic_removes_claude_code_pro/)). Claude Code is positioned as a lever for boosting subscription engagement.
- **Codex CLI**: OpenAI's official blog states, "Codex is included with ChatGPT Plus, Pro, Business, and Enterprise plans—no separate subscription needed" ([OpenAI: Introducing Codex](https://openai.com/index/introducing-codex/)), and signing in to Plus / Pro also grants free API credit ($5/$50). The tight Free / Go limits can be read as a deliberate push toward the ChatGPT subscription.

**C. Completion-focused giveaway**

- **Windsurf**: Cognition (Devin's parent company) acquired Windsurf for about $250M in December 2025. Cognition CEO Scott Wu laid out the strategy in an official blog post: "start by integrating Cognition's autonomous AI-powered engineer Devin into Windsurf's IDE," and "developers can plan tasks in Windsurf and launch a team of Devins" ([Cognition Blog: Windsurf acquisition](https://cognition.ai/blog/windsurf)). The Free plan's unlimited Tab completion accelerates IDE adoption, while monetization comes from advanced features (Cascade / Devin integration).

Once you see the strategy patterns, you realize that even similar numbers like 2,000 completions/month **play opposite roles depending on the strategy**. For GitHub Copilot it acts as "an entry point for user retention (a steady allowance to keep users in the GitHub ecosystem long-term)," while for Cursor it acts as "a cutoff line before paid (a mechanism to push serious users toward Pro at $20/month)." That's the contrast.

## Sorting by use case × tool

Based on the strategy patterns, the table below judges how far the 7 tools can be pushed across 3 typical use cases.

| Use case | Claude Code | Codex CLI | Cursor | Gemini CLI | GitHub Copilot | Windsurf | Kiro |
|------|-------------|-----------|--------|------------|----------------|----------|------|
| Completion-focused (Tab completion as main) | × | × | △ | ○ | ◎ | ◎ | △ |
| Agent-driven (delegating tasks) | △ | × | △ | ◎ | △ | △ | ○ |
| Refactoring / large-scale (multi-file editing) | × | × | × | △ | × | △ | × |

Legend: ◎ try first / ○ worth trying / △ paid required / × skip

### Reading by use case

**Completion-focused users** (typing in the IDE while heavily using Tab completion) have **two clear winners: GitHub Copilot Free and Windsurf**. Copilot Free offers 2,000 completions/month, while Windsurf has fully unlimited Tab. Copilot brings strong integration with the GitHub ecosystem, while Windsurf stands out for the polish of the IDE itself. Gemini CLI's 1,000 req/day is hard to dismiss for completion use, but being CLI-based, it's a fundamentally different experience from in-IDE completion. Cursor and Kiro deplete quota quickly under completion-focused use, and Claude Code and Codex CLI don't target completion as their primary use case (both lean agent).

**Agent-driven users** (delegating tasks via chat, auto-editing multiple files) will find that, perhaps surprisingly, **Gemini CLI Free is the strongest option**. Even though it's Flash-model-centric, 1,000 requests/day is plenty to try agent tasks, and being usable with just a Google account is a big plus. Kiro also suits agent delegation in spec mode, but burns through credits quickly under its credit-based system. Claude Code has high-quality agent design, but with a free tier of essentially zero, Pro is required for serious use. Cursor's 50 premium requests/month is insufficient for trying agent-driven workflows, and Codex CLI's free-tier limits aren't public, so it falls outside the scope of evaluation here.

**Refactoring / large-scale users** (structural changes spanning multiple files, heavy editing) unfortunately face **structurally insufficient free tiers across the board**. Cursor's 50 premium runs out in a few days, as do Kiro's 50 credits and Copilot Free's 50 agent / chat requests. Windsurf's Cascade is also limited to a few uses per day on the free tier. Gemini CLI's 1,000 requests/day is theoretically generous, but keeping multi-file editing within 5 requests per task is practically infeasible, and the quota gets consumed regardless. **For serious use of AI agents in this category, a paid upgrade to one of the tools should be assumed from the outset.**

## Conclusion

The fact that free-tier strategies divide into 3 patterns gives the chooser a clear guideline: **"match your use case to each provider's strategy pattern."**

- **Completion-focused trial** → Pattern A (GitHub Copilot Free / Windsurf) is enough. You get the benefits of the platform on-ramp while staying within the free tier
- **Agent-driven trial** → Short-term verification with Pattern A (Gemini CLI Free, or Kiro's initial bonus)
- **Refactoring / large-scale serious use** → A paid upgrade to one of the Pattern B tools (Cursor Pro / Claude Code Pro) is required

In other words, **individual developers shouldn't commit to a single tool but should combine free tiers by use case** — that's the realistic answer as of May 2026. Once you read each provider's strategy against your own use case, the right timing for going paid also becomes apparent on its own.

## Aside: OSS BYO API tools

While outside the scope of this article, the following OSS tools are worth knowing about as a separate category — **"the tool itself is $0 since it's OSS, but you pay separately for LLM API usage"**.

- **Cline**: A VS Code extension; an OSS tool whose popularity is rapidly rising. You bring your own API keys for Anthropic / OpenAI / Google, etc.
- **Aider**: A terminal-CLI-based OSS tool, aimed at power users
- **Continue**: OSS that runs as an extension for VS Code / JetBrains

These follow a "tool free, API at cost" model, so they don't fit on this article's "quantitative comparison of free tiers" axis. They are, however, an option for developers who don't want to pay a fixed monthly API fee or who prefer to manage billing themselves.

## References

- [Claude Code Pricing (Anthropic)](https://claude.com/pricing)
- [Codex Pricing (OpenAI Developers)](https://developers.openai.com/codex/pricing)
- [Cursor Models & Pricing](https://cursor.com/docs/models-and-pricing)
- [Gemini CLI Quotas (Google AI)](https://ai.google.dev/gemini-api/docs/rate-limits)
- [GitHub Copilot Plans](https://github.com/features/copilot/plans)
- [Windsurf Pricing](https://windsurf.com/pricing)
- [Kiro Pricing](https://kiro.dev/pricing/)
```

