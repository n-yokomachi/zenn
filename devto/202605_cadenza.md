---
title: "I Built a Claude Code Plugin That Supports Technical Output Creation"
emoji: "🎼"
type: "idea"
topics: [claudecode, claude, ai, aiagent, productivity]
published: false
---

> This article is an AI-assisted translation of a Japanese technical article.

> This article was written by a human, with generative AI used for plugin implementation and article proofreading.

## Introduction

When I write blog posts or give lightning talks, I often feel that my output is somehow not interesting. Looking back briefly, I think the causes are: (1) trying to cram in too much, ending up wide but shallow, (2) staying at the level of mere introduction without my own verification or analysis, and (3) lacking pacing in the structure, leaving it flat.

To address these issues and make my output more effective, efficient, and sustainable, I created a Claude Code plugin. (The contents are simply a collection of Skills, so it can be used with other agents as well.)

The repository is below. Anyone can install and use it by following the README.md.
https://github.com/n-yokomachi/cadenza

## Plugin Overview

The plugin is named `cadenza`. It comes from the musical term "cadenza" (a free movement in a concerto where the soloist showcases their virtuosity). The nuance is that while a structured workflow is strictly maintained, the user's free will is leveraged in the issue framing and verification.

cadenza is a Claude Code plugin that divides technical output creation into 5 phases. Each phase functions as a "gate," preventing rushed writing while encouraging users to clarify their questions.

The fundamental design philosophy is based on issue-first knowledge production theories such as Kazuto Ataka's *Issue Driven* (Eiji Press, 2010).

### The 5-phase structure

| Phase | Skill | Role |
|---|---|---|
| 1. Planning | `/cadenza:issue-finding` | Identify "what is the question worth answering" |
| 2. Design | `/cadenza:issue-decomposition` | Decompose into sub-issues and design the storyline |
| 3. Storyboard | `/cadenza:storyboarding` | Decide the "presentation" (code snippets, diagrams, tables, etc.) for each sub-issue |
| 4. Verification | `/cadenza:analysis-execution` | Implement, measure, and create diagrams according to the storyboard |
| 5. Finishing | `/cadenza:output-crafting` | Generate the Markdown deliverable |

In addition, there are 2 skills for review.

- `/cadenza:output-proofread` — AI-driven exhaustive proofreading (fact-checking + language proofreading)
- `/cadenza:output-review` — Author-driven review cycle support

Each skill confirms "Shall we proceed to the next phase?" upon completion, and if approved, calls the next skill in a chain. The final deliverable of cadenza is a single general-purpose Markdown file at `./.cadenza/output.md`. The intended use is to base blog posts or slide decks on this Markdown.

### Each phase functions as a "gate"

A key feature of this plugin is that each phase checks the start conditions of downstream phases. For example, when `storyboarding` starts up, it confirms whether the Phase 2 (Issue Decomposition) section is written in `./.cadenza/state.md`, and if not, it guides the user to run `issue-decomposition` first.

This structurally prevents phase skipping.

Each phase also defines "upstream regression signals." For example, if the storyline starts to drift in the design phase, guidance to return to the planning phase and reconsider the issue is shown.

### Enforcing user accountability

By the way, while I am introducing this AI tool for output creation, I still take a negative stance on output that is simply written by AI alone.
https://zenn.dev/yokomachi/articles/202512_ai_article_comment

For this reason, output by cadenza cannot be created by simply leaving everything to the agent. To ensure that everything written becomes the user's responsibility, mandatory steps such as user confirmation are placed at each phase, so the entire process cannot be fully delegated to the agent.

Roughly, the user-led and agent-led steps are as follows.

| Phase / Skill | User-led steps | Agent-led steps |
|--------------|-------------------|---------------|
| Phase 1: issue-finding | Confirm primary information / Articulate target audience, problem hypothesis, post-read change / Explicit consent to the one-line issue | Existing content survey (WebSearch) / 3-condition check |
| Phase 2: issue-decomposition | Agree on decomposition pattern / Articulate hypothesis for each sub-issue / Agree on storyline pattern / Fix claim in one sentence | Storyline validity check |
| Phase 3: storyboarding | Agree on format and specifications for each sub-issue / Specify output style | Storyboard assembly / Storyboard review |
| Phase 4: analysis-execution | Decide on upstream regression / Execute verification / Direct additional checks beyond skill standards | Classify verification type / Fix premises / Execute verification / Structure results |
| Phase 5: output-crafting | Title selection (1 from 3 candidates) | Structure assembly / Write TL;DR / Write each section / Final check |
| output-proofread | Decide whether to accept findings, edit | Technical accuracy check / Language proofreading / Generate proofreading report |
| output-review | User-led overall (author re-reads, asks questions, gives editing instructions) | Provide grounded answers to questions / Edit only when instructed by user |

The Phase 4 verification phase has different leadership balance depending on the type of verification. For verifications like Implementation, Measurement, and Reproduction, the agent handles the baseline planning, while the actual hands-on work or instructing the agent in separate implementation tasks is user-led. On the other hand, Comparison (research of public information) and Diagramming are AI-led through execution.

Ideally I'd want a guard that prevents output unless the user understands the verification results (for example, the agent gives the user a quiz on the verification results, and won't create the output unless the user answers correctly), but I'll leave that to the user's (my own) conscience.


## How to Use

### Installation

The cadenza repository itself functions as a Claude Code marketplace. You can use it just by registering the marketplace and installing the plugin.

```bash: Terminal
claude plugin marketplace add github.com/n-yokomachi/cadenza
claude plugin install cadenza@cadenza
```

After installation, reload the plugin with `/reload-plugins`, then check that cadenza is installed with `/plugins`.

### Launch

Launch Claude Code in the directory of the project where you want to write a technical output, and start the flow by running `/cadenza:issue-finding`.

```
/cadenza:issue-finding
```

### State management

cadenza creates a `./.cadenza/` directory directly under the working directory and consolidates state and deliverables here.

```
./.cadenza/
├── state.md          # Consolidates confirmed information from each phase
└── output.md         # Final deliverable
```

Confirmed information from Phase 1 to Phase 5 is appended to `state.md` sequentially. Each skill confirms that the upstream phase section exists in `state.md` before proceeding downstream, so phase skipping is structurally prevented.

If you work in a different project directory, `./.cadenza/` will naturally be a different one, allowing parallel production of multiple articles.

### Suspend and resume

Since each phase's completion is written out to `state.md`, you can resume even if the Claude Code session is disconnected. By running `/cadenza:<next phase>` in a new session, you can start where you left off by loading the contents of `state.md`.


## Bonus: Actual Flow

The following is a sample to confirm how cadenza actually behaves in output creation. The sample topic is "Quantitative Comparison of AI Coding Agent Free Tiers as of May 2026," and we'll follow how cadenza behaves in sequence. The output content is also just a sample. I haven't reviewed it properly, so please take it with a grain of salt.

### Phase 1: Issue Finding

When `/cadenza:issue-finding` is launched, it starts with theme, hypothesis, and issue framing.

The following 5 steps run in order.

| Step | Lead | Interaction details |
|---|------|----------|
| 1 | User | Confirm primary information → All 7 tools used / No experience getting stuck. Selected "Continue as research/survey by user with experience" |
| 2 | User | Articulate target audience / reader's problem hypothesis / post-read change in 1-2 sentences |
| 3 | AI | Survey existing articles via WebSearch → Found that the combination "free-tier-focused × quantitative × Japanese" is unfilled |
| 4 | AI | All 3 condition checks (essential choice / deep hypothesis / answerable) passed |
| 5 | User | Finalize the one-line issue and give explicit consent |

The final issue was decided as follows.

> As of May 2026, how should individual developers wanting to try AI coding agents choose the "tool to try first" that fits their use case from the free tiers of 7 major tools (Claude Code / Codex CLI / Cursor / Gemini CLI / GitHub Copilot / Windsurf / Kiro), and what usage patterns should they consider for paid upgrades?


### Phase 2: Issue Decomposition

When `/cadenza:issue-decomposition` is launched, it enters the process of building the storyline.

The following 5 steps run.

| Step | Lead | Interaction details |
|---|------|----------|
| 1 | AI proposal → User agreement | Decomposition pattern selection. This time, Compare-Select (Options → Criteria → Decision) was proposed → adopted |
| 2 | User (this time, AI draft → user editing) | One-line hypothesis for each sub-issue. Since I had answered "no experience getting stuck / no unique elements" in Phase 1, the AI provided a draft that was adopted as-is |
| 3 | AI proposal → User agreement | Storyline pattern. Sky-Rain-Umbrella, suitable for long-form articles, was proposed → adopted |
| 4 | User | Fix the claim in one sentence. Selected from 3 candidates |
| 5 | AI-led | Storyline validity check (5 items). All items passed |

The following storyline was decided.

| Role | Question |
|------|------|
| ☁️ Sky (fact) | What does it look like when each tool's free tier limits are aligned in common units? |
| 🌧️ Rain (interpretation) | Do the differences in limits come from each company's business model? (Does the 3-strategy classification of growth-first / paid conversion / platform infiltration hold?) |
| ☂️ Umbrella (action) | How do we sort by use case (completion / agent / refactoring) into "try first" vs. "paid required"? |

The claim is as follows.
> Each company's free tier reflects **3 strategic patterns** (growth-first / paid conversion / platform infiltration), and the right answer is to choose by matching the reader's use case with each company's strategic pattern.


### Phase 3: Storyboarding

When `/cadenza:storyboarding` is launched, you design "what to show with" (code/diagrams/tables/benchmarks, etc.) and "what needs to be verified vs. what won't be verified" for each sub-issue.

| Step | Lead | Interaction details |
|---|------|----------|
| 1, 2 | AI proposal → User agreement | Propose format (presentation) and specifications (content) for each sub-issue |
| 3 | AI proposal → User agreement | Adjust to match output style. This time I specified "drop flat onto Zenn, no diagrams, tables only" |
| 4 | AI-led | Organize all verification items and excluded items (what won't be done) |
| 5 | AI-led | Storyboard review (5 items). All items passed |

The policy is to express each sub-issue in one table (Mermaid diagrams are not adopted).

| Sub-issue | Format | Specification overview |
|----------|------|------------|
| ☁️ Sky (sub-issue 1) | Comparison table | Rows = 7 tools / Columns = official limits, common unit conversion (tasks/day), billing trigger, credit card requirement |
| 🌧️ Rain (sub-issue 2) | 3-strategy classification table | Rows = 7 tools / Columns = strategy pattern, limit thickness, offering form, judgment basis |
| ☂️ Umbrella (sub-issue 3) | Decision matrix + descriptive paragraph | 21 cells of rows = 3 use cases × columns = 7 tools with judgments (◎ / ○ / △ / ×), with decision guidance paragraph below |


### Phase 4: Analysis Execution

In `/cadenza:analysis-execution`, the actual verification work is executed. This time, I adjusted everything to be completed by web research only. Since it's a sample.

#### Verification execution and main findings

I aggregated the official pricing pages of the 7 tools and the business model background of each company via WebSearch, and defined the baseline unit "1 coding task = 1 file edit + ~5 completions or 1 agent invocation" based on the author's usage experience. Following this, I converted each tool's free tier into "tasks/day."

Main findings:

- For Tab completion thickness, Windsurf (unlimited) and GitHub Copilot Free (equivalent to 2,000/month) stand out
- For agent-driven use, Gemini CLI (1,000 req/day) is thicker than expected
- Claude Code / Codex CLI's free tier is essentially zero (Pro $20/month is required for full use)
- Refactoring and large-scale tasks have insufficient free tier across all companies, paid is required

#### Issue reconsideration (partial occurrence)

The 3-strategy names (growth-first / paid conversion / platform infiltration) set in Phase 2 turned out to be inaccurate when viewed from the data, and "platform attraction / pure tool paid conversion / completion-focused liberation" turned out to be a more persuasive classification.

cadenza defines 3 types of upstream regression signals (storyline collapse / new issue discovery / format mismatch). Since this finding doesn't match any of them — the structure of dividing into 3 strategies is maintained, only the labels are updated — I decided that no return to Phase 2 was needed, and to update only the hypothesis names within Phase 4.

The storyline partially shaking from the data is within the expected range, and cadenza is designed to ask the user whether to handle that shake by "going all upstream" or "updating in place."

#### Materials to hand over to Phase 5

- Comparison table (7 tools × 4 columns: official limits / task conversion / billing trigger / credit card requirement)
- 3-strategy classification table (revised, with judgment basis for each tool)
- Decision matrix (3 use cases × 7 tools = 21 cells of ◎/○/△/× judgment)
- Updated claim candidate (version with 3-strategy labels replaced)

This completes Phase 4. Next is Phase 5 (Output Crafting), which generates `./.cadenza/output.md`.

### Phase 5: Output Crafting

`/cadenza:output-crafting` writes out the final Markdown to `./.cadenza/output.md` based on the confirmed information from Phase 1 through 4 so far.

| Step | Lead | Interaction details |
|---|------|----------|
| 1 | AI-led | Build the structural skeleton (Title / TL;DR / Background / one section per sub-issue / Conclusion / References) |
| 2 | AI proposal → User selection | Propose 3 title candidates, user selects |
| 3 | AI-led | TL;DR / Opening (claim + target audience + post-read change in 3-5 lines) |
| 4 | AI-led | Write each sub-issue one section at a time. Use the visuals (tables) decided in the Phase 3 storyboard as-is, maintaining storyboard fidelity |
| 5 | AI-led | Final check on code/diagrams/personal info. Passed all 7 final confirmation items |


#### Output body

The output content is pasted below as-is.

<details>
<summary>output.md</summary>

# AI Coding Agent Free Tiers Reflect 3 Strategies: Sorting 7 Tools by Use Case

## TL;DR

When the free tiers of 7 major AI coding agent tools (Claude Code / Codex CLI / Cursor / Gemini CLI / GitHub Copilot / Windsurf / Kiro) are aligned in the common unit of "tasks/day," the limit design of each company reflects 3 business strategies (platform attraction / pure tool paid conversion / completion-focused liberation). For individual developers, the realistic answer is not to use a single tool, but to combine the optimal free tier for each use case (completion-focused / agent-driven / refactoring / large-scale).

The target audience is individual developers and small-team developers who want to try AI coding agents, who want to quantitatively compare multiple tools before paid upgrade. After reading, you'll grasp the practicality of each tool's free tier in common units, and be able to sort tools that fit your use case into "try first" vs. "free isn't enough, paid required."

## Stance of this article

This comparison is a research/survey-style organization by an experienced user. The author has actually used all 7 tools, but has no particular experience of "getting stuck" with the free tiers. The purpose is to organize information so that readers about to try them can quantitatively grasp the limits. Read this not as "stories of when I got stuck" but as "a map for those going to try them out."

## Definition of common unit "1 coding task"

Each company's limits are published in different units (requests / completions / tokens / premium requests / messages, etc.) and cannot be compared cross-cuttingly as-is. This article normalizes with the following baseline unit.

> **1 coding task = 1 file edit + about 5 completions or 1 agent invocation**

Here, "completion" means inline completion (short candidates accepted with Tab), and "agent invocation" treats chat-based instructions or Edit / Cascade-style operations spanning multiple files as 1 unit. The conversion accuracy assumes ±50%, designed to compare practical feel approximately.

## Each tool's free tier limits (as of May 2026)

The following is the result of organizing each company's official pricing page side-by-side.

| Tool | Official limit | Common unit conversion (tasks/day) | Billing trigger | Credit card required |
|--------|-----------|------------------------|------------|-----------|
| Claude Code | Pro $20/month (annual contract $17/month) required. Cannot be used in Free tier. There is information that new API accounts receive about $5 of API credit | About 5 tasks/day (rough estimate diluting $5 of API credit by Claude Sonnet 4.x mid-tier rates, assuming 5,000-10,000 tokens per task, spread over 30 days) | Pro subscription / API credit depleted | Required for both API and Pro subscription |
| Codex CLI | Codex is included in ChatGPT Free / Go, but specific usage limits for Free / Go are individually checked in the ChatGPT usage dashboard (not listed in official pricing table) | Cannot be evaluated (limits not public, cannot quantify) | To ChatGPT Plus $20/month | Optional |
| Cursor (Hobby) | According to public information, 2,000 completions + 50 slow premium model requests/month (cannot be directly extracted from official pricing page, referencing review articles) | About 13 tasks/day (completion) + about 1.7 premium/day | Monthly quota depletion → Pro $20 | Not required |
| Gemini CLI | 1,000 requests/day, 60 requests/minute, about 250,000 tokens/minute (Flash model-centric, Pro model is limited. Specific values are individually checked in Google AI Studio dashboard) | About 200 tasks/day (1 task = 5 requests conversion) | Daily limit / per-minute token limit | Not required (Google account only) |
| GitHub Copilot Free | Officially listed as 2,000 completions/month + 50 agent mode or chat requests/month | About 13 tasks/day (completion) + about 1.7 agent/chat requests/day | Monthly quota depletion → Pro $10 | Not required |
| Windsurf (Free) | Public information that Tab completion is exempt from usage quota. Advanced features like Cascade are quota-based (cannot be directly extracted from official pricing page, referencing review articles) | Completion: roughly unlimited / advanced: a few times/day | Advanced feature use → Pro $20 | Not required |
| Kiro (Free) | Officially listed as 50 credits/month + initial 500 credits (used within 30 days) bonus, $0.04/credit beyond | Persistent: about 1.7 credits/day / Initial: about 17 credits/day (vibe mode 1 = 1 credit, spec mode consumes several credits) | Credit depletion → Pro $20 / additional $0.04/credit | Not required |

> **Note**: The above values are aggregated from each company's official pricing pages and review articles as of May 2026. The official pricing pages that publish specific Free tier values in tables are only GitHub Copilot Free and Kiro. Others (Claude Code / Codex / Cursor / Gemini CLI / Windsurf) require individual confirmation on separate pages or usage dashboards, or the source of published limit information depends on external review articles. Please verify the latest official information before actual trial.

The numerical range opens **5-10 times**. The differences are too large to lump together as the same "free tier."

When laid out, you can see significant bias in the thickness of the free tier. Anthropic and OpenAI are essentially zero, Google and Microsoft (GitHub) are thicker, Windsurf is unlimited only for completion, and Amazon's Kiro is an irregular design with credit-based system. This is not a technical constraint but **a reflection of each company's business model**.

## 3-strategy classification of free tiers

> **Note**: The 3-strategy classification below is this article's original organization, not an established taxonomy in the industry. It is grouped into 3 from this article's perspective, based on strategies officially expressed by each company (citations are referenced in each company's judgment basis). Readers are welcome to reclassify by other axes (IDE-embedded / CLI / feature maturity, etc.).

When the free tier design of 7 tools is classified from a strategic perspective in this article's original organization, the following 3 patterns emerge.

| Pattern | Name | Characteristics | Applicable tools |
|------|------|------|----------|
| A | Platform attraction | Thick free tier to attract to own other services (GitHub / Google Cloud / AWS). Main business is cloud/platform, coding agent is the entry | GitHub Copilot, Gemini CLI, Kiro |
| B | Pure tool paid conversion | Thin free tier allows trial but full use is paid premise. Main business is the tool itself, subscription revenue is main | Cursor, Claude Code, Codex CLI |
| C | Completion-focused liberation | Tab completion is unlimited release, agent / advanced features differentiate by paid. Strategic loader aiming for IDE adoption maximization | Windsurf |

### Each company's judgment basis (official source citation)

**A. Platform attraction**

- **GitHub Copilot**: Microsoft CEO Satya Nadella stated "Any per user business of ours, whether it's productivity or coding or security, will become a per user and usage business," positioning Copilot as part of Microsoft's company-wide per-user + usage strategy ([GitHub Blog: usage-based billing](https://github.blog/news-insights/company-news/github-copilot-is-moving-to-usage-based-billing/)). Copilot Free can be interpreted as the entry point, with the aim of stickiness to GitHub accounts and repositories + monetization through Enterprise integration.
- **Gemini CLI**: Google official blog announcement explicitly states "industry's largest allowance with 60 model requests per minute and 1,000 requests per day at no charge," and expresses a tiered funnel where additional quota proceeds to "usage-based billing with Google AI Studio or Vertex AI key" ([Google Blog: Introducing Gemini CLI](https://blog.google/technology/developers/introducing-gemini-cli-open-source-ai-agent/)). Designed as the entry point for Cloud migration: Free → Standard → Vertex AI Enterprise.
- **Kiro**: AWS positions Kiro as the successor to Amazon Q Developer and has announced a strategic change to stop creating new Q Developer Free Tiers ([AWS Blog: Q Developer end-of-support](https://aws.amazon.com/blogs/devops/amazon-q-developer-end-of-support-announcement/)). Designed so that signing in with AWS Builder ID enables direct integration with Amazon Q and the AWS ecosystem ([Kiro Authentication docs](https://kiro.dev/docs/getting-started/authentication/)), readable as targeting AWS developer acquisition.

**B. Pure tool paid conversion**

- **Cursor**: Anysphere has achieved **$1B annualized revenue + over 1 million paying users** with Cursor alone, with $20 Pro subscription as the revenue mainstay. Hobby Free is positioned as an evaluation trial tier: "a real comparison... most developers who give it a serious two-week test either upgrade to Pro or decide the tool is not for them" (interpretation based on public benchmarks + review articles).
- **Claude Code**: Anthropic Head of Growth Amol Avasare officially explained the bundle strategy to Pro/Max: "Max launched a year prior, it didn't include Claude Code, and the company later bundled Claude Code into Max after it took off" ([Reported by The Register](https://www.theregister.com/2026/04/22/anthropic_removes_claude_code_pro/)). Claude Code is positioned as a device to increase subscription engagement.
- **Codex CLI**: OpenAI official blog explicitly states "Codex is included with ChatGPT Plus, Pro, Business, and Enterprise plans—no separate subscription needed" ([OpenAI: Introducing Codex](https://openai.com/index/introducing-codex/)), designed so that signing in to Plus / Pro also grants Free API credit ($5/$50). The strict Free / Go limits can be read as the premise for promoting migration to ChatGPT subscription.

**C. Completion-focused liberation**

- **Windsurf**: Cognition (parent company of Devin) acquired Windsurf for about $250M in December 2025. Cognition CEO Scott Wu expressed the strategy in an official blog: "start by integrating Cognition's autonomous AI-powered engineer Devin into Windsurf's IDE," "developers can plan tasks in Windsurf and launch a team of Devins" ([Cognition Blog: Windsurf acquisition](https://cognition.ai/blog/windsurf)). The Free plan with unlimited Tab completion is a device to accelerate IDE inflow, and can be interpreted as a structure that recovers billing through advanced features (Cascade / Devin integration).

When strategy patterns become visible, you can understand that even similar numbers like 2,000 completions/month **have reversed roles by strategy**. For GitHub Copilot, it functions as "an entry point for user retention (steady provision to keep users in the GitHub ecosystem long)," and for Cursor, "a cutoff line to paid (a device to push serious users to Pro $20/month)" — that's the contrast.

## Sorting by use case × tool

Based on the strategy patterns, the following table judges how far the 7 tools can be used in 3 typical use cases.

| Use case | Claude Code | Codex CLI | Cursor | Gemini CLI | GitHub Copilot | Windsurf | Kiro |
|------|-------------|-----------|--------|------------|----------------|----------|------|
| Completion-focused (Tab completion as main) | × | × | △ | ○ | ◎ | ◎ | △ |
| Agent-driven (delegating tasks) | △ | × | △ | ◎ | △ | △ | ○ |
| Refactoring / large-scale (multi-file editing) | × | × | × | △ | × | △ | × |

Legend: ◎ try first / ○ worth trying / △ paid required / × Skip

### Reading by use case

**Completion-focused users** (style of typing in IDE while heavily using Tab completion) have the **two strongest options of GitHub Copilot Free and Windsurf**. Copilot Free has 2,000 completions/month, Windsurf has fully unlimited Tab. Copilot has strong integration with the GitHub ecosystem, and Windsurf has the feature of high IDE completeness. Gemini CLI's 1,000 req/day for completion use is hard to dismiss, but being CLI-based, it's a different experience from IDE completion. Cursor / Kiro deplete quota quickly with completion-focused use, and Claude Code / Codex CLI don't aim at completion as their main purpose (both are agent-leaning).

**Agent-driven users** (delegating tasks via chat, automatic editing of multiple files) surprisingly have **Gemini CLI Free as the strongest candidate**. Even though it's Flash model-centric, 1,000 requests/day is sufficient for trying agent tasks, and being usable with just a Google account is significant. Kiro is also suitable for agent delegation in spec mode but consumes credits quickly with credit-based system. Claude Code has high-quality agent design but the free tier is essentially zero, requiring Pro for full use. Cursor's 50 premium requests/month is insufficient for agent-driven trial, and Codex CLI's free tier limits are not public, so it's outside the evaluation target.

**Refactoring / large-scale users** (structural changes spanning multiple files, large amounts of Edit) unfortunately have **structurally insufficient free tiers across all options**. Cursor 50 premium is depleted in a few days, Kiro 50 credits the same, Copilot Free's 50 agent / chat requests the same. Windsurf's Cascade is also a few times/day in the free tier. Gemini CLI's 1,000 requests/day is theoretically generous, but suppressing multi-file editing to 5 requests per task is practically difficult, and quota will be consumed in the end. **For full use of AI agents in this use case, paid upgrade of one of the tools should be built into the premise**.

## Conclusion

The free tier strategy that divides into 3 patterns provides a guideline for the chooser: **"match your use case with each company's strategy pattern."**

- **Completion-focused trial** → A pattern (GitHub Copilot Free / Windsurf) is sufficient. Receive the benefits of platform attraction while staying within the free tier
- **Agent-driven trial** → Short-term verification with A pattern (Gemini CLI Free or Kiro initial bonus)
- **Refactoring / large-scale full operation** → Paid upgrade to either of B pattern (Cursor Pro / Claude Code Pro) as a premise

In other words, **individual developers should not narrow down to a single tool but combine free tiers by use case** — that's the realistic answer as of May 2026. Once you read each company's strategy and match it with your use case, the timing of paid upgrade also becomes naturally visible.

## Aside: OSS BYO API series

While outside the scope of this article, the following OSS tools are worth recognizing as **"the tool itself starts at $0 since it's OSS, but LLM API billing is required separately"** — a different axis of existence.

- **Cline**: VS Code extension, OSS rapidly gaining popularity. You bring your own API keys for Anthropic / OpenAI / Google, etc.
- **Aider**: Terminal CLI-based OSS, for power users
- **Continue**: OSS that runs as a VS Code / JetBrains extension

These are "tool free, API at cost" models, so they don't fit on this article's "quantitative comparison of free tiers" axis. However, they are an option for developers who don't want to pay a monthly API fixed fee or want to manage billing themselves.

## References

- [Claude Code Pricing (Anthropic)](https://claude.com/pricing)
- [Codex Pricing (OpenAI Developers)](https://developers.openai.com/codex/pricing)
- [Cursor Models & Pricing](https://cursor.com/docs/models-and-pricing)
- [Gemini CLI Quotas (Google AI)](https://ai.google.dev/gemini-api/docs/rate-limits)
- [GitHub Copilot Plans](https://github.com/features/copilot/plans)
- [Windsurf Pricing](https://windsurf.com/pricing)
- [Kiro Pricing](https://kiro.dev/pricing/)

</details>
