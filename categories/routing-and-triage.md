# Routing & triage — sorting streams of unstructured input

Composite pipelines: one Jev request carries several atomic questions (they are evaluated independently), and code composes the outcome. The launch post's "smart if-statement" territory — classify, route, score, branch.

The same shape now runs at cluster scale: [vLLM Semantic Router](https://github.com/vllm-project/semantic-router) (6k★, self-described "programmable decision layer") routes each call across models, compute, and locations under a quality × latency × cost × compliance policy — triage with infrastructure budgets. **Community-observed**, the largest deployment of this category's pattern.

Templates use the Python SDK (`python -m pip install typesafe-sdk`).

---

### Confidence-gated reasoning
**Primitive:** Composite (Noul gate → expensive path) · **Added:** 2026-10-28 · **Status:** community-observed

Route each decision by the model's own confidence: answer directly when confident, trigger explicit reasoning only when uncertain. This is the AutoThink pattern — StartLux 27B AutoThink ships it natively (`think_mode: "auto"`, `gate: 0.6`); OpenAI's Decisions API applies the same principle (GPT-6 Luna reasons only on hard cases).

```python
# The gate is a threshold on the decision model's own confidence:
answer = engine.ask(state, questions)
if answer.confidence < THINK_GATE:
    answer = engine.ask(state, questions, think_mode="deep")   # expensive path
# Above the gate: one forward pass, no reasoning tokens.
```

**Wiring & thresholds**
- The gate threshold is per task: 0.6 is StartLux's default; a security gate might use 0.8, a ranking pre-filter 0.4.
- Budget the expensive path: StartLux caps reasoning at `think_budget` tokens; without a cap, uncertain inputs burn the margin saved by confident ones.
- The confidence signal comes from the same forward pass — no separate uncertainty model needed.

**Failure modes**
- Gate too low: reasoning fires on easy cases, eating the cost advantage. Gate too high: wrong answers ship without review — tune from logged (confidence, correctness) pairs.
- Not all engines support thinking modes (Jev has none); on those, the pattern degenerates to routing to a different (stronger, more expensive) model — same threshold logic.

**Sources:** [StartLux AutoThink](https://github.com/StartLuxLabs/Startlux-Decision) (`think_mode`/`gate`/`think_budget` API) · [OpenAI Decisions API](https://www.kai-waehner.de/blog/2026/10/20/how-decision-models-became-a-new-ai-category-after-jev) (per Waehner's timeline: "trading latency for accuracy on hard cases")

### Inbox / email triage
**Primitive:** Choice + Score + Noul · **Added:** 2026-09-28

One request, three questions: what is it, how urgent, does it need a reply today. The community's favorite cost-flex demo — large batches for cents, because input is $0.042/MTok and output is free.

```python
response = client.system_one(
    state={"message": email_text},
    questions={
        "kind": Choice(
            instructions="What kind of message is this?",
            criteria={
                "action_needed": "Asks me to do something concrete.",
                "fyi": "Informational; no action expected.",
                "spam_promo": "Unsolicited marketing or spam.",
                "personal": "Personal correspondence.",
                "other": "None of the above clearly fits.",
            },
        ),
        "urgency": Score(
            instructions="How soon does this need attention?",
            criteria=["Whenever.", "This week.", "Today.", "Within hours."],
        ),
        "needs_reply": Noul(
            instructions="Does this message explicitly expect a reply?",
        ),
    },
)
```

**Wiring & thresholds**
- Compose the folder/queue in code from the three answers (e.g. `action_needed && urgency >= 2 && needs_reply >= 0.7 → today_queue`) — never ask Jev "which folder?" as one blurred mega-question.
- Batch: many emails share one loop; latency stays under half a second each.

**Failure modes**
- Marketing mail that mimics personal tone lands in `personal` — keep a `spam_promo` description that names the mimicry ("friendly tone but selling something").

**Sources:** [walidboulanouar/awesome-jev-use-cases (demo catalog)](https://github.com/walidboulanouar/awesome-jev-use-cases) · [Launch post](https://typesafe.ai/blog/introducing-system-one-models-and-jev)

---

### Support ticket priority queue
**Primitive:** Choice + Score · **Added:** 2026-09-28**

Department first, severity second — a small hierarchy beats one flat question when the label space is the product of two dimensions.

```python
"department": Choice(
    instructions="Which team owns this ticket?",
    criteria={
        "billing": "Payments, refunds, invoices, subscriptions.",
        "technical": "Bugs, errors, integration problems.",
        "account": "Access, login, permissions, data requests.",
        "unrouted": "Cannot tell from the ticket.",
    },
),
"severity": Score(
    instructions="How severe is the impact described?",
    criteria=[
        "Question or cosmetic issue.",
        "Impaired but workaround exists.",
        "Blocking work for one user.",
        "Blocking many users or losing data.",
    ],
),
```

**Wiring & thresholds**
- `unrouted` → default queue with a human glance; never let the model guess a department to avoid the branch.
- Re-run on every customer reply — state changed, so the answers may have.

**Failure modes**
- Severity creep on angry tickets: frustration language inflates scores. If you also measure tone, do it in a separate Score and let code, not the question, decide they're independent.

**Sources:** [Cookbook — hierarchical classification](https://docs.typesafe.ai/cookbooks/hierarchical_classification) · [Quick-start example](https://github.com/Anil-matcha/awesome-jev-by-typesafe)

---

### RAG passage filtering
**Primitive:** Score + Noul · **Added:** 2026-09-28**

Retrieved 40 chunks, prompt budget fits 8: filter on relevance, verify on entity match, sort, cut.

```python
# per passage, fanned out in parallel:
questions={
    "relevance": Score(
        instructions="How well does this passage answer the question?",
        criteria=[
            "Irrelevant.",
            "Related topic, no answer.",
            "Partially answers.",
            "Directly answers.",
        ],
    ),
    "entity_match": Noul(
        instructions="Does the passage discuss the exact entity the question asks about?",
    ),
}
```

**Wiring & thresholds**
- Keep a passage only if `relevance ≥ 2.5` or (`relevance ≥ 2` and `entity_match ≥ 0.8`); the Noul rescues partial-but-on-entity passages from the cut.
- This runs per passage per query — log score distributions; they're your retrieval-quality monitor for free.

**Failure modes**
- Same-entity-different-question passages score 2 and slip through; relevance criteria should say "answers **this** question", not "is about **this** topic".

**Sources:** [Cookbook — classifying RAG passages](https://docs.typesafe.ai/cookbooks/classifying_rag_passages) · [Cookbook — rerank](https://docs.typesafe.ai/cookbooks/rerank_typesafe) · Community: [hotchpotch/jev-reranker](https://github.com/hotchpotch/jev-reranker), [erendikmenn/jev-rag-benchmark](https://github.com/erendikmenn/jev-rag-benchmark)

---

### Document stream sorting
**Primitive:** Choice · **Added:** 2026-09-28

A firehose of mixed documents (scans, exports, forwards) needs to land in N buckets with an audit trail. Jev classifies; code files, renames, and links.

```python
"bucket": Choice(
    instructions="Which pipeline should process this document?",
    criteria={
        "financial": "Invoices, receipts, statements, expenses.",
        "legal": "Contracts, agreements, policies, notices.",
        "hr": "CVs, applications, employment documents.",
        "junk": "Ads, newsletters, no business content.",
        "manual": "Important-looking; a human should decide.",
    },
),
```

**Wiring & thresholds**
- `manual` is the pressure valve — when its share in your weekly log spikes, a category definition has rotted.
- Pass extracted text (OCR first if needed): Jev is text-only, no images or PDF bytes. Multimodal System One variants ([OneJev](https://github.com/OmniJev/OneJev), [Valen](https://github.com/Liuziyu77/Valen)) can take pixels directly — pattern unchanged, thresholds re-tuned per modality.

**Failure modes**
- Cross-category hybrids (an HR contract) — pick the *processing* owner ("who acts on it"), not the *topic*; pipelines are about actions.

**Sources:** [Docs — use-case map](https://docs.typesafe.ai/concepts/use-case-map) · [Docs — state](https://docs.typesafe.ai/concepts/state)
---

### Market regime routing
**Primitive:** Choice · **Added:** 2026-10-28 · **Status:** derived

Classify the current market regime once per period, then route all downstream strategy calls through that regime's playbook. The Choice is cheap (one call), but it gates expensive model-selection, position-sizing, and risk-parameter decisions.

```python
"regime": Choice(
    instructions="Which market regime best describes the current environment?",
    criteria={
        "trending_bull": "Sustained upward movement with expanding breadth; momentum strategies favored.",
        "trending_bear": "Sustained decline with contracting breadth; capital preservation favored.",
        "range_bound": "Sideways with no sustained directional bias; mean-reversion strategies favored.",
        "high_volatility": "Large swings in either direction; reduce position sizes, widen stops.",
        "regime_unclear": "Signals conflict; default to smallest positions until clarity emerges.",
    })
```

**Wiring & thresholds**
- State should carry a compact market snapshot: index returns over multiple horizons, breadth measures, volatility indicators — not the full time series.
- The "regime_unclear" escape option is load-bearing: forcing a regime call when signals conflict produces false confidence that propagates to every downstream decision.
- Ask once per rebalance period, not per trade — the regime call is a strategic gate, not a tick-level signal.

**Failure modes**
- Regime lag: by the time the model is confident in a new regime, the transition is over. Accept the lag; the value is consistency (not being in the wrong playbook), not foresight.
- Over-granular regimes (six-plus): each added regime reduces per-class sample size and increases misclassification cost. Four to five is the practical cap.

**Sources:** derived from the multi-agent architecture in [TauricResearch/TradingAgents](https://github.com/TauricResearch/TradingAgents) and [HKUDS/Vibe-Trading](https://github.com/HKUDS/Vibe-Trading)
