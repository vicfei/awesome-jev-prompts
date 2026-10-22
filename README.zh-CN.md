# Awesome Jev Prompts（中文版）

> 面向 [Jev](https://typesafe.ai/blog/introducing-system-one-models-and-jev)（TypeSafe AI 的 System One 模型）的问题模式库：经过验证的问题模板、反模式与校准实践。**在类型化决策的世界里，"问题设计"就是提示词工程。**

[![Stars](https://img.shields.io/github/stars/vicfei/awesome-jev-prompts?style=social&label=Star)](https://github.com/vicfei/awesome-jev-prompts/stargazers)
[![Link check](https://github.com/vicfei/awesome-jev-prompts/actions/workflows/link-check.yml/badge.svg)](https://github.com/vicfei/awesome-jev-prompts/actions/workflows/link-check.yml)
[![License: CC0](https://img.shields.io/badge/license-CC0-007ec6)](LICENSE)

**English version is [here](README.md).** 全部 51 条条目均提供[中文译本](#-模式库--9-个分类-51-条)（以英文版为准，同步于 2026-10-08）。

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

## 模式库 — 9 个分类 51 条

| 分类 | 条数 | 覆盖内容 |
|---|---|---|
| [Choice 模式](categories/choice-patterns.zh-CN.md) | 6 | 意图路由、工具选择、模型路由、Best-of-N、文档分类、技能路由 |
| [Score 模式](categories/score-patterns.zh-CN.md) | 5 | 严重度、质量门禁、内容审核、RAG 相关性、优先级 |
| [Noul 模式](categories/noul-patterns.zh-CN.md) | 5 | 策略检查、去重、引用核验、人工升级、重试控制 |
| [路由与分诊](categories/routing-and-triage.zh-CN.md) | 4 | 收件箱分诊、工单队列、RAG 过滤、文档流 |
| [护栏与校验](categories/guardrails-and-verification.zh-CN.md) | 5 | 输出护栏、越狱检测、结构化校验、代码评审门禁 |
| [上下文压缩](categories/context-compaction.zh-CN.md) | 3 | 保留或丢弃、摘要或原文、工具结果裁剪 |
| [反模式](categories/anti-patterns.zh-CN.md) | 10 | Jev 问题十种常见的翻车方式与修复方法 |
| [校准与评估](categories/calibration-and-eval.zh-CN.md) | 5 | 从日志定阈值、问题版本化、影子模式、何时交给 System Two |
| [具身与多模态](categories/embodied-multimodal-patterns.zh-CN.md) | 8 | 咨询门控、能力表、任务合同、多模态状态绑定、逐轴控制 |

**一条衍生出大半规则的元规则：** *问题只描述判断；组合、阈值与副作用归代码。*

## 我该用哪个模式？

- **从你可控的选项集合里挑一个** → [Choice 模式](categories/choice-patterns.zh-CN.md)——意图、工具、模型路由、Best-of-N
- **在量表上给强度或质量打分** → [Score 模式](categories/score-patterns.zh-CN.md)——严重度、门禁、审核、相关性
- **问"是否为真 / 是否违规 / 是否同一个"** → [Noul 模式](categories/noul-patterns.zh-CN.md)——策略、去重、引用、升级
- **给非结构化的输入流分拣** → [路由与分诊](categories/routing-and-triage.zh-CN.md)
- **评判另一个模型的输出** → [护栏与校验](categories/guardrails-and-verification.zh-CN.md)
- **决定上下文窗口里留什么** → [上下文压缩](categories/context-compaction.zh-CN.md)
- **问屏幕、视频或机器人** → [具身与多模态](categories/embodied-multimodal-patterns.zh-CN.md)
- **以上任何一条上线之前** → 先读[反模式](categories/anti-patterns.zh-CN.md)，再读[校准与评估](categories/calibration-and-eval.zh-CN.md)

## 验证政策

每条条目都引用来源，来源分三类——上线前请先看清是哪类：

- **官方文档（Documented）**——基于 TypeSafe 官方文档或 cookbook（已链接）。模式的*形态*有据可查，示例措辞是我们写的。
- **社区实践（Community-observed）**——有公开项目或文章报告在这么做（已链接）。我们描述其做法，不构成背书。
- **推导实践（Derived practice）**——从已文档化规则推导的工程默认值；无外部来源处已注明。

**本清单中的阈值是起点，不是实测结果。** 请在你自己的日志分布上重新拟合——这正是[校准与评估](categories/calibration-and-eval.md)分类存在的意义。

## 生态动态

本清单的问题设计方法可跨 System One 模型迁移。值得关注的进展：

- **2026-10-22 · 开源权重在中文基准上追平 hosted 模型。** [jev-rag-zh-benchmark](https://github.com/vicfei/jev-rag-zh-benchmark) 迎来首批开源权重成绩：[StartLux-Decision 27B AutoThink](https://github.com/StartLuxLabs/Startlux-Decision)（经 [bamboonode](https://bamboonode.dev/) 免费托管，同一 `/v1/systemone` 请求、同一冻结问题措辞）在 T2Reranking 难负例上 score-zh nDCG@5 **0.557** / noul-zh **0.540**——对 hosted Jev-1.13 配对 **+0.011 [−0.039, +0.060]**（统计打平、点估计略高），对 BM25 **+0.144 [+0.064, +0.227]**（显著）；其 noul 分离度 AUC 0.727 为本样本最高。中文重排的选型从此不再只是"hosted Jev 或没有"——带免费托管的开源权重已统计打平。阈值仍需按引擎单独拟合。

- **2026-10-22 · 服务层收敛到 System One 线格式。** [vllm-jev](https://github.com/mode-io/vllm-jev)（668★）现已服务 24+ 个开源检查点（Laya、Kev、Decider、Open-Jev、JevK5……含 Clef），覆盖 Linux/Apple Silicon；其实验性 RadixFlow 调度器建立在一个正确的观察上——决策负载的打分走 **prefill**，共享前缀复用正是吞吐量所在。[StartLux](https://github.com/StartLuxLabs/Startlux-Decision)（1,183★，0.8B–27B，arXiv 2610.17309）自带 vLLM/llama.cpp/MLX 引擎、说同一种 `/v1/systemone` 格式，另有 27B 免费托管。对问题设计的含义："Jev 兼容"正在变成线格式属性而非厂商属性——本清单的模式适用于任何应答引擎，问题措辞才是可移植的部分。

- **2026-10-21 · 3 分钟从零训练的头追平 hosted Jev；蒸馏的反而不行。** [minimind-jev](https://github.com/vicfei/minimind-jev)（已公开）在冻结 bge-small-zh 上训练一个 66 万参数的决策头——笔记本 RTX 4060 训练 3 分钟、零 API 成本：nDCG@5 0.488，对 hosted Jev-1.13 的 0.546（n=100 配对 CI 含零，不可分），显著胜 BM25（+0.075）。有教益的负结果：把前沿教师的四级判断（其期望分 AUC 0.716 就在 Jev 同档）蒸馏进同一个头，反而**掉到 0.428**——纯蒸馏与混合监督三种配置一致。当你的指标已有二元 gold 标签时，直接监督胜过教师软标签。检查点：[cnfeichen/minimind-jev-v0.1](https://huggingface.co/cnfeichen/minimind-jev-v0.1)；教师判断已[作为数据集发布](https://huggingface.co/datasets/cnfeichen/t2reranking-4level-judgments)。对问题设计的含义：[RAG 相关性评分](categories/score-patterns.zh-CN.md#相关性评分rag)这对模式里"谁来给你的问题打分"，现在有了实测答案——数据集自己的标签，而不是教师评分尺。

- **2026-10-12 · 全模态竞速。** 视觉波已经拥挤——并且撞名了：[OmniJev](https://github.com/tinnel123666888/OmniJev)（全模态：图像/视频/屏幕/机器人场景，开放权重）、[shapsider/OmniJev](https://github.com/shapsider/OmniJev)（MuJoCo 具身工作台，Qwen3.5-9B + 校正头——我们具身模式的第四个独立印证）、[jev-omni.js](https://github.com/ai-ecoverse/jev-omni.js)（WebGPU 在浏览器里跑决策模型，DecisionBench 上与 fp32 对齐）加入了 [OneJev](https://github.com/OmniJev/OneJev)（163★）与 [Valen](https://github.com/Liuziyu77/Valen) 的行列。三个几乎同名的项目、尚无标准——引用时请确认名字指向的到底是哪个模型。多模态类型化决策的供给方越多，问题设计的消费方越多：[具身与多模态](categories/embodied-multimodal-patterns.zh-CN.md)分类的模式对它们全部适用。

- **2026-10-12 · 第一批中文实测数字。** [jev-rag-zh-benchmark](https://github.com/vicfei/jev-rag-zh-benchmark)：Jev Score 在 T2Reranking 难负例上 **nDCG@5 0.546 vs BM25 0.413**（n=100、单次运行、锁定 `typesafe/jev-1.13-20260917`）；纯排序场景 Score 与 Noul 几乎打平；分离度 AUC≈0.715。本清单的 RAG 相关性与 Noul 阈值从此有了中文实测参照——按验证政策计 **measured** 级来源。

- **2026-10-12 · "内在 Jev"配方。** [Releasing the Inner Jev](https://arxiv.org/abs/2610.17205)（Geuter、Cheng、Alvarez-Melis）主张这种能力并不绑定专用架构：开源指令模型只需读末位 token 上选项字母的 logit，零训练就能回答类型化选择题——Gemma 4 31B 在其 OpenDecisions 集上 79.6，Jev 为 80.1。再加一份轻量配方（LoRA + 从 LM head 切片初始化的 decision head），同一模型在 OpenDecisions 拿到 84.4、JevBench v1.7 上 81.5，两项都反超 Jev 约 4 个点；模型、serving 代码与 2,352 题数据集全部开源。对问题设计的含义：若任何指令模型都能坐在同一份契约之下，耐久的资产就是问题本身——本库模式适用于任何打分引擎。

- **2026-10-10 · 小型开源决策模型出现。** [THX-01](https://huggingface.co/doofz/THX-01)（HAL-X AI，[发布说明](https://huggingface.co/blog/doofz/thx-01-we-open-sourced-a-322m-decision-model-that)）：322M mmBERT-base 编码器 + ~15M 决策头，单次前向（~10 ms）覆盖六种能力（Choice、Noul、Score、Number、Excerpt、Citation），8 阶段 RLCD 后训练、210 万条决策、18 语种，Apache 2.0，另有托管 API 与 `pip install thx01`。其内部多语工单基准自称对 Jev 1.13 约 98.4% 准确率——同时承认精确数字查找输给 Jev（93.4% vs 96.6%）；厂商自测、serving 条件不同，但这份诚实的胜负切分本身就有参考价值。对问题设计的含义：问题设计不再绑定托管 API——模式集从此可以在边缘侧落地。

- **2026-10-08 · 编码 Agent 工具链收敛。** harness 生态已经沉淀出一份合同：模型提议，Jev 回答窄化的类型问题，**代码组合裁定，host 授权执行**——没有任何实现允许 Jev 打补丁或授予权限（[TypeSafeAI/jev-harness](https://github.com/TypeSafeAI/jev-harness)，注意：独立于 TypeSafe AI 的社区组织；[PerryLink/jevcore](https://github.com/PerryLink/jevcore)）。反复出现的实践：离线 mock 优先开发、门控默认关闭、出口披露、每个 Noul 都写判定边界。模型调用正收敛到锁版本：[jev-permission-gate](https://github.com/madisonrickert/jev-permission-gate) 锁定 `jev-1.13.0`（阈值在该版本上调校，并做了双盲标注评估），还向老用户发出从 `jev-latest` 迁移的提示——正是[反模式 #7](categories/anti-patterns.zh-CN.md#7-信任-jev-latest-当阈值敏感时)的田野验证。价格参照：[jev-decision-gate](https://github.com/f-tiger/jev-decision-gate) 实测输入价格约为前沿聊天模型的 1/238。
- **2026-10-08 · RAG 之波。** 重排是 Jev 落地最集中的方向：[hotchpotch/jev-reranker](https://github.com/hotchpotch/jev-reranker)（相关性过滤 + 重排库）、[WiktorB2004/llama-index-jev](https://github.com/WiktorB2004/llama-index-jev)（LlamaIndex 适配器）、[spring-ai-community/spring-ai-typesafe](https://github.com/spring-ai-community/spring-ai-typesafe)（Spring AI 官方社区集成，提供 `JevDocumentFilter` / `JevDocumentReranker`）、[erendikmenn/jev-rag-benchmark](https://github.com/erendikmenn/jev-rag-benchmark) 与 [PPRAMANIK62/yc-jev-bench](https://github.com/PPRAMANIK62/yc-jev-bench)（可复现基准）、[aifabrice/jev-rag](https://github.com/aifabrice/jev-rag)（本地优先知识检索，零向量库依赖）。社区对 Jev 在这里的角色已收敛：**昂贵 cross-encoder 之前的廉价预过滤层**——正是本库[相关性评分](categories/score-patterns.zh-CN.md#相关性评分rag)与 [RAG 过滤](categories/routing-and-triage.zh-CN.md#rag-段落过滤)这对模式的位置。
- **2026-10-08 · 问题设计技能化。** 可安装的 agent 技能开始从不同角度覆盖本清单的领域：[VBS2004/jev-questions-skill](https://github.com/VBS2004/jev-questions-skill)（9 条实测规则 + 5 个标准库检查脚本）、[PyModel/jev-skill](https://github.com/PyModel/jev-skill)（11 种实现形态带代码草图）、[abhisheksharma001/jev-skill](https://github.com/abhisheksharma001/jev-skill)（适配检查、代码库发现、问题优化，基准数据诚实）、[wuyoscar/jev-skill](https://github.com/wuyoscar/jev-skill)（5 个技能 + 108 个场景模板）。它们与本清单互补——想把它们串成一条工作流，可以用 [jev-pipeline-skill](https://github.com/vicfei/jev-pipeline-skill)：find → fit → draft → lint → spread → threshold → cascade。
- **2026-10-02 · 视觉来了。** [PixelJev](https://arxiv.org/abs/2609.29283)（论文：原生图像的类型化决策——图像 + 指令 + 候选集 → 结构化输出）、[OneJev](https://github.com/OmniJev/OneJev)（对屏幕、照片、视频和文本的类型化问题，单次前向传播给出校准答案）、[Valen](https://github.com/Liuziyu77/Valen)（自己训练 Jev 式多模态模型）把这一范式扩展到了像素。对问题设计的影响：Choice/Score/Noul 的思路对视觉状态原样适用，但阈值必须按模态重新校准——不要照搬文本上调好的阈值。
- **2026-10-01 · 头部云厂商入场。** Cloudflare 发布 [Clef 与 Clef-flash](https://blog.cloudflare.com/clef-decision-models)：冻结 Qwen 底座（3.8-27B / 3.5-9B）+ 路由头 + rank-256 LoRA，prefill-only 两阶段注意力并行给 schema 选项打分；Apache 2.0 权重（[clef](https://huggingface.co/Cloudflare/clef)、[clef-flash](https://huggingface.co/Cloudflare/clef-flash)），且 Jev-API 兼容、可直接替换。训练用 label-smoothed 交叉熵 + Brier loss，RLCD 作为第二优化目标——相邻序数选项给部分分、参考惩罚抗分布漂移。目前登顶 Jev Decision Index，Clef-flash 中位延迟 ~38.8 ms（Jev 约 ~524 ms）。对问题设计的含义：Jev 兼容不再等于只能用 Jev——类型化的问题可以原样跨引擎迁移。
- **2026-09-29 · 第一份独立学术评测。** [Evaluating and Benchmarking the System One Model Jev](https://arxiv.org/abs/2609.37647)（Deußer、Sparrenberg、Sifa）对 Jev v1.13.0 做 37 个公开数据集的零样本评测——346,009 次请求、总花费不到 $10：对 Qwen3.8-27B 27/37 胜、对 Gemma-4-E4B 37/37 全胜，Choice 概率校准足以支撑选择性预测。对本清单最有教益的负面发现：二分类概率相对固定 0.5 阈值表现不佳——调阈值后 UNFAIR-ToS micro-F1 从 0.50 升到 0.75，这正是[校准与评测](categories/calibration-and-eval.zh-CN.md)存在的理由。选项轮换与去题检查排除了浅层捷径。
- **2026-09-24 · Jev 作为零样本对齐检测器。** [Just Ask Jev](https://arxiv.org/abs/2609.29429)（Guo 等）用类型化问题替代生成式裁判：单个通用问题在 RLCDAlignBench（10 类失败类型、44 个基准、5 个目标模型）上零样本 median AUROC 0.886，成本仅为 LLM-judge 裁判的 1/63，与参照裁判对人工标注的一致度持平。其设计教训本身就是一条模式：问题措辞影响甚微，而承载参照物的上下文字段——用户的信念、被注入的指令——影响巨大；失败是关系性的，要把"问什么"与"给什么看"分开。代码与数据：[sumleo/RLCDAlignBench](https://github.com/sumleo/RLCDAlignBench)。

**与这些技能的配合方式**：① 在本库挑模式起草问题 → ② 用 [VBS2004/jev-questions-skill](https://github.com/VBS2004/jev-questions-skill) 的 `lint_questions.py` + `spread.py` 做静态与区分度检查（纯标准库、不调 API）→ ③ 拿不准该不该用 Jev 就跑 [abhisheksharma001/jev-skill](https://github.com/abhisheksharma001/jev-skill) 的 `fit_check.py`（确定性 go/no-go）→ ④ 或直接用 [jev-pipeline-skill](https://github.com/vicfei/jev-pipeline-skill) 一条命令串起来（可装为 Claude Code / Codex / OpenCode / ClawHub 技能）。

## 官方资源

- [文档](https://docs.typesafe.ai/) — [原语](https://docs.typesafe.ai/primitives) · [模式](https://docs.typesafe.ai/patterns) · [置信度](https://docs.typesafe.ai/confidence) · [状态](https://docs.typesafe.ai/concepts/state) · [用例地图](https://docs.typesafe.ai/concepts/use-case-map) · [快速开始](https://docs.typesafe.ai/introduction/quickstart)
- SDK — [Python](https://github.com/typesafe-ai/typesafe-sdk-python) · [JavaScript](https://github.com/typesafe-ai/typesafe-sdk-js) · [Skills 仓库](https://github.com/typesafe-ai/skills)
- [TypeSafeAI/jev-harness](https://github.com/TypeSafeAI/jev-harness) — TypeSafeAI 社区组织（独立于 TypeSafe AI）的参考编码 harness："模型提议，Jev 提供证据，代码做决定"
- [评测](https://evals.typesafe.ai/) · [控制台与 Playground](https://console.typesafe.ai/) · [发布文章](https://typesafe.ai/blog/introducing-system-one-models-and-jev)
- 也可通过 [Vercel AI Gateway](https://vercel.com/ai-gateway/models/jev) 与 [Cloudflare Workers AI](https://developers.cloudflare.com/ai/models/typesafe/jev/) 使用

## 相关清单

英文版 README 底部维护着社区清单对照表（星数由 CI 每日刷新）：[查看](README.md#related-lists)。

## 贡献

有有效的模式或踩过的坑？欢迎 PR / issue——一个 PR 一条模式、必须附来源、必须含模板。见 [CONTRIBUTING.md](CONTRIBUTING.md)。纠错优先于新增——一行错误的信息比一行缺失的信息代价更大。

## 许可

[CC0 1.0](LICENSE)——贡献至公共领域，随意使用。

**免责声明：** 本仓库为独立社区资源，与 TypeSafe AI 无隶属关系。事实性数据（价格、限制、行为）引用自公开来源，可能变动，请以[官方文档](https://docs.typesafe.ai/)为准。
