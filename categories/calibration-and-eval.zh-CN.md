# 校准与评估——让阈值值得信任

> 中文译本，以[英文版](calibration-and-eval.md)为准（同步于 2026-10-08）。

"它返回一个数字"和"这个数字有意义"之间的距离。这里收集的是流程模式：怎么选阈值、怎么保持阈值的诚实、什么时候交给 System Two。

---

### 从日志分布拟合双阈值带
**Added:** 2026-09-28

不要拍脑袋定 cutoff。拿几百条真实日志跑一遍这个问题，按真值分组画出答案分布，在两类人群**实际分开**的位置放一条行动带和一条升级带。

- 每次调用都完整记录（答案、概率、置信度、实际返回的模型版本）——它同时就是你的评估数据集。
- 分布漂移时重新拟合；漂移是"该重调"的信号，不是"模型不行"的判决。

**来源：** [Cookbook — classification using confidence](https://docs.typesafe.ai/cookbooks/classification_using_confidence) · [官方文档 — confidence](https://docs.typesafe.ai/confidence)

---

### 问题版本化，模型锁定
**Added:** 2026-09-28

把问题文本当 schema 对待：一旦阈值依赖它，就冻结、编号、有意识地变更。模型同理：锁定 `jev-1.13.0`，逐调用记录返回版本。"上周还好用"应该能从日志里回答。

**来源：** [官方文档 — models](https://docs.typesafe.ai/models) · [Anil-matcha/awesome-jev-by-typesafe（设计规则）](https://github.com/Anil-matcha/awesome-jev-by-typesafe)

---

### 高风险答案的一致性检查
**Added:** 2026-09-28

同一判断换措辞问两遍（或用 Choice 和 Noul 各编码一次）。不同框架下一致的答案远比单次高置信可信；不一致自动升级。

**来源：** [Cookbook — consistency (Noul)](https://docs.typesafe.ai/cookbooks/consistency_noul_cookbook) · [Cookbook — consistency (Choice)](https://docs.typesafe.ai/cookbooks/consistency_choice_cookbook)

---

### 切换前的影子模式
**Added:** 2026-09-28

让 Jev 的决定与现有规则/LLM 决定并行运行，记录分歧率和"本可避免的错误"率，数字达标再切换。社区 harness 已把它做成一等公民特性。

**来源：** [AntonioCoppe/jev-harness（shadow mode）](https://github.com/AntonioCoppe/jev-harness) · [kenhuangus/jev-usecases（置信度门控）](https://github.com/kenhuangus/jev-usecases)

---

### 知道何时升级到 System Two
**Added:** 2026-09-28

Jev 是快而便宜的判断层——不是最后一道防线，也不是整个大脑。健康的架构是双院制：反射（分类、路由、门控）在 Jev；深思（计划、起草、解释）在 LLM；交接由 Jev 自己的置信信号触发。TypeSafeAI 社区 harness 与多个其他 harness 都是这个结构。

**来源：** [TypeSafeAI/jev-harness（"the model proposes, Jev supplies evidence, code decides"）](https://github.com/TypeSafeAI/jev-harness) · [AbdelStark/bicameral](https://github.com/AbdelStark/bicameral) · [发布文章](https://typesafe.ai/blog/introducing-system-one-models-and-jev)
