# Structured-state patterns — when your state is a table, not text

Decision models (Jev, Clef, StartLux) read natural-language state. Tabular foundation models (TabPFN, LimiX, TabFM) read a training table as context. The contract is the same — state + question → calibrated probability, one forward pass — but the state shape differs. These patterns cover the boundary: when to route to which paradigm, and how to design questions when your evidence lives in columns, not sentences.

All entries here are **derived practice** — reasoned from the documented behavior of both paradigms and our own measurements, unless a community source is linked.

---

### Column semantics in state
**Primitive:** Composite (state design) · **Added:** 2026-10-28 · **Status:** derived

When structured data feeds a decision model, the column names and units go into `state` as a labeled block — the model needs to know what `account_balance_usd = 450` means, not just the number.

```python
state = {
    "customer_profile": {
        "account_age_days": 320,
        "balance_usd": 450,
        "overdraft_count_90d": 3,
        "credit_score": 680,
    },
    "request": "Customer asks for a credit limit increase to $5000.",
}
# Question: Noul("Should this request be approved without manual review?")
```

**Wiring & thresholds**
- Name columns with units and time windows (`overdraft_count_90d`, not `od_cnt`) — the model reads names literally.
- Put the action context (what the decision triggers) in a separate state field, not mixed into the column block.

**Failure modes**
- Bare numeric arrays with no column names: the model pattern-matches positionally, which breaks when column order changes.

---

### Tabular FM as the cheap gate
**Primitive:** Composite (routing) · **Added:** 2026-10-28 · **Status:** derived

When your state is mostly structured (numeric/categorical columns) and the task is classification or regression on rows, a tabular foundation model is cheaper and often better than routing through a text-based decision model. Use the decision model only when the judgment requires reading prose.

```python
# Route by state shape, not by habit:
if state_is_mostly_tabular(rows) and task in ("classification", "regression"):
    score = tabular_fm.predict(training_rows, query_row)     # TabPFN / LimiX
else:
    answer = jev.ask(state, questions)                        # Jev / Clef / StartLux
```

**Wiring & thresholds**
- Tabular FMs shine at small data (hundreds to ~10K rows as context); beyond that, classic gradient boosting trained on the full table wins.
- Both paradigms return calibrated probabilities — threshold discipline transfers, but re-fit per model (see [Calibration & eval](calibration-and-eval.md)).

**Failure modes**
- Feeding a tabular FM a task that requires reading prose (a support ticket, a legal clause) — it has no text-understanding pathway.

---

### Cross-paradigm calibration
**Primitive:** Score (comparison) · **Added:** 2026-10-28 · **Status:** derived

When both a tabular FM and a decision model produce probabilities on the same task, calibrate them on a shared held-out set before comparing — raw probabilities from different model families are not on the same scale. Use a proper scoring rule (Brier, log loss) as the common metric.

**Wiring & thresholds**
- Fit a temperature (or isotonic regression) for each model on the same calibration split.
- Compare post-calibration probabilities, not raw outputs — a 0.7 from TabPFN and a 0.7 from Jev may mean different things pre-calibration.

**Failure modes**
- Comparing AUC without calibration: ranking quality and absolute probability quality are different properties (see the [minimind-jev benchmark](https://github.com/vicfei/jev-rag-zh-benchmark) for a measured example of AUC/nDCG divergence).
