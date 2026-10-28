# Score 模式——有序评分判断

> 中文译本，以[英文版](score-patterns.md)为准（同步于 2026-10-08）。

Score 接收 `instructions` + 作为**有序列表**的 `criteria`，定义每一级评分等级。答案是概率加权的 `score`（可以落在两级之间），另有 `legend`、`probabilities`、`confidence`。如果你的等级不能按强度或质量严格排序，你要的是 [Choice](choice-patterns.zh-CN.md)，不是 Score。

模板使用 Python SDK（`python -m pip install typesafe-sdk`）。

---

### 严重度评分
**Primitive:** Score · **Added:** 2026-09-28

这事有多糟？支持和运维流水线中复用率最高的一把评分尺。

```python
"severity": Score(
    instructions="How severe is this incident report?",
    criteria=[
        "Cosmetic or informational; no functional impact.",
        "Minor impairment; workaround exists.",
        "Major feature broken for some users.",
        "Outage or data loss; urgent response required.",
    ],
),
```

**接线与阈值**
- 把返回的 `score` 当作 `legend` 的索引（0 起）；把分数带映射到 SLA 由代码完成——例如 score ≥ 2.5 呼叫值班、≥ 1.5 高优先级。
- 评分等级要写成评审者可以盲排的完整句子——简写标签（"S1"…"S4"）训练不出任何东西。

**失效模式**
- 间距不均：若 2→3 的跨度远大于 1→2，分数会堆积在平缓区。拆分或改写。

**来源：** [快速上手示例](https://github.com/Anil-matcha/awesome-jev-by-typesafe) · [官方文档 — patterns](https://docs.typesafe.ai/patterns)

---

### 质量门禁
**Primitive:** Score · **Added:** 2026-09-28

对生成产物（代码、文案、结构化输出）在触达用户或合并之前给出 驳回/修复/通过 的裁定。

```python
"quality": Score(
    instructions="Rate this generated patch against the task requirements.",
    criteria=[
        "Wrong: does not address the task.",
        "Partial: addresses the task but with clear defects.",
        "Acceptable: meets requirements with minor issues.",
        "Excellent: meets requirements and is robust.",
    ],
),
```

**接线与阈值**
- 按区间设闸而非单点：< 1.5 驳回、1.5–2.5 一轮修复、≥ 2.5 放行。"schema 合法 ≠ 决策正确"——门禁评判内容，schema 只评判形状。
- 搭配一个"是否违反任何既定约束？"的 Noul 问题作为第二票。

**失效模式**
- 评分尺漂移：悄悄改写某一级会改变所有下游阈值——像代码一样给评分尺做版本管理。

**来源：** [官方文档 — confidence](https://docs.typesafe.ai/confidence) · [Cookbook — llm guardrails](https://docs.typesafe.ai/cookbooks/llm_guardrails)

---

### 内容审核评分
**Primitive:** Score · **Added:** 2026-09-28

在展示之前，对用户或模型生成的内容按审核政策打分——一次 70–500ms 的调用，够实时 UX 用。

```python
"moderation": Score(
    instructions="How much does this content violate the stated policy?",
    criteria=[
        "No policy concern.",
        "Borderline; context could make it fine.",
        "Clearly against policy.",
        "Severe: harassment, hate, or illegal content.",
    ],
),
```

**接线与阈值**
- 把政策正文放进 `state`（如 `state={"policy": ...}`），调政策不动问题。
- 只在最高区间自动拦截；中间区间走人工复审而非删除——审核误伤的代价高于复审延迟。

**失效模式**
- 把政策写进问题、把示例写进问题——阈值依赖问题文本稳定，一切可变内容都应该在 `state` 里。

**来源：** [发布文章 — guardrails](https://typesafe.ai/blog/introducing-system-one-models-and-jev) · [官方文档 — state](https://docs.typesafe.ai/concepts/state)

---

### 相关性评分（RAG）
**Primitive:** Score · **Added:** 2026-09-28

检索到的段落进入提示词之前先评分——比用聊天模型重排便宜，且返回校准的等级。

```python
"relevance": Score(
    instructions="How well does this passage answer the question?",
    criteria=[
        "Irrelevant or off-topic.",
        "Topically related but doesn't answer it.",
        "Partially answers the question.",
        "Directly and completely answers it.",
    ],
),
```

**接线与阈值**
- 每个段落一次请求（并行问题共享上下文限制）；扇出后取 score ≥ 2.5 进提示词并按分数排序。
- 记录每次检索的分数；均值漂移就是语料或查询变化的信号。

**失效模式**
- 段落含关键词但说的是另一个实体（"得州的巴黎" vs "法国的巴黎"）——旁边加一个实体匹配 Noul。

**来源：** [Cookbook — classifying RAG passages](https://docs.typesafe.ai/cookbooks/classifying_rag_passages) · [Cookbook — rerank](https://docs.typesafe.ai/cookbooks/rerank_typesafe) · 社区实践：[hotchpotch/jev-reranker](https://github.com/hotchpotch/jev-reranker)、[WiktorB2004/llama-index-jev](https://github.com/WiktorB2004/llama-index-jev)

---

### 队列优先级评分
**Primitive:** Score · **Added:** 2026-09-28

把非结构化请求变成有序的队列编号，调度器不再对一切先来后到。

```python
"priority": Score(
    instructions="How soon does this request genuinely need action?",
    criteria=[
        "Whenever; no deadline.",
        "This week is fine.",
        "Today; blocked on us.",
        "Now; someone is waiting live.",
    ],
),
```

**接线与阈值**
- Score 只判*紧迫感*，排序归代码——在调度器里把 `score` 与 SLA 时钟、客户档位组合，遵守元规则。
- 状态变化时（客户回复提升了工单）重新评分，不要永久缓存。

**失效模式**
- 评分等级掺入业务规则（"VIP 永远 3 分"）——档位归代码，问题只判人的紧迫程度。

**来源：** [官方文档 — patterns](https://docs.typesafe.ai/patterns) · [官方文档 — use-case map](https://docs.typesafe.ai/concepts/use-case-map)
---

### 研报确信度评分
**原语：** Score · **收录：** 2026-10-28 · **状态：** derived

给一条证据（研报、电话会、新闻事件）对某个特定投资论点的支持力度评级。评分尺把"来源可信"和"证据支持论点"分成两个判断——传统研报摘要把这两者混在一起。

```python
"conviction": Score(
    instructions="How strongly does this evidence support the stated investment thesis?",
    criteria=[
        "Contradicts: the evidence actively undermines the thesis.",
        "Neutral: the evidence is relevant but does not move the thesis either way.",
        "Supports: the evidence is consistent with and mildly supportive of the thesis.",
        "Confirms: the evidence directly validates the core mechanism of the thesis.",
    ])
```

**接线与阈值**
- state 携带三个标签字段：论点（一句话，读证据**之前**写好）、证据摘要、来源可信度 Noul——分开的判断，一次请求。
- 仓位可以按确信度级别操作：低于"supports"不动手，"supports"建仓，"confirms"加仓。
- 评分尺是相对于论点的，不相对于来源——一个高度可信的来源说了不相关的话也只评"neutral"。

**失败模式**
- 把来源可信度混进确信度评分：可信来源说了不相关的话应评"neutral"不是"confirms"——保持两个独立问题。
- 论点漂移：如果读完证据后改论点（去迎合证据），评分无意义——先写论点、冻结、再问。

**来源：** 推导自 ai-hedge-fund 投资人 Agent 模式（[virattt/ai-hedge-fund](https://github.com/virattt/ai-hedge-fund)，64k★）
