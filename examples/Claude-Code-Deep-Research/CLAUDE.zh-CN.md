# CLAUDE.md

本文件为 Claude Code (claude.ai/code) 处理此代码库时提供指导。

## 项目概述

这是一个 **Claude Code 深度研究代理**框架，实现了一个复杂的多代理研究系统，用于进行全面的、有引用的研究项目。它利用 Claude Code 的原生功能复制并增强了 OpenAI 的 Deep Research 和 Google Gemini 的 Deep Research 能力。

**核心技术：**
- **思维图谱 (GoT) 框架** - 基于图推理的智能研究路径管理
- **七阶段深度研究流程** - 质量研究的结构化方法论
- **多代理架构** - 具有专门角色的并行研究代理
- **引用验证系统** - A-E 源质量评级与验证链

## 快速启动命令

### 主要研究命令

```bash
/deep-research [研究主题]
```

此命令执行完整的研究工作流：
1. 问题精炼（询问澄清问题）
2. 带有子主题的研究规划
3. 多代理并行研究部署
4. 源三角验证与综合
5. 引用验证
6. 输出到 `RESEARCH/[主题]/` 目录

### 分步命令

```bash
/refine-question [原始问题]     # 生成结构化研究提示
/plan-research [结构化提示]     # 创建执行计划
/synthesize-findings [目录]    # 合并研究成果
/validate-citations [文件]      # 验证引用质量
```

## 架构

### 七阶段研究流程

1. **问题界定** - 定义边界、输出格式、约束条件
2. **检索规划** - 将主题分解为子主题，规划代理部署
3. **迭代查询** - 部署并行研究代理（3-8 个代理）
4. **源三角验证** - 跨源交叉验证发现
5. **知识综合** - 合并为带有引用的连贯叙述
6. **质量保证** - 事实核查、验证引用、检测幻觉
7. **输出与包装** - 生成结构化研究文档

### 技能系统

`.claude/skills/` 目录包含模块化的研究能力：

| 技能 | 用途 | 使用时机 |
|------|------|----------|
| `question-refiner` | 将原始问题转换为结构化提示 | 模糊主题、范围未定义 |
| `research-executor` | 执行完整的七阶段研究流程 | 结构化研究提示 |
| `got-controller` | 管理复杂主题的思维图谱 | 多方面研究、质量关键 |
| `citation-validator` | 验证引用的准确性和质量 | 最终报告、发布准备 |
| `synthesizer` | 合并多个代理的发现 | 矛盾源、综合报告 |

### 思维图谱操作

GoT 框架将研究管理为具有以下转换的图：

- **Generate(k)**：从节点生成 k 个并行研究路径
- **Aggregate(k)**：将 k 个发现合并为更强的综合
- **Refine(1)**：在不进行新研究的情况下改进现有发现
- **Score**：根据引用、准确性、完整性评级质量 (0-10)
- **KeepBestN(n)**：剪枝到每层 top n 个节点

**研究模式：**
- **平衡模式**：Generate(4-5) → 评分最佳 → 深化顶部路径 → 聚合
- **深度优先**：Generate(3) → 选取最佳 → 从中 Generate(3) → 继续
- **广度优先**：Generate(8) → KeepBestN(5) → 从每个 Generate(2) → 聚合

### 多代理部署策略

执行研究时，并行部署代理：

```
阶段 3：迭代查询
├── 网络研究代理 (3-5)：当前信息、趋势、新闻
├── 学术/技术代理 (1-2)：论文、规范
└── 交叉引用代理 (1)：事实核查、验证
```

每个代理接收：
- 研究重点的清晰描述
- 具体的搜索查询
- 预期的输出格式
- 引用要求

## 输出结构

研究输出创建在 `RESEARCH/[topic_name]/`：

```
RESEARCH/[topic_name]/
├── README.md                    # 概述和导航
├── executive_summary.md         # 1-2 页关键发现
├── full_report.md               # 完整分析 (20-50 页)
├── data/
│   └── statistics.md           # 关键数字、事实
├── visuals/
│   └── descriptions.md         # 图表/图形描述
├── sources/
│   ├── bibliography.md        # 完整引用
│   └── source_quality_table.md # A-E 评级
├── research_notes/
│   └── agent_findings_summary.md # 原始代理输出
└── appendices/
    ├── methodology.md          # 研究方法
    └── limitations.md         # 未知、空白
```

## 引用要求

**每个事实主张必须包括：**
1. 作者/组织名称
2. 发布日期
3. 来源标题
4. 直接 URL/DOI
5. 页码（如果适用）

**来源质量评级：**
- **A**：同行评审的随机对照试验、系统综述、元分析
- **B**：队列研究、临床指南、知名分析师
- **C**：专家意见、病例报告、机制研究
- **D**：预印本、初步研究、博客
- **E**：趣闻、理论、推测

## 工具权限

`.claude/settings.local.json` 文件配置允许的工具：
- **WebSearch**：通用网络搜索
- **mcp__playwright__***：用于动态内容的浏览器自动化
- **Task**：部署自主研究代理
- **TodoWrite**：跟踪研究进度
- **Read/Write**：管理研究文档

## 开发笔记

### 修改技能时

`.claude/skills/[name]/` 中的每个技能包含：
- `SKILL.md`：YAML 前置matter + 描述
- `instructions.md`：详细实现指导
- `examples.md`：使用示例

创建新技能时：
1. 遵循现有结构
2. 在 SKILL.md 中包含清晰的 YAML 前置matter
3. 提供全面的说明
4. 添加多样化的示例

### 修改命令时

`.claude/commands/[name].md` 中的命令是用户快捷方式。每个命令：
- 具有描述、参数提示、允许工具的 YAML 前置matter
- 引用适当的技能执行
- 应简单且专注

### 思维图状态管理

使用 GoT Controller 进行研究时：
- 在整个执行过程中维护图状态
- 在 `research_notes/got_operations_log.md` 中记录操作
- 将各个节点保存到 `research_notes/got_nodes/[id].md`
- 使用 TodoWrite 跟踪 GoT 操作

## 关键文档

- `CLAUDE.md`：此文件 - Claude Code 快速参考
- `CLAUDE2.md`：完整思维图谱实现指南
- `PROJECT_UNDERSTANDING.md`：详细架构和设计
- `IMPLEMENTATION_GUIDE.md`：用户指南，包含示例和工作流
- `.claude/skills/*/instructions.md`：技能特定说明

## 重要约束

- 所有研究输出放入 `RESEARCH/[topic]/` 目录
- 将大型文档拆分为小文件以避免上下文限制
- 使用 TodoWrite 跟踪任务完成
- 使用并行代理部署（单个响应，多个 Task 调用）
- 在最终确定报告前验证引用
- 永不无根据地做出主张 - 如果不确定，声明"需要来源"
