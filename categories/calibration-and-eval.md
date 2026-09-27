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

Jev is the fast, cheap judgment layer — not the last resort and not the whole brain. The healthy architecture is bicameral: reflexes (classify, route, gate) on Jev; deliberate reasoning (plan, draft, explain) on an LLM; handoffs triggered by Jev's own confidence signals. The official coding harness and several community harnesses are built exactly this way.

**Sources:** [TypeSafeAI/jev-harness ("the model proposes, Jev supplies evidence, code decides")](https://github.com/TypeSafeAI/jev-harness) · [AbdelStark/bicameral](https://github.com/AbdelStark/bicameral) · [Launch post](https://typesafe.ai/blog/introducing-system-one-models-and-jev)
