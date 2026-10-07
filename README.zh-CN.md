# Awesome Jev Prompts（中文版）

> 面向 [Jev](https://typesafe.ai/blog/introducing-system-one-models-and-jev)（TypeSafe AI 的 System One 模型）的问题模式库：经过验证的问题模板、反模式与校准实践。**在类型化决策的世界里，"问题设计"就是提示词工程。**

[![Stars](https://img.shields.io/github/stars/vicfei/awesome-jev-prompts?style=social&label=Star)](https://github.com/vicfei/awesome-jev-prompts/stargazers)
[![Link check](https://github.com/vicfei/awesome-jev-prompts/actions/workflows/link-check.yml/badge.svg)](https://github.com/vicfei/awesome-jev-prompts/actions/workflows/link-check.yml)
[![License: CC0](https://img.shields.io/badge/license-CC0-007ec6)](LICENSE)

**English version is [here](README.md).** 条目正文（模板与代码）以英文维护，欢迎提交中文场景的实践。

Jev 返回的是**类型化答案**——**Choice**（选择）、**Score**（评分）、**Noul**（0–1 概率判断）——附带概率，70–500 毫秒内出结果。它不生成任何文本，所以你在 LLM 上积累的提示词技巧几乎全部失效。真正起作用的是**问题设计**：怎么把一个决策拆成原子判断、选项描述怎么措辞、阈值定在哪、什么时候不该信任那个数字。本库收录实践中有效的模式，以及悄悄毁掉生产系统的反模式。

## Jev 是什么

一个 "System One" 模型（命名来自卡尼曼的"快思考"）：输入非结构化状态，输出类型化的概率决策。它放弃字符串生成，换来类型安全且校准过的输出——在"判断"形状的任务上比聊天模型快两个数量级、便宜两个数量级。

| 原语 | 你提供 | 你得到 |
|---|---|---|
| **Choice** | `instructions` + `criteria` 字典（选项 → 描述） | 选中的选项、每个选项的 `probabilities`、`confidence` |
| **Score** | `instructions` + `criteria` **有序**评分等级列表 | 概率加权的 `score`（可落在两级之间）、`legend`、`probabilities`、`confidence` |
| **Noul** | 仅 `instructions` | `noul`：陈述为真的概率，0–1 |

速查（对应 Jev 1.13，请以[官方文档](https://docs.typesafe.ai/models)为准）：

| | |
|---|---|
| 端点 | `POST https://api.typesafe.ai/v1/systemone` |
| 别名 / 版本 | `jev-latest`、`jev-preview` → `jev-1.13.0`（别名会漂移，阈值敏感场景请锁定版本） |
| 价格 | 输入 $0.042 / 百万 token；输出免费 |
| 上下文 | 每请求 64k token（32k 状态 + 最长问题） |
| 限制 | 250k token/秒；1,200 请求/分钟 |
| 模态 | 仅文本（Jev 本体）——多模态 System One 变体已出现，见[生态动态](#生态动态) |

## 快速上手

见 [README.md 快速上手](README.md#quick-start)（Python / TypeScript 双示例）。

## 模式库 — 8 个分类 43 条

| 分类 | 条数 | 覆盖内容 |
|---|---|---|
| [Choice 模式](categories/choice-patterns.md) | 6 | 意图路由、工具选择、模型路由、Best-of-N、文档分类、技能路由 |
| [Score 模式](categories/score-patterns.md) | 5 | 严重度、质量门禁、内容审核、RAG 相关性、优先级 |
| [Noul 模式](categories/noul-patterns.md) | 5 | 策略检查、去重、引用核验、人工升级、重试控制 |
| [路由与分诊](categories/routing-and-triage.md) | 4 | 收件箱分诊、工单队列、RAG 过滤、文档流 |
| [护栏与校验](categories/guardrails-and-verification.md) | 5 | 输出护栏、越狱检测、结构化校验、代码评审门禁 |
| [上下文压缩](categories/context-compaction.md) | 3 | 保留或丢弃、摘要或原文、工具结果裁剪 |
| [反模式](categories/anti-patterns.md) | 10 | Jev 问题十种常见的翻车方式与修复方法 |
| [校准与评估](categories/calibration-and-eval.md) | 5 | 从日志定阈值、问题版本化、影子模式、何时交给 System Two |

**一条衍生出大半规则的元规则：** *问题只描述判断；组合、阈值与副作用归代码。*

## 我该用哪个模式？

- **从你可控的选项集合里挑一个** → [Choice 模式](categories/choice-patterns.md)——意图、工具、模型路由、Best-of-N
- **在量表上给强度或质量打分** → [Score 模式](categories/score-patterns.md)——严重度、门禁、审核、相关性
- **问"是否为真 / 是否违规 / 是否同一个"** → [Noul 模式](categories/noul-patterns.md)——策略、去重、引用、升级
- **给非结构化的输入流分拣** → [路由与分诊](categories/routing-and-triage.md)
- **评判另一个模型的输出** → [护栏与校验](categories/guardrails-and-verification.md)
- **决定上下文窗口里留什么** → [上下文压缩](categories/context-compaction.md)
- **以上任何一条上线之前** → 先读[反模式](categories/anti-patterns.md)，再读[校准与评估](categories/calibration-and-eval.md)

## 验证政策

每条条目都引用来源，来源分三类——上线前请先看清是哪类：

- **官方文档（Documented）**——基于 TypeSafe 官方文档或 cookbook（已链接）。模式的*形态*有据可查，示例措辞是我们写的。
- **社区实践（Community-observed）**——有公开项目或文章报告在这么做（已链接）。我们描述其做法，不构成背书。
- **推导实践（Derived practice）**——从已文档化规则推导的工程默认值；无外部来源处已注明。

**本清单中的阈值是起点，不是实测结果。** 请在你自己的日志分布上重新拟合——这正是[校准与评估](categories/calibration-and-eval.md)分类存在的意义。

## 生态动态

本清单的问题设计方法可跨 System One 模型迁移。值得关注的进展：

- **2026-10-08 · 问题设计技能化。** 可安装的 agent 技能开始从不同角度覆盖本清单的领域：[VBS2004/jev-questions-skill](https://github.com/VBS2004/jev-questions-skill)（9 条实测规则 + 5 个标准库检查脚本）、[PyModel/jev-skill](https://github.com/PyModel/jev-skill)（11 种实现形态带代码草图）、[abhisheksharma001/jev-skill](https://github.com/abhisheksharma001/jev-skill)（适配检查、代码库发现、问题优化，基准数据诚实）、[wuyoscar/jev-skill](https://github.com/wuyoscar/jev-skill)（5 个技能 + 108 个场景模板）。它们与本清单互补——想把它们串成一条工作流，可以用 [jev-pipeline-skill](https://github.com/vicfei/jev-pipeline-skill)：find → fit → draft → lint → spread → threshold → cascade。

**与这些技能的配合方式**：① 在本库挑模式起草问题 → ② 用 [VBS2004/jev-questions-skill](https://github.com/VBS2004/jev-questions-skill) 的 `lint_questions.py` + `spread.py` 做静态与区分度检查（纯标准库、不调 API）→ ③ 拿不准该不该用 Jev 就跑 [abhisheksharma001/jev-skill](https://github.com/abhisheksharma001/jev-skill) 的 `fit_check.py`（确定性 go/no-go）→ ④ 或直接用 [jev-pipeline-skill](https://github.com/vicfei/jev-pipeline-skill) 一条命令串起来（可装为 Claude Code / Codex / OpenCode / ClawHub 技能）。
- **2026-10-02 · 视觉来了。** [PixelJev](https://arxiv.org/abs/2609.29283)（论文：原生图像的类型化决策——图像 + 指令 + 候选集 → 结构化输出）、[OneJev](https://github.com/OmniJev/OneJev)（对屏幕、照片、视频和文本的类型化问题，单次前向传播给出校准答案）、[Valen](https://github.com/Liuziyu77/Valen)（自己训练 Jev 式多模态模型）把这一范式扩展到了像素。对问题设计的影响：Choice/Score/Noul 的思路对视觉状态原样适用，但阈值必须按模态重新校准——不要照搬文本上调好的阈值。

## 官方资源

- [文档](https://docs.typesafe.ai/) — [原语](https://docs.typesafe.ai/primitives) · [模式](https://docs.typesafe.ai/patterns) · [置信度](https://docs.typesafe.ai/confidence) · [状态](https://docs.typesafe.ai/concepts/state) · [用例地图](https://docs.typesafe.ai/concepts/use-case-map) · [快速开始](https://docs.typesafe.ai/introduction/quickstart)
- SDK — [Python](https://github.com/typesafe-ai/typesafe-sdk-python) · [JavaScript](https://github.com/typesafe-ai/typesafe-sdk-js) · [Skills 仓库](https://github.com/typesafe-ai/skills)
- [TypeSafeAI/jev-harness](https://github.com/TypeSafeAI/jev-harness) — 官方编码 harness："模型提议，Jev 提供证据，代码做决定"
- [评测](https://evals.typesafe.ai/) · [控制台与 Playground](https://console.typesafe.ai/) · [发布文章](https://typesafe.ai/blog/introducing-system-one-models-and-jev)
- 也可通过 [Vercel AI Gateway](https://vercel.com/ai-gateway/models/jev) 与 [Cloudflare Workers AI](https://developers.cloudflare.com/ai/models/typesafe/jev/) 使用

## 相关清单

英文版 README 底部维护着社区清单对照表（星数由 CI 每日刷新）：[查看](README.md#related-lists)。

## 贡献

有有效的模式或踩过的坑？欢迎 PR / issue——一个 PR 一条模式、必须附来源、必须含模板。见 [CONTRIBUTING.md](CONTRIBUTING.md)。纠错优先于新增——一行错误的信息比一行缺失的信息代价更大。

## 许可

[CC0 1.0](LICENSE)——贡献至公共领域，随意使用。

**免责声明：** 本仓库为独立社区资源，与 TypeSafe AI 无隶属关系。事实性数据（价格、限制、行为）引用自公开来源，可能变动，请以[官方文档](https://docs.typesafe.ai/)为准。
