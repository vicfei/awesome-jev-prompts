# 路由与分诊——给非结构化输入流分拣

> 中文译本，以[英文版](routing-and-triage.md)为准（同步于 2026-10-08）。

组合式流水线：一次 Jev 请求携带多个原子问题（各自独立评估），代码负责组合结果。发布文章里"智能 if else"的领地——分类、路由、打分、分支。

模板使用 Python SDK（`python -m pip install typesafe-sdk`）。

---

### 收件箱 / 邮件分诊
**Primitive:** Choice + Score + Noul · **Added:** 2026-09-28

一次请求三个问题：这是什么、多急、今天要不要回。社区最爱炫的性价比示例——输入 $0.042/百万 token、输出免费，大批量只要几美分。

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

**接线与阈值**
- 三个答案在代码里组合出文件夹/队列（如 `action_needed && urgency >= 2 && needs_reply >= 0.7 → today_queue`）——绝不要问 Jev"进哪个文件夹"这种糅在一起的大问题。
- 批量处理：很多邮件共用一个循环，每封延迟仍低于半秒。

**失效模式**
- 模仿个人语气的营销邮件落进 `personal`——`spam_promo` 的描述要点名这种伪装（"语气亲切但在卖东西"）。

**来源：** [walidboulanouar/awesome-jev-use-cases（demo 目录）](https://github.com/walidboulanouar/awesome-jev-use-cases) · [发布文章](https://typesafe.ai/blog/introducing-system-one-models-and-jev)

---

### 支持工单优先级队列
**Primitive:** Choice + Score · **Added:** 2026-09-28

先部门后严重度——标签空间是两个维度的乘积时，小层级结构胜过一个扁平大问题。

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

**接线与阈值**
- `unrouted` → 默认队列加人工一瞥；绝不让模型为了逃避分支而硬猜部门。
- 客户每次回复后重跑——状态变了，答案可能也变了。

**失效模式**
- 愤怒工单的严重度通胀：情绪化语言抬高分数。若也要测语气，放单独的 Score，让代码（而不是问题）决定两者独立。

**来源：** [Cookbook — hierarchical classification](https://docs.typesafe.ai/cookbooks/hierarchical_classification) · [快速上手示例](https://github.com/Anil-matcha/awesome-jev-by-typesafe)

---

### RAG 段落过滤
**Primitive:** Score + Noul · **Added:** 2026-09-28

检索了 40 段、提示词只装得下 8 段：先按相关性过滤，再按实体匹配核验，排序、截断。

```python
# 每段一次，并行扇出：
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

**接线与阈值**
- `relevance ≥ 2.5` 或（`relevance ≥ 2` 且 `entity_match ≥ 0.8`）才保留；Noul 拯救"对实体但部分相关"的段落免于被砍。
- 每查询每段落都跑——分数分布就是免费获得的检索质量监控。

**失效模式**
- 同实体不同问题的段落拿 2 分混进来；相关性 criteria 要写"回答**这个**问题"，不是"关于**这个**主题"。

**来源：** [Cookbook — classifying RAG passages](https://docs.typesafe.ai/cookbooks/classifying_rag_passages) · [Cookbook — rerank](https://docs.typesafe.ai/cookbooks/rerank_typesafe) · 社区实践：[hotchpotch/jev-reranker](https://github.com/hotchpotch/jev-reranker)、[erendikmenn/jev-rag-benchmark](https://github.com/erendikmenn/jev-rag-benchmark)

---

### 文档流分拣
**Primitive:** Choice · **Added:** 2026-09-28

混合文档洪流（扫描件、导出、转发）要落进 N 个桶并留审计轨迹。Jev 分类；代码归档、改名、建链。

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

**接线与阈值**
- `manual` 是泄压阀——周报里它的占比飙升，说明某个类别定义已经腐烂。
- 喂提取后的文本（需要先 OCR）：Jev 仅支持文本，不收图像和 PDF 字节。

**失效模式**
- 跨类别混合体（HR 合同）——选*处理*归属（"谁对它行动"），不选*主题*；流水线关乎行动。

**来源：** [官方文档 — use-case map](https://docs.typesafe.ai/concepts/use-case-map) · [官方文档 — state](https://docs.typesafe.ai/concepts/state)
