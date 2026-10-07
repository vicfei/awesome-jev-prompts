# Noul 模式——概率化真值判断

> 中文译本，以[英文版](noul-patterns.md)为准（同步于 2026-10-08）。

Noul 只接收 `instructions`，返回 0 到 1 之间的数。把它读作"陈述为真的概率"，**永远不要**当评分读：**0.5 的含义是不确定，不是中等。** 行动要靠两个阈值（行动带 + 升级带），不是一个。

模板使用 Python SDK（`python -m pip install typesafe-sdk`）。

---

### 策略违规检查
**Primitive:** Noul · **Added:** 2026-09-28

这条输入是否违反既定规则？基础护栏问题——越狱检测、违禁内容、越权工具调用。

```python
"violates": Noul(
    instructions="Does this message violate the stated usage policy?",
),
# state 同时携带消息与政策文本：
# state = {"message": ..., "policy": ...}
```

**接线与阈值**
- 按区间行动：≥ 0.8 拦截、0.4–0.8 复审、< 0.4 放行。区间要从日志分布里调（见[校准与评估](calibration-and-eval.zh-CN.md)），不要继承 0.5。
- 政策放 `state`，改政策不会作废与问题绑定的阈值。

**失效模式**
- 长政策下的否定盲区——指令用肯定式（"是否违反"），一个问题只放一条政策；政策内部互相冲突会糊掉概率。

**来源：** [发布文章 — 护栏与越狱检测](https://typesafe.ai/blog/introducing-system-one-models-and-jev) · [Cookbook — llm guardrails](https://docs.typesafe.ai/cookbooks/llm_guardrails)

---

### 重复检测
**Primitive:** Noul · **Added:** 2026-09-28

这两个条目是同一个东西吗？工单、商品、联系人、代码片段的去重，无需向量基础设施。

```python
"duplicate": Noul(
    instructions="Do these two items refer to the same underlying entity?",
),
# state = {"item_a": ..., "item_b": ...}
```

**接线与阈值**
- 用作候选过滤器：精确键在代码里拉黑名单，模糊候选交给 Noul 复核——不要跑 O(n²) 全量对。
- ≥ 0.75 合并、0.35–0.75 标记人工、以下保留。

**失效模式**
- "同一实体"与"同一主题"的混淆——在 `instructions` 里写明是哪一种；关于巴黎的各项目互相不是重复。

**来源：** [Cookbook — entity alignment](https://docs.typesafe.ai/cookbooks/entity_alignment) · [官方文档 — primitives](https://docs.typesafe.ai/primitives)

---

### 引用 / 蕴含检查
**Primitive:** Noul · **Added:** 2026-09-28

这段文字真的支持这个论断吗？生成答案最便宜幻觉闸门。

```python
"supported": Noul(
    instructions="Is the claim fully supported by the cited passage alone?",
),
# state = {"claim": ..., "passage": ...}
```

**接线与阈值**
- ≥ 0.8 才展示引用；0.4–0.8 撤引用并在代码里软化措辞（不要让 Jev 改写——它不会写字）。
- "alone"（仅凭此段）很关键：没有它，世界知识会渗入并抬高分数。

**失效模式**
- 多跳论断在单段落上必败——把论断拆成逐跳 Noul，要求全部通过。

**来源：** [Cookbook — citation check](https://docs.typesafe.ai/cookbooks/citation_check) · [官方文档 — patterns](https://docs.typesafe.ai/patterns)

---

### 人工升级触发
**Primitive:** Noul · **Added:** 2026-09-28

这事需要人来看吗？一个问题把低置信路径变成显式分支，而不是无声的错答。

```python
"escalate": Noul(
    instructions="Does this situation need a human decision before we act?",
),
```

**接线与阈值**
- 代码组合：`noul ≥ 0.6` **或** 配套 Choice 的最高概率低于下限即升级——两个独立的不确定信号。
- 每次升级都是下月调阈值的标注样本；存完整响应，不只存数字。

**失效模式**
- 问"这重要吗"——重要性不可判定；"需要人来判断吗"才可判定。说清人要做的那个决定。

**来源：** [官方文档 — confidence](https://docs.typesafe.ai/confidence) · [Cookbook — classification using confidence](https://docs.typesafe.ai/cookbooks/classification_using_confidence)

---

### 重试 / 跳过控制
**Primitive:** Noul · **Added:** 2026-09-28

失败的 LLM/工具调用该重试还是放弃？在 agent 循环里省预算也省延迟。

```python
"retry": Noul(
    instructions="Is this failure likely to succeed on a plain retry?",
),
# state = {"task": ..., "error": ..., "attempts": 2}
```

**接线与阈值**
- 仅当 `noul ≥ 0.6` 且 `attempts < 3` 才重试——计数器与副作用归代码，Jev 只做判断。
- 把原始错误文本放进 state；"瞬态 vs 权限错误"正是 Jev 擅长的类型化判断。

**失效模式**
- 用它掩盖 bug：同一错误持续 0.9 重试说明你的失败分类法错了，不是需要更多重试。

**来源：** [TypeSafeAI/jev-harness](https://github.com/TypeSafeAI/jev-harness) · [官方文档 — patterns](https://docs.typesafe.ai/patterns)
