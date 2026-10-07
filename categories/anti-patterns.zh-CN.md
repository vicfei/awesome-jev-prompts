# 反模式——Jev 问题是怎样写坏的

> 中文译本，以[英文版](anti-patterns.md)为准（同步于 2026-10-08）。

失去对 Jev 信任的最快方式是一个设计糟糕的问题。以下都是反复出现的失效模式，各附修复方法。每一条都在公开项目中出现过或在官方文档中被点名。

---

### 1. 让 Jev 做计算
**Added:** 2026-09-28

Jev 不擅长数学、计数和日期——它是判断模型，不是计算器。

- ❌ `Noul("发票总额是否大于行项目之和？")`
- ✅ 求和在代码里做完；只在必要时问 `Noul(" stated totals 与行项目一致吗？")`，算术自己验。

**规则：** 算术、计数、日期运算归代码；Jev 判断数字*意味着什么*。

**来源：** [walidboulanouar/awesome-jev-use-cases（Jev 1.13 局限）](https://github.com/walidboulanouar/awesome-jev-use-cases) · [官方文档 — primitives](https://docs.typesafe.ai/primitives)

---

### 2. 开放式的"Choice"
**Added:** 2026-09-28

Choice 需要可枚举的有限选项集（上限 255；超了会静默退化到更慢的两阶段路径）。"选个最好的标题"是 System Two 模型的活，然后再用 Jev 做 best-of-N。

**来源：** [发布文章](https://typesafe.ai/blog/introducing-system-one-models-and-jev) · [Cookbook — hierarchical classification](https://docs.typesafe.ai/cookbooks/hierarchical_classification)

---

### 3. 不留逃生选项
**Added:** 2026-09-28

凡是选项清单可能不完整的 Choice，都需要 `other` / `none_of_the_above` / `review`。没有它，Jev 被迫把异类硬塞进某个选项——日志看起来更干净，实际是错的。

**来源：** [Anil-matcha/awesome-jev-by-typesafe（设计规则）](https://github.com/Anil-matcha/awesome-jev-by-typesafe) · [官方文档 — patterns](https://docs.typesafe.ai/patterns)

---

### 4. Score 用无序评分尺
**Added:** 2026-09-28

Score 的 `criteria` 必须是**严格有序**的等级列表（答案可以落在两级之间）。无序集合（"红/蓝/绿"）是穿了 Score 外套的 Choice——"两级之间"没有方向，结果毫无意义。

**来源：** [官方文档 — primitives](https://docs.typesafe.ai/primitives)

---

### 5. 把 Noul 0.5 读作"中等"
**Added:** 2026-09-28

Noul 返回陈述为真的概率。**0.5 是不确定，不是中等分。** 不要像评分一样在 0.33/0.66 处三分；要设行动带和升级带（如 ≥ 0.8 行动、≤ 0.4 放行、中间 → 显式不确定分支）。

**来源：** [Anil-matcha/awesome-jev-by-typesafe（设计规则）](https://github.com/Anil-matcha/awesome-jev-by-typesafe) · [官方文档 — confidence](https://docs.typesafe.ai/confidence)

---

### 6. 全局一套阈值
**Added:** 2026-09-28

不存在被祝福的 0.7。阈值按动作、按风险等级分别定——审核拦截和"锦上添花"标记不共享 cutoff。各自从日志概率分布里拟合（见[校准与评估](calibration-and-eval.zh-CN.md)）。

**来源：** [Anil-matcha/awesome-jev-by-typesafe（设计规则）](https://github.com/Anil-matcha/awesome-jev-by-typesafe) · [Cookbook — classification using confidence](https://docs.typesafe.ai/cookbooks/classification_using_confidence)

---

### 7. 阈值敏感路径上信任 `jev-latest`
**Added:** 2026-09-28

别名会漂移（`jev-latest`、`jev-preview` 都指向会变的版本）。阈值依赖模型行为时，锁定版本号（`jev-1.13.0`）并**记录实际返回的版本**，而不是你请求的别名。

**来源：** [Anil-matcha/awesome-jev-by-typesafe（设计规则）](https://github.com/Anil-matcha/awesome-jev-by-typesafe) · [官方文档 — models](https://docs.typesafe.ai/models)

---

### 8. 忽略与 argmax 相左的概率
**Added:** 2026-09-28

`choice` 是分布的顶端；`probabilities` 才是分布。前两名 0.45 / 0.42 时，"决定"就是抛硬币——分支去复审，别上线。置信度门就是为这个存在的。

**来源：** [官方文档 — confidence](https://docs.typesafe.ai/confidence) · [Cookbook — classification using confidence](https://docs.typesafe.ai/cookbooks/classification_using_confidence)

---

### 9. 让问题拥有组合或副作用
**Added:** 2026-09-28

元规则：**问题只描述判断；组合、阈值与副作用归代码。**"进哪个文件夹、什么优先级、要不要邮件经理？"塞进一个问题，是三个判断加一个动作——判断拆开，动作留给代码。

**来源：** [Anil-matcha/awesome-jev-by-typesafe（设计规则）](https://github.com/Anil-matcha/awesome-jev-by-typesafe) · [官方文档 — patterns](https://docs.typesafe.ai/patterns)

---

### 10. 拿 Jev 做授权或替代人工审核
**Added:** 2026-09-28

Jev 不是权限系统、输入校验器或人工审核员。它可以把请求*路由*到权限检查；不能*成为*权限检查。校准描述的是群体而非单次输出——任何单次输出都不配得到盲信。

**来源：** [Anil-matcha/awesome-jev-by-typesafe（"What Jev is not"）](https://github.com/Anil-matcha/awesome-jev-by-typesafe) · [官方文档 — confidence](https://docs.typesafe.ai/confidence)
