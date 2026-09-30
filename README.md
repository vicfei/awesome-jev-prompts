# Awesome Jev Prompts

> A curated library of question patterns, anti-patterns, and calibration notes for [Jev](https://typesafe.ai/blog/introducing-system-one-models-and-jev) — TypeSafe AI's System One model. **Question design is the prompt engineering of typed decisions.**

[![Stars](https://img.shields.io/github/stars/vicfei/awesome-jev-prompts?style=social&label=Star)](https://github.com/vicfei/awesome-jev-prompts/stargazers)
[![Last commit](https://img.shields.io/github/last-commit/vicfei/awesome-jev-prompts?label=last%20commit)](https://github.com/vicfei/awesome-jev-prompts/commits)
[![Link check](https://github.com/vicfei/awesome-jev-prompts/actions/workflows/link-check.yml/badge.svg)](https://github.com/vicfei/awesome-jev-prompts/actions/workflows/link-check.yml)
[![License: CC0](https://img.shields.io/badge/license-CC0-007ec6)](#license)

**中文版 README 在[这里](README.zh-CN.md)。**

Jev returns typed answers — **Choice**, **Score**, **Noul** — with probabilities, in 70–500 ms. It never writes text, so none of your prompt-engineering habits transfer. What transfers instead is **question design**: how you split a decision into atomic judgments, how you word option descriptions, where you set thresholds, and when you refuse to trust the number. This list collects the patterns that work — and the anti-patterns that quietly break production systems.

## What is Jev?

A "System One" model (the fast-thinking reference is Kahneman's): unstructured state in, typed probabilistic decisions out. It gives up string generation for type-safe, calibrated outputs, which makes it two orders of magnitude faster and cheaper than chat models on judgment-shaped work.

| Primitive | You supply | You get back |
|---|---|---|
| **Choice** | `instructions` + `criteria` dict (option → description) | picked option, per-option `probabilities`, `confidence` |
| **Score** | `instructions` + `criteria` as an **ordered** rubric list | probability-weighted `score` (can land between levels), `legend`, `probabilities`, `confidence` |
| **Noul** | `instructions` | `noul`: probability the statement is true, 0–1 |

Quick facts (as of Jev 1.13 — verify against [docs](https://docs.typesafe.ai/models)):

| | |
|---|---|
| Endpoint | `POST https://api.typesafe.ai/v1/systemone` |
| Aliases / version | `jev-latest`, `jev-preview` → `jev-1.13.0` (aliases can move — pin when thresholds matter) |
| Pricing | $0.042 per 1M input tokens; output tokens free |
| Context | 64k tokens per request (32k state + longest question) |
| Limits | 250k tokens/sec; 1,200 requests/min |
| Modality | Text only — no images, audio, or video |

## Quick start

```python
# python -m pip install typesafe-sdk
from typesafe_sdk import Choice, Noul, Score, TypeSafeClient

state = {
    "ticket": "I was charged twice and need the duplicate refunded today.",
    "account_tier": "business",
}

with TypeSafeClient() as client:
    response = client.system_one(
        state=state,
        questions={
            "intent": Choice(
                instructions="What is the customer's main request?",
                criteria={
                    "refund": "The customer wants money returned.",
                    "technical_help": "The customer needs a bug or integration fixed.",
                    "information": "The customer is asking for information only.",
                    "other": "None of the other options clearly fits.",
                },
            ),
            "is_urgent": Noul(
                instructions="Does the ticket explicitly communicate time pressure?",
            ),
            "frustration": Score(
                instructions="How frustrated does the customer appear?",
                criteria=[
                    "Calm and neutral",
                    "Concerned but civil",
                    "Very angry or using strong language",
                ],
            ),
        },
    )

print(response.answers["intent"].choice)
print(response.answers["intent"].probabilities)
print(response.answers["is_urgent"].noul)
print(response.answers["frustration"].score)
```

<details>
<summary>TypeScript equivalent</summary>

```ts
// npm install @typesafe-ai/sdk
import { choice, noul, score, TypeSafeClient } from "@typesafe-ai/sdk";

const client = new TypeSafeClient();
const result = await client.systemOne({
  state: { ticket: "I was charged twice and need the duplicate refunded today." },
  questions: {
    intent: choice("What is the customer's main request?", {
      refund: "The customer wants money returned.",
      technical_help: "The customer needs a bug or integration fixed.",
      information: "The customer is asking for information only.",
      other: "None of the other options clearly fits.",
    }),
    isUrgent: noul("Does the ticket explicitly communicate time pressure?"),
    frustration: score("How frustrated does the customer appear?", [
      "Calm and neutral",
      "Concerned but civil",
      "Very angry or using strong language",
    ]),
  },
});
```

</details>

*(Quick-start example adapted from [Anil-matcha/awesome-jev-by-typesafe](https://github.com/Anil-matcha/awesome-jev-by-typesafe), MIT.)*

## The library — 43 entries in 8 categories

Every entry gives the question template, threshold/wiring guidance, known failure modes, and sources.

| Category | Entries | What it covers |
|---|---|---|
| [Choice patterns](categories/choice-patterns.md) | 6 | Intent routing, tool selection, model routing, best-of-N, document types, skill routing |
| [Score patterns](categories/score-patterns.md) | 5 | Severity, quality gates, moderation, RAG relevance, priority queues |
| [Noul patterns](categories/noul-patterns.md) | 5 | Policy checks, dedup, citation checks, escalation, retry control |
| [Routing & triage](categories/routing-and-triage.md) | 4 | Inbox triage, ticket queues, RAG filtering, document streams |
| [Guardrails & verification](categories/guardrails-and-verification.md) | 5 | Output guardrails, jailbreak detection, validation, review gates |
| [Context compaction](categories/context-compaction.md) | 3 | Keep-or-drop, summarize-or-quote, tool-result pruning |
| [Anti-patterns](categories/anti-patterns.md) | 10 | The ten ways Jev questions go wrong, with fixes |
| [Calibration & eval](categories/calibration-and-eval.md) | 5 | Thresholds from logs, versioned questions, shadow mode, System Two handoff |

**The one rule that generates most of the others:** *questions describe judgments; code owns composition, thresholds, and side effects.*

## Official resources

- [Docs](https://docs.typesafe.ai/) — [Primitives](https://docs.typesafe.ai/primitives) · [Patterns](https://docs.typesafe.ai/patterns) · [Confidence](https://docs.typesafe.ai/confidence) · [State](https://docs.typesafe.ai/concepts/state) · [Use-case map](https://docs.typesafe.ai/concepts/use-case-map) · [Quick start](https://docs.typesafe.ai/introduction/quickstart) · [Agent skill](https://docs.typesafe.ai/agent-skill) · [Models](https://docs.typesafe.ai/models)
- SDKs — [Python](https://github.com/typesafe-ai/typesafe-sdk-python) · [JavaScript](https://github.com/typesafe-ai/typesafe-sdk-js) · [Skills repo](https://github.com/typesafe-ai/skills) · [System One adapter](https://github.com/typesafe-ai/system-one-adapter-python)
- [TypeSafeAI/jev-harness](https://github.com/TypeSafeAI/jev-harness) — official coding harness: "the model proposes, Jev supplies evidence, code decides"
- [Evals](https://evals.typesafe.ai/) · [Console & playground](https://console.typesafe.ai/) · [Launch post](https://typesafe.ai/blog/introducing-system-one-models-and-jev)
- Also available via [Vercel AI Gateway](https://vercel.com/ai-gateway/models/jev) and [Cloudflare Workers AI](https://developers.cloudflare.com/ai/models/typesafe/jev/)

## Related lists

<!-- related-lists:start -->
| List | Focus | Stars |
|---|---|---:|
| [yibie/awesome-jev](https://github.com/yibie/awesome-jev) | General list, highest-frequency updates | 2,011 |
| [heyjunpenn/awesome-jev](https://github.com/heyjunpenn/awesome-jev) | 900+ project catalog with companion site | 903 |
| [Anil-matcha/awesome-jev-by-typesafe](https://github.com/Anil-matcha/awesome-jev-by-typesafe) | Use cases, starter code, design rules | 886 |
| [v-modal/awesome-jev-tools](https://github.com/v-modal/awesome-jev-tools) | Tools list with inclusion criteria | 738 |
| [logicrw/awesome-jev-projects](https://github.com/logicrw/awesome-jev-projects) | Ecosystem radar web app, auto GitHub sync | 629 |
| [kydlikebtc/awesome-jev](https://github.com/kydlikebtc/awesome-jev) | Machine-readable catalog by decision pattern | 587 |
| [AnotiaWang/awesome-jev](https://github.com/AnotiaWang/awesome-jev) | Classic minimal list, open replicas & benchmarks | 580 |
| [AbdelStark/awesome-typesafe-jev](https://github.com/AbdelStark/awesome-typesafe-jev) | Field guide with platform routing & evals | 549 |
| [cobanov/awesome-jev](https://github.com/cobanov/awesome-jev) | Curated list with dated review notes | 470 |
| [walidboulanouar/awesome-jev-use-cases](https://github.com/walidboulanouar/awesome-jev-use-cases) | Demos ranked by social metrics, limits & cost | 350 |
<!-- related-lists:end -->

*Star counts refresh daily via CI.*

## Contributing

Found a pattern that works, or an anti-pattern that bit you? PRs and issues welcome — one pattern per PR, sources required, template mandatory. See [CONTRIBUTING.md](CONTRIBUTING.md). Corrections take priority over additions — a wrong row costs more than a missing one.

## License

[CC0 1.0](LICENSE) — dedicated to the public domain. Use everything freely.

**Disclaimer:** this is an independent community resource. It is not affiliated with or endorsed by TypeSafe AI. Facts (pricing, limits, behavior) are cited from public sources and can change — always verify against the [official docs](https://docs.typesafe.ai/).

<!-- last-checked:start -->
*Last checked: 2026-09-30*
<!-- last-checked:end -->
