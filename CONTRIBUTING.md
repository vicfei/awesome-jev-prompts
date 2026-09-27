# Contributing

Thanks for helping make Jev question design better. **Corrections take priority over additions — a wrong row costs more than a missing one.**

## What we accept

- **Patterns** — a reusable question template for a real decision (Choice / Score / Noul or a small composite).
- **Anti-patterns** — a failure mode you actually hit, with the fix.
- **Calibration & eval practices** — threshold-fitting, versioning, shadow-mode, handoff rules.
- **Corrections** — broken links, outdated facts, wrong guidance. These always jump the queue.

## Entry format (mandatory)

```markdown
### Pattern name
**Primitive:** Choice | Score | Noul | Composite · **Added:** YYYY-MM-DD

One or two sentences: what decision this makes and where it fits.

```python
# runnable question template (Python SDK; TS optional)
```

**Wiring & thresholds**
- How to act on the answer: bands, floors, fallbacks.

**Failure modes**
- What goes wrong in practice, and how to detect it.

**Sources:** [label](url) · [label](url)
```

## Quality bar

1. **Question template is copy-pasteable** — real SDK shape (`Choice/Score/Noul` from `typesafe_sdk` or `@typesafe-ai/sdk`), not pseudocode.
2. **Every claim has a source** — official docs, the launch post, or a public repo/article. If it's your own hard-won lesson, say so ("observed in production by the author") instead of faking a citation.
3. **Atomic judgment only** — composition, thresholds, and side effects belong to code; if your question does three things, split it (that's probably an anti-pattern entry too).
4. **Failure modes are honest** — an entry with no known failure mode usually means it hasn't been used.
5. **Variable content goes in `state`**, not in the question text — thresholds depend on question stability.
6. No affiliate links, no SEO-spam, no "my product" entries unless the pattern genuinely stands alone.

## Process

- One pattern per PR. Small diffs get reviewed fast.
- Open an issue with the [submission template](.github/ISSUE_TEMPLATE/submit-pattern.yml) first if you want to sound out an idea.
- Link check runs weekly in CI; dead links are issues, not deletions — find the replacement.

## Style

- English entries; keep wording tight. Code comments only where a constraint isn't obvious.
- Don't reformat existing entries you're not editing.
- Dates in `Added:` use ISO format and are never rewritten.
