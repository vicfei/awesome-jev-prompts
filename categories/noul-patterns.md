# Noul patterns — probabilistic truth checks

Noul takes `instructions` only and returns a number from 0 to 1. Read it as "probability the statement is true", never as a rating: **0.5 means uncertainty, not a medium score.** Act through two thresholds (an acceptance band and an escalation band), not one.

Templates use the Python SDK (`python -m pip install typesafe-sdk`).

---

### Policy violation check
**Primitive:** Noul · **Added:** 2026-09-28

Does this input violate a stated rule? The base guardrail question — jailbreak detection, banned content, off-policy tool calls.

```python
"violates": Noul(
    instructions="Does this message violate the stated usage policy?",
),
# state carries the message AND the policy text:
# state = {"message": ..., "policy": ...}
```

**Wiring & thresholds**
- Act on bands: ≥ 0.8 block, 0.4–0.8 review, < 0.4 pass. Tune from logged distributions (see [Calibration](calibration-and-eval.md)), don't inherit 0.5.
- Keep the policy in `state` so policy edits don't invalidate thresholds tied to the question.

**Failure modes**
- Negation blindness on long policies — phrase the instruction positively ("does it violate") and keep one policy per question; conflicting rules inside one policy blur the probability.

**Sources:** [Launch post — guardrails & jailbreak detection](https://typesafe.ai/blog/introducing-system-one-models-and-jev) · [Cookbook — llm guardrails](https://docs.typesafe.ai/cookbooks/llm_guardrails)

---

### Duplicate detection
**Primitive:** Noul · **Added:** 2026-09-28

Are these two items the same thing? Dedup tickets, products, contacts, or code fragments without embedding infrastructure.

```python
"duplicate": Noul(
    instructions="Do these two items refer to the same underlying entity?",
),
# state = {"item_a": ..., "item_b": ...}
```

**Wiring & thresholds**
- Use as a candidate filter: blocklist exact keys in code, Noul-verify the fuzzy shortlist — don't run it over O(n²) pairs.
- ≥ 0.75 merge, 0.35–0.75 flag for a human, below keep separate.

**Failure modes**
- "Same entity" vs "same topic" confusion — state explicitly which one you mean in `instructions`; projects about Paris aren't duplicates of each other.

**Sources:** [Cookbook — entity alignment](https://docs.typesafe.ai/cookbooks/entity_alignment) · [Docs — primitives](https://docs.typesafe.ai/primitives)

---

### Citation / entailment check
**Primitive:** Noul · **Added:** 2026-09-28

Does the passage actually support the claim? The cheapest hallucination gate for generated answers.

```python
"supported": Noul(
    instructions="Is the claim fully supported by the cited passage alone?",
),
# state = {"claim": ..., "passage": ...}
```

**Wiring & thresholds**
- Require ≥ 0.8 before showing a citation; 0.4–0.8 drop the citation and soften the sentence in code (don't rewrite with Jev — it can't write).
- "Alone" matters: without it, world knowledge leaks in and inflates the score.

**Failure modes**
- Multi-hop claims fail on single passages — decompose the claim into per-hop Noul questions and require all hops to pass.

**Sources:** [Cookbook — citation check](https://docs.typesafe.ai/cookbooks/citation_check) · [Docs — patterns](https://docs.typesafe.ai/patterns)

---

### Human escalation trigger
**Primitive:** Noul · **Added:** 2026-09-28

Should a person look at this? One question that turns low-confidence paths into an explicit branch instead of a silent wrong answer.

```python
"escalate": Noul(
    instructions="Does this situation need a human decision before we act?",
),
```

**Wiring & thresholds**
- Compose in code: escalate if `noul ≥ 0.6` **or** the paired Choice's top probability < your floor — two independent uncertainty signals.
- Every escalation is a labeled example for next month's threshold tuning; store the whole response, not just the number.

**Failure modes**
- Asking "is this important?" — importance isn't decidable; need-for-human-judgment is. Name the decision the human would make.

**Sources:** [Docs — confidence](https://docs.typesafe.ai/confidence) · [Cookbook — classification using confidence](https://docs.typesafe.ai/cookbooks/classification_using_confidence)

---

### Retry / skip control
**Primitive:** Noul · **Added:** 2026-09-28

Should we retry the failed LLM/tool call, or is the failure permanent? Saves budget and latency in agent loops.

```python
"retry": Noul(
    instructions="Is this failure likely to succeed on a plain retry?",
),
# state = {"task": ..., "error": ..., "attempts": 2}
```

**Wiring & thresholds**
- Retry only while `noul ≥ 0.6` AND `attempts < 3` — code owns the counter and the side effects, Jev owns only the judgment.
- Include the raw error text in state; "likely transient" vs "definitely a permission error" is exactly the typed call Jev is for.

**Failure modes**
- Using it to mask bugs: persistent 0.9-retry on the same error means your failure taxonomy is wrong, not that you need more retries.

**Sources:** [TypeSafeAI/jev-harness](https://github.com/TypeSafeAI/jev-harness) · [Docs — patterns](https://docs.typesafe.ai/patterns)
