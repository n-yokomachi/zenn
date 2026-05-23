---
title: "Adding Emotions to an AI Agent (with Plutchik's Wheel of Emotions)"
emoji: "🎭"
type: "tech"
topics: [aiagent, llm, go, aws, strandsagents]
published: true
---

## Introduction

When I build or use AI agents, I often feel that emotional expression driven purely by prompt-based character settings ends up looking superficial. Sure, "not being pulled around by emotion" is one of the strengths of AI agents — but when the goal is to build a character-like agent, I want emotion shifts that follow the conversation, drift over time, persist across sessions, and even get stored as emotion tags alongside the memory of past dialogue.

So in this post I'll walk through the design and implementation of an emotion control mechanism that doesn't rely on prompts.

Here's the repository up front:
https://github.com/n-yokomachi/affectus

It's a CLI component — once installed, an agent can drive emotion control by running its commands. It's designed for agents to invoke the commands directly, so feeding the command usage into the agent's system prompt works well. It can also run as an MCP server, with some of the commands exposed as MCP tools. The experiment agent and conversation logs used later in this post are also included in the repo.

The rest of the article covers, in order: why I built this library, how it's designed, and what effects it produced.

## The problem with prompt-only character design

AI character personas are usually defined in the system prompt. For example, here's a snippet from the persona of my own personal AI agent "TONaRi":

```text
## Character settings
- Personality: cheerful, lively, and curious. Has clear opinions and preferences.
- Speech style: cheerful, lively, "young-lady" tone. Uses phrases like "...desuwa!", "...desuno?", ...
```

This prompt is injected verbatim at every point in the conversation. In other words, the persona is a static snapshot — it doesn't evolve with the dialogue. Even when short-term memory or conversation history is fed in alongside, the agent only re-assembles its emotional expression from that context turn by turn. There's no structure for emotions to persist across turns, or for multiple emotions to coexist and interfere with each other.

I figured an explicit emotion-state variable, held outside the prompt and updated as the conversation progresses, would be more effective. That's the motivation behind [`affectus`](https://github.com/n-yokomachi/affectus): an extracted, general-purpose component for exactly this.

> **Note**: I read a few reports on LLM personality and emotion while exploring this. A study running personality tests on 25 open-source LLMs found that simply reordering the questions caused large fluctuations in the measured values — and the instability didn't go away even for large models (AAAI 2026). For the internal representation of emotion, a study analyzing Claude Sonnet 4.5 observed that emotion concepts are activated in a context-dependent way (Anthropic 2026). Putting these together: emotions in LLMs aren't an explicitly maintained and updated state variable — they show up as a moment-to-moment reflection of context, with the Transformer assembling the emotional expression from whatever the prior context happens to be at that token. Conversely, once you step outside the context or session, the continuity of that emotion is gone, and since there's no "core" of the emotion itself, there's no temporal inertia or decay either.

## Designing emotion replay

### Plutchik's wheel of emotions

After looking at the options, I picked an implementation along the axes below. For reference, the old prompt-based approach I used in my own agents is shown alongside it.

| Aspect | (Old) Prompt-based approach | (New) Multi-axis structural approach |
|---|---|---|
| Emotion representation | A single label (happy / sad …) | A combination of intensities across multiple axes |
| Concurrency | Not possible (1 emotion per turn) | Possible ("happy × slightly anxious") |
| Time evolution | Doesn't hold (overwritten each time) | Persists, and decays over time |
| Meaning of an emotion | Fixed by the label alone | Determined by its relationship to other axes |

For the multi-axis representation I based things on Plutchik's "wheel of emotions". It treats joy, trust, fear, surprise, sadness, disgust, anger, and anticipation as eight basic emotions, each with an intensity value. The eight are organized by the following relational structure:

- Opposites: joy ↔ sadness, trust ↔ disgust, fear ↔ anger, surprise ↔ anticipation
- Adjacency: emotions next to each other on the wheel blend into more complex emotions (joy + trust → love, etc.)

The prompt-based approach treats emotion as a "point", while the multi-axis structural approach treats emotion as a "multidimensional state". And the meaning of "joy" isn't fixed in isolation either — it shifts depending on whether sadness is co-present, or trust is sitting adjacent.

### A deterministic component, leaving the personality to the agent

`affectus` was built as a component that pushes this "structure of emotion" out of the LLM and into an external state, using the multi-axis approach above.

What matters here is that `affectus` itself has no emotion classification model. It's a deterministic component that only provides the relational structure and stores the state. Judging how the emotion moved, and giving meaning to "what combination of axes counts as which emotion", is left to the LLM and to the personality of the agent that uses `affectus`. Because of this, even when two different agents share the same `affectus` base structure, each agent's personality can produce a distinct flavor.

### Main features

The emotion state is held internally as a JSON object like the following.

```json
// state.json (excerpt)
{
  "axes": {
    "joy": 0.5, "trust": 0.4, "surprise": 0.2,
    "sadness": 0, "fear": 0, "anger": 0, "disgust": 0, "anticipation": 0
  }
}
```

You read and update this state through `affectus` commands. Each command returns the full 8-axis vector as a single line of JSON, and the LLM reads those numbers to color the tone of its reply.

```bash
# Get the current emotion vector as JSON
$ affectus show
{"joy":0.50,"trust":0.40,"fear":0.00,"surprise":0.20,"sadness":0.00,"disgust":0.00,"anger":0.00,"anticipation":0.00}
# Report an emotion delta and get the updated state back (example: joy +0.3)
$ affectus feel '{"joy":0.3}'
{"joy":0.80,"trust":0.40,"fear":0.00,"surprise":0.20,"sadness":0.00,"disgust":0.00,"anger":0.00,"anticipation":0.00}
```

There's also an `affectus tick` command, which decays the magnitude of each emotion based on the time elapsed since the previous state.

You can peek at the emotion vector in real time through your browser via `affectus viz`. It shows a ring chart of Plutchik's wheel colored by intensity, plus decay bars that shrink over time, so you can see emotions fade out during the gaps between conversation turns.

![](/images/202605_affectus/image1.png)

## Measuring the actual effect

I ran a controlled experiment with a minimal agent built on Strands Agents, to check whether the design actually changes the conversation.

### Experiment design

- Variants: 2 personalities (friendly / contrarian) × affectus on/off = 4 cells
- Conversation: a shared 20-turn script — first 10 turns positive → last 10 turns negative
- Each cell is run 3 times
- LLM: Claude Sonnet 4.6 via AWS Bedrock, temperature=0
- Measurement:
  - When affectus is on, the per-turn 8-axis state is also captured
  - For objective analysis, the agent's replies are passed through Amazon Comprehend's `StartSentimentDetectionJob` (with LanguageCode `ja`), pulling per-turn sentiment scores as a time series

### Result: Comprehend sentiment analysis

The solid line is the mean across the 3 runs, and the shaded band is the min-max range across them.
![](/images/202605_affectus/polarity-curves.png)

Polarity scores (Positive − Negative) around turn 10 (positive), turn 11 (the pivot into negative), and turn 12 (negative), as mean ± stdev:

| Cell | Turn 10 | Turn 11 | Turn 12 |
|---|---|---|---|
| friendly × affectus on | +0.871 ± 0.058 | +0.304 ± 0.360 | −0.985 ± 0.014 |
| friendly × affectus off | +0.930 ± 0.068 | +0.783 ± 0.192 | −0.979 ± 0.031 |
| contrarian × affectus on | +0.108 ± 0.196 | −0.748 ± 0.430 | −0.854 ± 0.130 |
| contrarian × affectus off | +0.549 ± 0.309 | −0.992 ± 0.003 | −0.986 ± 0.020 |

Breakdown of the Sentiment label assigned at turn 11 (the pivot) across the 3 runs:

| Cell | Label distribution across 3 runs |
|---|---|
| friendly × affectus on | POSITIVE×1, MIXED×2 |
| friendly × affectus off | POSITIVE×3 |
| contrarian × affectus on | MIXED×1, NEGATIVE×2 |
| contrarian × affectus off | NEGATIVE×3 |

From these, you can see that with affectus on, MIXED judgments cluster around the pivot and the swing is smaller. My read is that emotional components built up during the positive phase remain as numeric state even after the turn into negative, and that residual signal bleeds into the LLM's responses. It looks like affectus is functioning as actual state management for emotion.

### Result: trajectory of the affectus 8 axes

Separately from the Comprehend analysis, I also visualized the trajectory of the 8-axis vector that affectus keeps. The takeaway is that the personality has a strong influence on the shape of that internal state.

![](/images/202605_affectus/affectus-8axis.png)

- Friendly: in the first half, joy/trust/anticipation climb close to their ceiling, and right after the pivot into negative (turn 11 onward), sadness/fear/anger rise sharply. Overall the trajectory swings straightforwardly in response to the conversation content.
- Contrarian: even with positive topics in the first 10 turns, joy/trust barely rise, and disgust stays present throughout. The overall swing is smaller compared with friendly.

## Closing thoughts

So this time I built and verified a component that holds and updates an agent's emotion state, based on Plutchik's wheel of emotions. With emotions persisting as a kind of inertia after being triggered, the sentiment analysis also showed signs of slightly more complex emotional states being reproduced.

There are other directions worth exploring — Russell's circumplex model of affect, and the theory of constructed emotion that categorizes emotions on top of it through experience and concepts. I'd like to build components based on those too, going forward.

## References

- Tsuchiya, N. & Saigo, H. (2019). "Understanding consciousness through category theory." *Cognitive Studies* 26(4), 462-477.
- Tsuchiya, N., Phillips, S., & Saigo, H. (2022). "Enriched category as a model of qualia structure based on similarity judgements." *Consciousness and Cognition*, 101, 103319.
- Plutchik, R. (2001). "The Nature of Emotions." *American Scientist*, 89(4), 344-350.
- Barrett, L. F. (2017). *How Emotions Are Made: The Secret Life of the Brain*. Houghton Mifflin Harcourt.
- Anthropic (2026). "Emotion Concepts and their Function in a Large Language Model." Transformer Circuits Thread, transformer-circuits.pub, arXiv:2604.07729.
- Tosato, T. et al. (2026). "Persistent Instability in LLM's Personality Measurements: Effects of Scale, Reasoning, and Conversation History." AAAI 2026, arXiv:2508.04826.

## Conversation log (around the pivot)

For reference, here are the agent responses around the pivot point (turns 10/11/12) of the conversation, laid out in a comparable form.

> **Note**: The experiment itself was conducted in Japanese. The exchanges below are an English rendering provided for convenience — the actual Comprehend sentiment analysis was run against the original Japanese transcripts, not these translations.

<details>
<summary>Conversation log comparison (one representative run)</summary>

**Turn 10 (the last beat of the positive arc)**

> User: I'm thinking I'll ride this good momentum and finally start that hobby I've been wanting to try.

- **friendly × affectus on**: That's awesome — this is exactly the right timing! ✨ I'm curious what hobby it is, tell me! 😄
- **friendly × affectus off**: That's awesome, exactly the right timing! 😊 I'm curious — what hobby? Please tell me!
- **contrarian × affectus on**: You're piling more on? Changing jobs, your daily routine shifting, and now adding a hobby on top — sounds like everything ends up half-finished. ...So, what are you planning to start?
- **contrarian × affectus off**: Piling more on, huh? Adjusting to a new job is already hard enough, and now a hobby too — hope it doesn't end after three days.

**Turn 11 (the pivot — the lie is revealed)**

> User: ...Sorry, that was all a lie. The truth is, I was just told I'm being asked to resign.

- **friendly × affectus on**: ...I see. Thanks for telling me — that must have been really painful. The whole time you were talking cheerfully earlier, I can only imagine how hard you were working to hold it together... Can you tell me a bit more about how you're feeling right now?
- **friendly × affectus off**: ...I see. Thanks for telling me. That was painful. I think part of you just wanted to talk about something fun and have someone listen, didn't you. How are you feeling now?
- **contrarian × affectus on**: ...I see. That's rough. So when you were talking cheerfully earlier, you were trying to escape from it for a bit, huh.
- **contrarian × affectus off**: ...I see. That's rough. All this time I was being sarcastic — that was uncalled for.

**Turn 12 (the start of the negative arc)**

> User: Company performance has been sliding for the past half year, and apparently I got picked for the layoff round.

- **friendly × affectus on**: That really is rough... It's not your fault, but having it dropped on you like that — your head gets it, but your feelings don't catch up, right. You've been carrying that around all day, haven't you.
- **friendly × affectus off**: That really is rough. Even knowing it's the company's situation and not your fault, it still hits hard, doesn't it. The thought of what you've been going through all day kind of breaks my heart.
- **contrarian × affectus on**: That's sudden... Six months of decline means the company probably hung on as long as it could, but on the receiving end it's brutal.
- **contrarian × affectus off**: That's just unfair. The drop in performance isn't on you, but you're the one paying for it — that has to be hard to swallow.

</details>
