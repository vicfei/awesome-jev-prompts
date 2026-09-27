# Choice patterns — picking from a finite set

Choice takes `instructions` + a `criteria` dict of `option → description` and returns the picked option, per-option `probabilities`, and `confidence`. Choice cardinality is capped at 255; larger sets fall back to a slower two-stage process, so split big taxonomies with hierarchical questions instead.

Templates use the Python SDK (`python -m pip install typesafe-sdk`); the TypeScript equivalent is in the [quick start](../README.md#quick-start).

---

### Intent routing
**Primitive:** Choice · **Added:** 2026-09-28

Pick the customer's primary intent before any downstream branching happens. The canonical first question in a triage pipeline.

```python
"intent": Choice(
    instructions="What is the customer's main request?",
    criteria={
        "refund": "The customer wants money returned.",
        "technical_help": "The customer needs a bug or integration fixed.",
        "information": "The customer is asking for information only.",
        "other": "None of the other options clearly fits.",
    },
),
```

**Wiring & thresholds**
- Route on `answers["intent"].choice`; send to `other` or a human when `probabilities["other"]` is the top or `confidence` is below your routing floor.
- Keep option descriptions mutually exclusive — overlapping descriptions push probability mass onto `other`.

**Failure modes**
- Mixed-intent tickets get forced into one bucket; split into parallel atomic questions instead of one mega-question.
- Option creep: every new intent added "just this once" degrades calibration of the whole set.

**Sources:** [Quick-start example](https://github.com/Anil-matcha/awesome-jev-by-typesafe) · [Docs — patterns](https://docs.typesafe.ai/patterns)

---

### Tool selection for agents
**Primitive:** Choice · **Added:** 2026-09-28

Before an agent loop expands its tool list, let Jev pick the one tool (or none) that matches the current step. Cuts tool-result noise and token spend in coding harnesses.

```python
"tool": Choice(
    instructions="Which tool should handle the current step?",
    criteria={
        "search": "The step needs code/text search over the workspace.",
        "edit": "The step is a concrete file edit with a known target.",
        "run": "The step needs a command or test execution.",
        "none": "No tool is needed; the model should answer directly.",
    },
),
```

**Wiring & thresholds**
- Gate execution on `confidence`; on low confidence, fall back to showing the agent the full tool list.
- `none` prevents forced tool calls on conversational turns — the single most common fix reported in community harness repos.

**Failure modes**
- Descriptions written for humans, not for matching against raw tool output; include the tool's trigger conditions, not its implementation.

**Sources:** [TypeSafeAI/jev-harness](https://github.com/TypeSafeAI/jev-harness) · [Docs — agent skill](https://docs.typesafe.ai/agent-skill)

---

### Model routing
**Primitive:** Choice · **Added:** 2026-09-28

Choose which downstream LLM (tier/effort) should serve a turn. Jev stays in the hot path because it returns in ~70–500 ms, far under a System Two model's first token.

```python
"route": Choice(
    instructions="Which model tier should answer this turn?",
    criteria={
        "fast": "Simple, low-risk, mostly mechanical request.",
        "standard": "Normal complexity; no safety or correctness stakes.",
        "premium": "Complex reasoning, high stakes, or a failed earlier attempt.",
    },
),
```

**Wiring & thresholds**
- Combine with a Noul escalation question (see [Noul patterns](noul-patterns.md)) so "premium" has two independent votes before you pay for it.
- Log the routed tier next to the returned model version to audit drift.

**Failure modes**
- Routing on politeness/formatting cues instead of task complexity — describe what "complex" means in the criteria, with examples.

**Sources:** [JoacoMarc/jev-harness-router](https://github.com/JoacoMarc/jev-harness-router) · [Docs — use-case map](https://docs.typesafe.ai/concepts/use-case-map)

---

### Best-of-N selection
**Primitive:** Choice · **Added:** 2026-09-28

You generated N drafts (replies, summaries, commit messages) with an LLM; Jev picks the best one against stated criteria — cheaply enough to run per request.

```python
"best": Choice(
    instructions="Which draft best answers the user, factually and in tone?",
    criteria={
        "draft_1": "Draft 1.",  # put each draft's text in state, key it here
        "draft_2": "Draft 2.",
        "draft_3": "Draft 3.",
        "reject_all": "No draft is acceptable; regenerate.",
    },
),
```

**Wiring & thresholds**
- Pass the drafts in `state` (e.g. `state={"drafts": [...]}`) and keep criteria as stable references, so the question text stays identical across calls.
- `reject_all` above some floor (e.g. top option probability < 0.5) triggers one regeneration, then hard-stops — don't loop forever.

**Failure modes**
- Position bias: rotate draft order between calls if you reuse the selection across batches.

**Sources:** [Docs — confidence](https://docs.typesafe.ai/confidence) · [Cookbook — parallel questions](https://docs.typesafe.ai/cookbooks/parallel_questions)

---

### Document type classification
**Primitive:** Choice · **Added:** 2026-09-28

Invoice vs. receipt vs. contract vs. junk — the entry question of every document pipeline, and the classic "smart if-statement".

```python
"doc_type": Choice(
    instructions="What kind of document is this?",
    criteria={
        "invoice": "Requests payment; has line items and totals.",
        "receipt": "Confirms a completed payment.",
        "contract": "Defines obligations between parties.",
        "correspondence": "A letter or email, no payment or obligations.",
        "unknown": "Not clearly any of the above.",
    },
),
```

**Wiring & thresholds**
- For taxonomies deeper than ~15 labels, classify hierarchically (coarse group → fine type) rather than one flat 255-option question.
- Feed extracted text, not scans — Jev is text-only.

**Failure modes**
- Jev is weak at math, counting, and dates; classify on structure and wording, never on "the total looks bigger than…".

**Sources:** [Cookbook — hierarchical classification](https://docs.typesafe.ai/cookbooks/hierarchical_classification) · [Docs — primitives](https://docs.typesafe.ai/primitives)

---

### Skill / expert routing
**Primitive:** Choice · **Added:** 2026-09-28

Route a user turn to the matching agent skill or expert package before loading prompts — the Jev-native replacement for keyword-based skill triggers.

```python
"skill": Choice(
    instructions="Which skill should handle this request?",
    criteria={
        "data_analysis": "Needs dataset inspection, charts, or computation.",
        "writing": "Drafting or rewriting user-facing prose.",
        "ops": "Deploy, restart, or infrastructure operations.",
        "none": "General conversation; no skill applies.",
    },
),
```

**Wiring & thresholds**
- Keep skill descriptions aligned with when the skill *should fire*, not what it contains; drift between description and behavior shows up as misroutes.
- `none` should win the tie, not lose it — check `probabilities` ordering, not just the argmax.

**Failure modes**
- Two skills with near-identical triggers split probability and stall; merge or add disambiguating criteria.

**Sources:** [typesafe-ai/skills](https://github.com/typesafe-ai/skills) · [Docs — agent skill](https://docs.typesafe.ai/agent-skill)
