# 结构化状态模式——当你的状态是一张表而不是一段文字

> 中文译本，以[英文版](structured-state-patterns.md)为准（同步于 2026-10-28）。

决策模型（Jev、Clef、StartLux）读自然语言状态。表格基础模型（TabPFN、LimiX、TabFM）把训练表当上下文读。契约相同——状态 + 问题 → 校准概率，一次前向——但状态形态不同。这些模式覆盖边界：什么时候走哪条范式，以及当你的证据住在列里而不是句子里时，怎么设计问题。

本分类所有条目均为 **derived** 级——从两种范式的文档行为与我们自己的测量推导，除非标注了社区来源。

---

### 列语义进状态
**原语：** Composite（状态设计）· **收录：** 2026-10-28 · **状态：** derived

结构化数据喂给决策模型时，列名和单位作为带标签的块进入 `state`——模型需要知道 `account_balance_usd = 450` 意味着什么，而不只是一个数字。

```python
state = {
    "customer_profile": {
        "account_age_days": 320,
        "balance_usd": 450,
        "overdraft_count_90d": 3,
        "credit_score": 680,
    },
    "request": "Customer asks for a credit limit increase to $5000.",
}
# 问题: Noul("Should this request be approved without manual review?")
```

**接线与阈值**
- 列名带单位和时间窗（`overdraft_count_90d`，不要 `od_cnt`）——模型按字面读名字。
- 把动作上下文（这个决定触发什么）放在单独的 state 字段里，不要混进列块。

**失败模式**
- 没有列名的裸数字数组：模型按位置做模式匹配，列序一变就坏。

---

### 表格 FM 当廉价门闸
**原语：** Composite（路由）· **收录：** 2026-10-28 · **状态：** derived

当状态大部分是结构化的（数值/分类列），且任务是行级分类或回归时，表格基础模型比绕道文本决策模型更便宜、常常也更好。只有判断需要读散文时才用决策模型。

```python
# 按状态形态路由，不按习惯：
if state_is_mostly_tabular(rows) and task in ("classification", "regression"):
    score = tabular_fm.predict(training_rows, query_row)     # TabPFN / LimiX
else:
    answer = jev.ask(state, questions)                        # Jev / Clef / StartLux
```

**接线与阈值**
- 表格 FM 的主场是小数据（几百到 ~10K 行做上下文）；超出后，在整表上训练的经典梯度提升赢。
- 两种范式都返回校准概率——阈值纪律可迁移，但要按模型重拟合（见[校准与评测](calibration-and-eval.zh-CN.md)）。

**失败模式**
- 给表格 FM 一个需要读散文的任务（工单、法律条款）——它没有文本理解通路。

---

### 跨范式校准
**原语：** Score（对比）· **收录：** 2026-10-28 · **状态：** derived

当表格 FM 和决策模型在同一任务上各出概率时，先在同一留出集上分别校准再比较——不同模型族的原始概率不在同一标尺上。用 proper scoring rule（Brier、log loss）做公共指标。

**接线与阈值**
- 在同一校准切分上为每个模型拟合温度（或等渗回归）。
- 比较校准后概率，不比原始输出——TabPFN 的 0.7 和 Jev 的 0.7 校准前可能意味着不同的东西。

**失败模式**
- 不校准就比 AUC：排序质量和绝对概率质量是两个不同的属性（[minimind-jev 基准](https://github.com/vicfei/jev-rag-zh-benchmark)有一个 AUC/nDCG 分歧的实测例子）。
