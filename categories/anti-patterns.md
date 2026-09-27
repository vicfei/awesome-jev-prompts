# Anti-patterns — how Jev questions go wrong

The fastest way to lose trust in Jev is a badly designed question. These are the recurring failure modes, with the fix for each. Every one of them has been observed in public projects or called out in official docs.

---

### 1. Asking Jev to compute
**Added:** 2026-09-28

Jev is weak at math, counting, and dates — it's a judgment model, not a calculator.

- ❌ `Noul("Is the invoice total larger than the sum of the line items?")`
- ✅ Sum the line items in code; ask `Noul("Do the stated totals match the line items?")` only if you must, and verify arithmetic yourself.

**Rule:** arithmetic, counting, and date math stay in code; Jev judges what the numbers *mean*.

**Sources:** [walidboulanouar/awesome-jev-use-cases (Jev 1.13 limits)](https://github.com/walidboulanouar/awesome-jev-use-cases) · [Docs — primitives](https://docs.typesafe.ai/primitives)

---

### 2. Open-ended "Choice" with unbounded options
**Added:** 2026-09-28

Choice needs a finite, enumerable option set (cardinality capped at 255; bigger sets silently fall back to a slower two-stage path). "Pick the best title" is a job for a System Two model, then a Jev best-of-N.

**Sources:** [Launch post](https://typesafe.ai/blog/introducing-system-one-models-and-jev) · [Cookbook — hierarchical classification](https://docs.typesafe.ai/cookbooks/hierarchical_classification)

---

### 3. No escape option
**Added:** 2026-09-28

Every Choice whose option list might be incomplete needs an `other` / `none_of_the_above` / `review` option. Without it, Jev is forced to misclassify the misfits — and your logs will look cleaner while being wrong.

**Sources:** [Anil-matcha/awesome-jev-by-typesafe (design rules)](https://github.com/Anil-matcha/awesome-jev-by-typesafe) · [Docs — patterns](https://docs.typesafe.ai/patterns)

---

### 4. Score with an unordered rubric
**Added:** 2026-09-28

Score's `criteria` must be a **strictly ordered** list of levels (probability-weighted; answers can land between levels). An unordered set ("red", "blue", "green") is a Choice question wearing a Score costume — results are meaningless because "between levels" has no direction.

**Sources:** [Docs — primitives](https://docs.typesafe.ai/primitives)

---

### 5. Reading Noul 0.5 as "medium"
**Added:** 2026-09-28

Noul returns the probability a statement is true. **0.5 is uncertainty, not a medium score.** Don't build a three-way split at 0.33/0.66 like it's a rating; build acceptance and escalation bands (e.g. ≥ 0.8 act, ≤ 0.4 pass, between → explicit uncertain branch).

**Sources:** [Anil-matcha/awesome-jev-by-typesafe (design rules)](https://github.com/Anil-matcha/awesome-jev-by-typesafe) · [Docs — confidence](https://docs.typesafe.ai/confidence)

---

### 6. One global threshold everywhere
**Added:** 2026-09-28

There is no blessed 0.7. Thresholds are per action and per risk level — a moderation block and a "nice to have" flag do not share a cutoff. Tune each from logged probability distributions (see [Calibration & eval](calibration-and-eval.md)).

**Sources:** [Anil-matcha/awesome-jev-by-typesafe (design rules)](https://github.com/Anil-matcha/awesome-jev-by-typesafe) · [Cookbook — classification using confidence](https://docs.typesafe.ai/cookbooks/classification_using_confidence)

---

### 7. Trusting `jev-latest` on threshold-sensitive paths
**Added:** 2026-09-28

Aliases move (`jev-latest`, `jev-preview` both resolve to versioned releases that can change under you). If your thresholds depend on model behavior, pin a versioned ID (`jev-1.13.0`) and **log the version actually returned**, not the alias you asked for.

**Sources:** [Anil-matcha/awesome-jev-by-typesafe (design rules)](https://github.com/Anil-matcha/awesome-jev-by-typesafe) · [Docs — models](https://docs.typesafe.ai/models)

---

### 8. Ignoring probabilities that disagree with the argmax
**Added:** 2026-09-28

`choice` is the top of the distribution; `probabilities` is the distribution. If the top two options sit at 0.45 / 0.42, the "decision" is a coin flip — branch to review, don't ship it. Confidence gates exist precisely for this.

**Sources:** [Docs — confidence](https://docs.typesafe.ai/confidence) · [Cookbook — classification using confidence](https://docs.typesafe.ai/cookbooks/classification_using_confidence)

---

### 9. Letting the question own composition or side effects
**Added:** 2026-09-28

The core rule: **questions describe judgments; code owns composition, thresholds, and side effects.** "Which folder, what priority, and should we email the manager?" crammed into one question is three judgments plus an action — split the judgments, keep the action in code.

**Sources:** [Anil-matcha/awesome-jev-by-typesafe (design rules)](https://github.com/Anil-matcha/awesome-jev-by-typesafe) · [Docs — patterns](https://docs.typesafe.ai/patterns)

---

### 10. Using Jev for authorization or as a substitute for review
**Added:** 2026-09-28

Jev is not an authorization system, an input validator, or a human reviewer. It can *route* a request toward a permission check; it must not *be* the permission check. Calibration describes groups, not individual answers — no individual output deserves blind trust.

**Sources:** [Anil-matcha/awesome-jev-by-typesafe ("What Jev is not")](https://github.com/Anil-matcha/awesome-jev-by-typesafe) · [Docs — confidence](https://docs.typesafe.ai/confidence)
