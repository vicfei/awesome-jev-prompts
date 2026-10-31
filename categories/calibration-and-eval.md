# Calibration & eval — making thresholds trustworthy

The gap between "it returns a number" and "the number means something". Patterns here are process patterns: how to pick thresholds, keep them honest, and know when to hand off to a System Two model.

---

### Two-band thresholds from logged distributions
**Added:** 2026-09-28

Don't guess a cutoff. Run the question over a few hundred logged real cases, plot the answer distribution per ground-truth bucket, and place an **action band** and an **escalation band** where the populations actually separate.

- Record the full response (answer, probabilities, confidence, returned model version) on every call — it doubles as your eval dataset.
- Re-fit bands when the distribution shifts; drift is the signal to re-tune, not to distrust the model wholesale.

**Sources:** [Cookbook — classification using confidence](https://docs.typesafe.ai/cookbooks/classification_using_confidence) · [Docs — confidence](https://docs.typesafe.ai/confidence)

---

### Versioned questions, pinned models
**Added:** 2026-09-28

Treat question text like a schema: once a threshold depends on it, freeze it, give it an ID, and change it deliberately. Same for the model: pin `jev-1.13.0` and log the returned version per call. "It worked last week" should be answerable from your logs.

**Sources:** [Docs — models](https://docs.typesafe.ai/models) · [Anil-matcha/awesome-jev-by-typesafe (design rules)](https://github.com/Anil-matcha/awesome-jev-by-typesafe)

---

### Consistency checks for high-stakes answers
**Added:** 2026-09-28

Ask the same judgment twice with different phrasings (or a Choice and a Noul encoding the same question). Agreeing answers with different framings are far more reliable than a single high-confidence answer; disagreement is an automatic escalation.

**Sources:** [Cookbook — consistency (Noul)](https://docs.typesafe.ai/cookbooks/consistency_noul_cookbook) · [Cookbook — consistency (Choice)](https://docs.typesafe.ai/cookbooks/consistency_choice_cookbook)

---

### Shadow mode before cutover
**Added:** 2026-09-28

Run the Jev decision alongside the existing rule-based or LLM-based decision, log disagreement rate and would-have-been-wrong rate, and cut over only when the numbers clear your bar. Community harnesses ship this as a first-class feature.

**Sources:** [AntonioCoppe/jev-harness (shadow mode)](https://github.com/AntonioCoppe/jev-harness) · [kenhuangus/jev-usecases (confidence-gated logic)](https://github.com/kenhuangus/jev-usecases)

---

### Knowing when to escalate to System Two
**Added:** 2026-09-28

Jev is the fast, cheap judgment layer — not the last resort and not the whole brain. The healthy architecture is bicameral: reflexes (classify, route, gate) on Jev; deliberate reasoning (plan, draft, explain) on an LLM; handoffs triggered by Jev's own confidence signals. The TypeSafeAI community harness and several other harnesses are built exactly this way.

**Sources:** [TypeSafeAI/jev-harness ("the model proposes, Jev supplies evidence, code decides")](https://github.com/TypeSafeAI/jev-harness) · [AbdelStark/bicameral](https://github.com/AbdelStark/bicameral) · [Launch post](https://typesafe.ai/blog/introducing-system-one-models-and-jev)


---

### Measured reference points (2026-10-22 to 2026-10-29)
**Primitive:** Composite (reference) · **Added:** 2026-11-01 · **Status:** measured

Published measurements from the [jev-rag-zh-benchmark](https://github.com/vicfei/jev-rag-zh-benchmark) and the [minimind-jev](https://github.com/vicfei/minimind-jev) training arc, useful as calibration anchors:

- **Ranking ≠ calibration**: on the same 100-query Chinese reranking sample, a model can have higher separation AUC but lower nDCG (minimind-jev v0.3-lite: AUC 0.647 > v0.1's 0.630, but nDCG@5 0.440 < 0.488). Ranking rewards placing the single positive high; AUC rewards pairwise ordering across all candidates. Different questions, different metrics.
- **Binary threshold pathology**: Deußer et al. ([arXiv:2609.37647](https://arxiv.org/abs/2609.37647)) report Jev's binary probabilities sit poorly against a fixed 0.5 cutoff — tuned thresholds lift UNFAIR-ToS micro-F1 from 0.50 to 0.75. This is the published version of the pattern this category has always taught: fit thresholds on your own logged distribution, not on a universal default.
- **Temperature-scaled calibration is cheap and underused**: a single-parameter fit on a held-out split (LBFGS, seconds) measurably improves probability quality without touching ranking. Reference implementations in [minimind-jev scripts](https://github.com/vicfei/minimind-jev/blob/main/scripts/train.py).
- **StartLux-27B noul separation AUC 0.727** on the same sample — the highest measured on that benchmark, ahead of hosted Jev 1.13 (0.718). Open weights now match or exceed hosted models on calibration-sensitive metrics.

**Sources:** [jev-rag-zh-benchmark results](https://github.com/vicfei/jev-rag-zh-benchmark/blob/main/results/s1-startlux_report.md) · [Deußer et al.](https://arxiv.org/abs/2609.37647) · [minimind-jev DISTILLATION-NOTES](https://github.com/vicfei/minimind-jev/blob/main/docs/DISTILLATION-NOTES.md)
