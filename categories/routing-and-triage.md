# Routing & triage — sorting streams of unstructured input

Composite pipelines: one Jev request carries several atomic questions (they are evaluated independently), and code composes the outcome. The launch post's "smart if-statement" territory — classify, route, score, branch.

Templates use the Python SDK (`python -m pip install typesafe-sdk`).

---

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

**Sources:** [Cookbook — classifying RAG passages](https://docs.typesafe.ai/cookbooks/classifying_rag_passages) · [Cookbook — rerank](https://docs.typesafe.ai/cookbooks/rerank_typesafe)

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
