# Claude Code 深度研究代理

一个 sophisticated 的多代理研究框架，使用 Claude Code 的原生功能实现了 OpenAI 和 Google Gemini 的深度研究能力。

## 概述

本项目利用 Claude Code 的技能(Skills)和命令(Commands)系统，通过以下方式开展全面的、带有引用验证的研究：

- **思维图谱框架(Graph of Thoughts, GoT)** - 基于图结构的推理，实现智能研究路径管理
- **七阶段深度研究流程** - 结构化的研究方法论，确保研究质量
- **多代理架构** - 具有专业角色的并行研究代理
- **引用验证系统** - A-E 源质量评级与验证链

## 快速开始

### 前置条件

- 已安装 Claude Code CLI
- 具有 API 访问权限的 Claude Code 账户

### 安装

1. 克隆此仓库：
```bash
git clone <repository-url>
cd Claude-Code-Deep-Research-main
```

2. 技能和命令已在 `.claude/` 目录中配置完成

### 基本使用

执行深度研究最简单的方式：

```bash
/deep-research [你的研究主题]
```

**示例：**
```bash
/deep-research AI在临床诊断中的应用
```

此单一命令将：
1. 询问澄清问题以细化研究需求
2. 创建结构化的研究计划
3. 部署多个并行研究代理
4. 综合发现形成全面的报告
5. 验证所有引用来源
6. 将结果输出到 `RESEARCH/[主题]/` 目录

## 高级用法

### 分步研究工作流

如需对研究过程进行更多控制：

#### 1. 细化问题
```bash
/refine-question 我应该在我的项目中使用WebAssembly吗？
```

问题细化器将询问5-6个澄清问题，涉及：
- 具体关注领域
- 输出格式要求
- 地理和时间范围
- 目标受众
- 特殊要求

#### 2. 制定研究计划（可选）
```bash
/plan-research [来自步骤1的结构化提示]
```

创建详细的执行计划，显示：
- 主题如何分解为子主题
- 将部署哪些代理
- 预期时间线

#### 3. 执行研究
```bash
/deep-research [你的主题]
```

#### 4. 综合发现（如需要）
```bash
/synthesize-findings RESEARCH/[主题]/research_notes/
```

#### 5. 验证引用
```bash
/validate-citations RESEARCH/[主题]/full_report.md
```

## 项目结构

```
claude-code-deep-research/
├── .claude/
│   ├── skills/                    # 研究技能
│   │   ├── question-refiner/      # 问题细化
│   │   ├── research-executor/     # 主要研究执行
│   │   ├── got-controller/        # 思维图谱控制器
│   │   ├── citation-validator/    # 引用验证
│   │   └── synthesizer/           # 研究综合
│   ├── commands/                  # 用户命令
│   │   ├── deep-research.md       # 主要研究命令
│   │   ├── refine-question.md     # 问题细化
│   │   ├── plan-research.md       # 研究计划
│   │   ├── synthesize-findings.md # 发现综合
│   │   └── validate-citations.md  # 引用验证
│   └── settings.local.json        # 工具权限设置
├── RESEARCH/                      # 研究输出
│   └── [topic_name]/
│       ├── README.md
│       ├── executive_summary.md
│       ├── full_report.md
│       ├── data/
│       ├── visuals/
│       ├── sources/
│       ├── research_notes/
│       └── appendices/
├── CLAUDE.md                      # Claude Code 快速参考
├── CLAUDE2.md                     # 思维图谱指南
├── PROJECT_UNDERSTANDING.md       # 架构文档
├── IMPLEMENTATION_GUIDE.md        # 用户指南
└── README.md                      # 本文件
```

## 研究输出结构

每个研究项目都会创建结构化输出：

```
RESEARCH/[topic_name]/
├── README.md                    # 概述和导航
├── executive_summary.md         # 1-2页的关键发现
├── full_report.md               # 完整分析（20-50页）
├── data/
│   └── statistics.md            # 关键数字和事实
├── visuals/
│   └── descriptions.md          # 图表描述
├── sources/
│   ├── bibliography.md          # 完整引用
│   └── source_quality_table.md  # A-E质量评级
├── research_notes/
│   └── agent_findings_summary.md # 原始代理输出
└── appendices/
    ├── methodology.md           # 研究方法
    └── limitations.md           # 未知和空白
```

## 引用要求

每个事实声明都需包含：
1. 作者/组织名称
2. 发布日期
3. 来源标题
4. 直接URL/DOI
5. 页码（如适用）

**来源质量评级：**
- **A**：同行评审的随机对照试验、系统综述、元分析
- **B**：队列研究、临床指南、知名分析师报告
- **C**：专家意见、案例报告、机制研究
- **D**：预印本、初步研究、博客
- **E**：趣闻、理论推测、主观臆断

## 思维图谱框架

GoT框架将研究管理为图结构，具有以下操作：

| 操作 | 目的 | 示例 |
|------|------|------|
| **Generate(k)** | 生成k条并行研究路径 | Generate(4)从根节点 → 4条研究路径 |
| **Aggregate(k)** | 将k个发现综合为一份报告 | Aggregate(3) → 1份综合报告 |
| **Refine(1)** | 改进现有发现 | Refine(node_5) → 提升质量 |
| **Score** | 质量评分(0-10) | 基于引用和准确性评分 |
| **KeepBestN(n)** | 剪枝保留前n个节点 | KeepBestN(3) → 保留最佳3个 |

**研究模式：**
- **平衡模式**：Generate(4-5) → 评分最佳 → 深化最优 → 综合
- **深度优先**：Generate(3) → 取最佳 → 从中生成(3)
- **广度优先**：Generate(8) → KeepBestN(5) → 每个生成2个

## 文档

| 文档 | 描述 |
|------|------|
| `CLAUDE.md` | Claude Code 实例的快速参考 |
| `CLAUDE2.md` | 完整的思维图谱实现 |
| `PROJECT_UNDERSTANDING.md` | 详细的架构和设计 |
| `IMPLEMENTATION_GUIDE.md` | 带有示例和工作流的用户指南 |

## 命令参考

| 命令 | 用法 | 描述 |
|------|------|------|
| `/deep-research` | `/deep-research [主题]` | 执行完整的研究工作流 |
| `/refine-question` | `/refine-question [问题]` | 将问题细化为结构化提示 |
| `/plan-research` | `/plan-research [提示]` | 创建执行计划 |
| `/synthesize-findings` | `/synthesize-findings [目录]` | 合并研究输出 |
| `/validate-citations` | `/validate-citations [文件]` | 验证引用质量 |

## 示例

### 市场研究
```bash
/deep-research AI在医疗保健市场，重点关注临床诊断，
              综合报告，全球范围，2022-2024年数据，
              目标受众是医疗保健高管
```

### 技术评估
```bash
/deep-research WebAssembly vs JavaScript 性能基准
```

### 学术文献综述
```bash
/deep-research AI中的Transformer架构，
              仅同行评审来源，2017年至今，
              综合文献综述
```

## 功能特性

- 多代理并行研究（3-8个代理同时工作）
- 思维图谱优化确保研究质量
- 自动引用验证
- 来源质量评级（A-E量表）
- 验证链防止幻觉
- 结构化输出，包含执行摘要
- 跨来源三角验证

## 性能

- **快速研究**（狭窄主题）：10-15分钟
- **标准研究**（中等范围）：20-30分钟
- **综合研究**（广泛主题）：30-60分钟
- **学术文献综述**：45-90分钟

## 贡献

欢迎贡献！要添加新技能或改进：

1. 遵循 `.claude/skills/` 中的技能结构
2. 包含 `SKILL.md`、`instructions.md`、`examples.md`
3. 用多样化主题测试
4. 更新文档

## 许可证

本项目按原样提供，仅用于教育和研究目的。

## 致谢

- 思维图谱框架灵感来自 [SPCL, ETH Zürich](https://github.com/spcl/graph-of-thoughts)
- 基于 [Claude Code](https://claude.ai/code) 构建
- 七阶段研究流程基于深度研究最佳实践

---

**详细使用说明，请参阅 [IMPLEMENTATION_GUIDE.md](IMPLEMENTATION_GUIDE.md)**

**架构详情，请参阅 [PROJECT_UNDERSTANDING.md](PROJECT_UNDERSTANDING.md)**
