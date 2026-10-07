# Choice 模式——从有限集合中选择

> 中文译本，以[英文版](choice-patterns.md)为准（同步于 2026-10-08）。

Choice 接收 `instructions` + 一个 `选项 → 描述` 的 `criteria` 字典，返回选中的选项、每个选项的 `probabilities` 和 `confidence`。Choice 的选项数上限为 255；更大的集合会退化到较慢的两阶段流程，所以大分类请用层级式问题拆分。

模板使用 Python SDK（`python -m pip install typesafe-sdk`）；TypeScript 等价写法见[快速上手](../README.md#quick-start)。

---

### 意图路由
**Primitive:** Choice · **Added:** 2026-09-28

在任何下游分支之前，先选出客户的主要意图。分诊流水线的经典第一问。

```python
"intent": Choice(
    instructions="What is the customer's main request?",
    criteria={
        "refund": "The customer wants money returned.",
        "technical_help": "The customer needs a bug or integration fixed.",
        "information": "The customer is asking for information only.",
        "other": "None of the other options clearly fits.",
    },
),
```

**接线与阈值**
- 按 `answers["intent"].choice` 路由；当 `probabilities["other"]` 排在首位或 `confidence` 低于路由下限时，送 `other` 或转人工。
- 选项描述必须互斥——描述重叠会把概率质量推给 `other`。

**失效模式**
- 混合意图的工单被硬塞进一个桶；应拆成多个并行的原子问题，而不是一个巨无霸问题。
- 选项蔓延：每"就加这一次"的新意图都会劣化整个集合的校准。

**来源：** [快速上手示例](https://github.com/Anil-matcha/awesome-jev-by-typesafe) · [官方文档 — patterns](https://docs.typesafe.ai/patterns)

---

### Agent 的工具选择
**Primitive:** Choice · **Added:** 2026-09-28

在 agent 循环展开工具列表之前，让 Jev 选出与当前步骤匹配的那一个工具（或"不用工具"）。能显著减少编码 harness 中的工具结果噪音与 token 开销。

```python
"tool": Choice(
    instructions="Which tool should handle the current step?",
    criteria={
        "search": "The step needs code/text search over the workspace.",
        "edit": "The step is a concrete file edit with a known target.",
        "run": "The step needs a command or test execution.",
        "none": "No tool is needed; the model should answer directly.",
    },
),
```

**接线与阈值**
- 以 `confidence` 设闸；低置信时回退为向 agent 展示完整工具列表。
- `none` 防止对话轮次被强制调用工具——这是社区 harness 仓库里报告最多的单点修复。

**失效模式**
- 描述写给人看而不是用于匹配原始工具输出；应写工具的触发条件，不是实现方式。

**来源：** [TypeSafeAI/jev-harness](https://github.com/TypeSafeAI/jev-harness) · [官方文档 — agent skill](https://docs.typesafe.ai/agent-skill)

---

### 模型路由
**Primitive:** Choice · **Added:** 2026-09-28

选择本轮该由哪个下游 LLM（档位/力度）服务。Jev 适合放在热路径上，因为 ~70–500ms 就返回，远低于 System Two 模型的首 token 时间。

```python
"route": Choice(
    instructions="Which model tier should answer this turn?",
    criteria={
        "fast": "Simple, low-risk, mostly mechanical request.",
        "standard": "Normal complexity; no safety or correctness stakes.",
        "premium": "Complex reasoning, high stakes, or a failed earlier attempt.",
    },
),
```

**接线与阈值**
- 搭配一个人工升级 Noul 问题（见 [Noul 模式](noul-patterns.zh-CN.md)），让"premium"获得两次独立投票后再付费。
- 把路由档位与实际返回的模型版本一起记日志，审计漂移。

**失效模式**
- 依据礼貌用语/格式等线索而非任务复杂度路由——在 criteria 里写清"复杂"意味着什么，最好带例子。

**来源：** [JoacoMarc/jev-harness-router](https://github.com/JoacoMarc/jev-harness-router) · [官方文档 — use-case map](https://docs.typesafe.ai/concepts/use-case-map)

---

### Best-of-N 选择
**Primitive:** Choice · **Added:** 2026-09-28

你用 LLM 生成了 N 个草稿（回复、摘要、commit message）；Jev 按声明的标准选出最好的一个——便宜到可以每次请求都跑。

```python
"best": Choice(
    instructions="Which draft best answers the user, factually and in tone?",
    criteria={
        "draft_1": "Draft 1.",  # 各草稿文本放进 state，此处仅作稳定引用
        "draft_2": "Draft 2.",
        "draft_3": "Draft 3.",
        "reject_all": "No draft is acceptable; regenerate.",
    },
),
```

**接线与阈值**
- 草稿放在 `state`（如 `state={"drafts": [...]}`），criteria 保持稳定引用，这样问题文本在多次调用间保持一致。
- `reject_all` 高于某个下限（如最高选项概率 < 0.5）触发一次重新生成，然后硬停止——不要无限循环。

**失效模式**
- 位置偏差：跨批次复用选择时轮换草稿顺序。

**来源：** [官方文档 — confidence](https://docs.typesafe.ai/confidence) · [Cookbook — parallel questions](https://docs.typesafe.ai/cookbooks/parallel_questions)

---

### 文档类型分类
**Primitive:** Choice · **Added:** 2026-09-28

发票 / 收据 / 合同 / 垃圾邮件——每条文档流水线的入口问题，经典的"智能 if else"。

```python
"doc_type": Choice(
    instructions="What kind of document is this?",
    criteria={
        "invoice": "Requests payment; has line items and totals.",
        "receipt": "Confirms a completed payment.",
        "contract": "Defines obligations between parties.",
        "correspondence": "A letter or email, no payment or obligations.",
        "unknown": "Not clearly any of the above.",
    },
),
```

**接线与阈值**
- 分类体系深于 ~15 个标签时，用层级分类（粗组 → 细类），不要做一个 255 选项的扁平问题。
- 喂提取后的文本，不要喂扫描件——Jev 仅支持文本。

**失效模式**
- Jev 不擅长数学、计数和日期；依据结构和措辞分类，绝不依据"总额看起来大于…"。

**来源：** [Cookbook — hierarchical classification](https://docs.typesafe.ai/cookbooks/hierarchical_classification) · [官方文档 — primitives](https://docs.typesafe.ai/primitives)

---

### 技能 / 专家路由
**Primitive:** Choice · **Added:** 2026-09-28

在加载提示词之前，把用户轮次路由到匹配的 agent 技能或专家包——Jev 原生的关键词触发替代方案。

```python
"skill": Choice(
    instructions="Which skill should handle this request?",
    criteria={
        "data_analysis": "Needs dataset inspection, charts, or computation.",
        "writing": "Drafting or rewriting user-facing prose.",
        "ops": "Deploy, restart, or infrastructure operations.",
        "none": "General conversation; no skill applies.",
    },
),
```

**接线与阈值**
- 技能描述应对齐"技能何时应该触发"，而不是"里面有什么"；描述与行为的脱节会表现为误路由。
- `none` 应该赢得平局而不是输掉——检查 `probabilities` 排序，不要只看 argmax。

**失效模式**
- 两个触发条件几乎相同的技能会分裂概率并卡住；合并它们，或补充消歧 criteria。

**来源：** [typesafe-ai/skills](https://github.com/typesafe-ai/skills) · [官方文档 — agent skill](https://docs.typesafe.ai/agent-skill)
