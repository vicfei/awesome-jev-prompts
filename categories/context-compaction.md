# Context compaction — deciding what stays in the window

Agent context windows fill with tool results and history nobody will read again. Jev decides keep/drop/summarize per item in milliseconds; the window and receipts stay in code. This is the most active sub-genre in the community right now — several harness plugins below ship exactly this loop.

Templates use the Python SDK (`python -m pip install typesafe-sdk`).

---

### Keep-or-drop for messages
**Primitive:** Score · **Added:** 2026-09-28

Before compaction, score each old message/tool result for future value; drop below a floor, keep above.

```python
"keep": Score(
    instructions="How much will this conversation item matter for the remaining task?",
    criteria=[
        "Noise: greeting, boilerplate, spent tool output.",
        "Maybe: context that could matter.",
        "Likely: decisions and constraints already established.",
        "Critical: the task goal, key facts, or blocking state.",
    ],
),
# state = {"task": ..., "item": ...}
```

**Wiring & thresholds**
- Always force-keep the task statement and last N turns in code — the Score ranks the middle history, not the protected head/tail.
- Drop `keep < 1.0`, summarize 1.0–2.0 (with an LLM — Jev can't write), keep ≥ 2.0.

**Failure modes**
- Dropping the only message that named a constraint ("use the staging DB") — "critical" needs to say *why* it's critical, and protected turns need a floor you never cross.

**Sources:** [wjw66/deepseek-harness-jev-pre-compaction](https://github.com/wjw66/deepseek-harness-jev-pre-compaction) · [yangyu666/dsh-jev-prune](https://github.com/yangyu666/dsh-jev-prune)

---

### Summarize-or-quote
**Primitive:** Choice · **Added:** 2026-09-28**

For items surviving compaction: compress to a summary, or keep verbatim because precision will matter later?

```python
"treatment": Choice(
    instructions="How should this item be carried forward in the context?",
    criteria={
        "verbatim": "Exact wording matters: IDs, numbers, code, quotes.",
        "summary": "Gist suffices; details are recoverable from the log.",
        "drop": "No future value.",
    },
),
```

**Wiring & thresholds**
- Code owns the actual summarization (a System Two call) and the receipts — Jev only picks the treatment.
- `verbatim` share trending up in logs = your summaries are losing something users keep needing.

**Failure modes**
- Treating API responses as "summary-safe" — exact field values get rounded out of summaries and agents then re-query in a loop; error payloads are verbatim by default.

**Sources:** [yangyu666/dsh-jev-prune (receipt compaction)](https://github.com/yangyu666/dsh-jev-prune) · [Docs — concepts](https://docs.typesafe.ai/concepts/state)

---

### Tool-result pruning
**Primitive:** Noul + Score · **Added:** 2026-09-28**

Before results even enter the context: did this call succeed, and is its output worth the tokens? A pre-filter for agent loops that fire many tools.

```python
"succeeded": Noul(
    instructions="Did this tool call achieve its purpose based on the result?",
),
"value": Score(
    instructions="How useful is this tool output for the next step?",
    criteria=[
        "Dead weight: empty, redundant, or already-known.",
        "Low: marginally useful.",
        "Useful: informs the next step.",
        "Essential: the next step depends on it.",
    ],
),
# state = {"intent": ..., "result": ...}
```

**Wiring & thresholds**
- Prune when `succeeded < 0.5` (replace with a one-line error receipt) or `value < 1.0`; keep receipts so the model knows a call happened.
- Runs per tool call at agent speed — this is the 10-queries-per-second Doom-bot latency class, not batch analytics.

**Failure modes**
- Pruning failures entirely: the agent retries the same call because it never saw it fail. Failed calls stay as receipts; only their payloads go.

**Sources:** [Astro-Han/jev-harness (tool-result filtering)](https://github.com/Astro-Han/jev-harness) · [TypeSafeAI/jev-harness](https://github.com/TypeSafeAI/jev-harness)
