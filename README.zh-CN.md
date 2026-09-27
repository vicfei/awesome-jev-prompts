# Awesome Jev Prompts（中文版）

> 面向 [Jev](https://typesafe.ai/blog/introducing-system-one-models-and-jev)（TypeSafe AI 的 System One 模型）的问题模式库：经过验证的问题模板、反模式与校准实践。**在类型化决策的世界里，"问题设计"就是提示词工程。**

[![Stars](https://img.shields.io/github/stars/OWNER/awesome-jev-prompts?style=social&label=Star)](https://github.com/OWNER/awesome-jev-prompts/stargazers)
[![Link check](https://github.com/OWNER/awesome-jev-prompts/actions/workflows/link-check.yml/badge.svg)](https://github.com/OWNER/awesome-jev-prompts/actions/workflows/link-check.yml)
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
| 模态 | 仅文本——不支持图像、音频、视频 |

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
