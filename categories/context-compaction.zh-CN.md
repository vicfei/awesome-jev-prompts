# 上下文压缩——决定窗口里留什么

> 中文译本，以[英文版](context-compaction.md)为准（同步于 2026-10-08）。

Agent 的上下文窗口塞满了没人再读的工具结果和历史。Jev 以毫秒级速度逐条决定 保留/丢弃/摘要；窗口与回执归代码。这是当前社区最活跃的子类——下面几个 harness 插件做的就是这条循环。

模板使用 Python SDK（`python -m pip install typesafe-sdk`）。

---

### 消息的保留或丢弃
**Primitive:** Score · **Added:** 2026-09-28

压缩之前，给每条旧消息/工具结果打"未来价值"分；低于下限丢弃，高于保留。

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

**接线与阈值**
- 任务陈述和最近 N 轮永远在代码里强制保留——Score 只给中间历史排序，不碰受保护的头部和尾部。
- `keep < 1.0` 丢弃、1.0–2.0 摘要（用 LLM——Jev 不会写字）、≥ 2.0 保留。

**失效模式**
- 丢掉唯一提到约束的消息（"用 staging 库"）——"critical"要说清*为什么*关键，且受保护轮次要设不可跨越的下限。

**来源：** [wjw66/deepseek-harness-jev-pre-compaction](https://github.com/wjw66/deepseek-harness-jev-pre-compaction) · [yangyu666/dsh-jev-prune](https://github.com/yangyu666/dsh-jev-prune)

---

### 摘要或原文
**Primitive:** Choice · **Added:** 2026-09-28

压缩后幸存的条目：压缩成摘要，还是因精确性而逐字保留？

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

**接线与阈值**
- 实际摘要（System Two 调用）与回执归代码——Jev 只选处理方式。
- 日志里 `verbatim` 占比持续走高 = 你的摘要正在丢失用户反复需要的东西。

**失效模式**
- 把 API 响应当"可摘要"——精确字段值会在摘要中被抹掉，然后 agent 循环重查；错误负载默认逐字保留。

**来源：** [yangyu666/dsh-jev-prune（回执压缩）](https://github.com/yangyu666/dsh-jev-prune) · [官方文档 — state](https://docs.typesafe.ai/concepts/state)

---

### 工具结果裁剪
**Primitive:** Noul + Score · **Added:** 2026-09-28

结果进入上下文之前先问：这次调用成功了吗？输出值不值这些 token？agent 多工具循环的前置过滤器。

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

**接线与阈值**
- `succeeded < 0.5`（替换为一行错误回执）或 `value < 1.0` 时裁剪；保留回执让模型知道调用发生过。
- 每次工具调用都跑、跟上 agent 速度——这是 Doom bot 每秒 10 次调用那档延迟，不是批量分析。

**失效模式**
- 把失败整个裁掉：agent 没看到失败就会原样重试。失败以回执形式保留，只裁负载。

**来源：** [Astro-Han/jev-harness（工具结果过滤）](https://github.com/Astro-Han/jev-harness) · [TypeSafeAI/jev-harness](https://github.com/TypeSafeAI/jev-harness)
