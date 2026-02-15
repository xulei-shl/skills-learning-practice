# Claude Code Subagents 最佳实践

> 基于 Claude Code Hooks Mastery 项目的 Subagents 实践经验总结

---

## 1. Subagents 核心概念

### 1.1 什么是 Subagents

Subagents 是专门的 AI 助手，拥有独立的上下文窗口、自定义系统提示词、特定的工具访问权限和独立的权限控制。

### 1.2 信息流

```
用户 (User)
    ↓
主代理 (Primary Agent)
    ↓
子代理 (Subagent) ← 响应主代理的提示，非用户
    ↓
主代理 (整合结果)
    ↓
用户 (User)
```

**关键点**：
- Subagents 不直接与用户通信
- Subagents 响应主代理的提示词
- Subagents 从新开始，无对话历史

### 1.3 Subagent 存储位置

| 位置 | 作用域 | 优先级 |
|------|--------|--------|
| `--agents` CLI 参数 | 当前会话 | 1 (最高) |
| `.claude/agents/` | 当前项目 | 2 |
| `~/.claude/agents/` | 全局用户 | 3 |
| 插件 `agents/` 目录 | 插件范围 | 4 (最低) |

---

## 2. Subagent 文件格式

### 2.1 基本结构

```yaml
---
name: code-reviewer
description: Expert code review specialist. Proactively reviews code for quality, security, and maintainability. Use immediately after writing or modifying code.
tools: Read, Grep, Glob, Bash
model: sonnet
---

# Code Reviewer

你是一个高级代码审查员...
```

### 2.2 Frontmatter 字段

| 字段 | 必需 | 说明 |
|------|------|------|
| `name` | ✅ | 唯一标识符（小写字母+连字符）|
| `description` | ✅ | 何时调用此代理 |
| `tools` | ❌ | 允许的工具列表 |
| `disallowedTools` | ❌ | 禁止的工具 |
| `model` | ❌ | 模型选择 |
| `color` | ❌ | 终端颜色标识 |
| `permissionMode` | ❌ | 权限模式 |
| `skills` | ❌ | 预加载的 Skills |
| `hooks` | ❌ | 生命周期 Hooks |

---

## 3. 团队协作模式

### 3.1 Builder-Validator 模式

项目展示了经典的团队协作模式：

```yaml
# .claude/agents/team/builder.md
---
name: builder
description: Generic engineering agent that executes ONE task at a time
model: opus
color: cyan
hooks:
  PostToolUse:
    - matcher: "Write|Edit"
      hooks:
        - type: command
          command: "uv run $CLAUDE_PROJECT_DIR/.claude/hooks/validators/ruff_validator.py"
        - type: command
          command: "uv run $CLAUDE_PROJECT_DIR/.claude/hooks/validators/ty_validator.py"
---

# Builder

## Purpose
你是一个专注的工程代理，负责执行单一任务...

## Workflow
1. 理解任务
2. 执行
3. 验证
4. 完成任务
```

```yaml
# .claude/agents/team/validator.md
---
name: validator
description: Read-only validation agent that checks if a task was completed successfully
model: opus
disallowedTools: Write, Edit, NotebookEdit
color: yellow
---

# Validator

## Purpose
你是只读验证代理，负责验证任务完成...

## Workflow
1. 理解任务和验收标准
2. 检查工作
3. 验证
4. 报告
```

### 3.2 团队编排工具

| 工具 | 用途 |
|------|------|
| `TaskCreate` | 创建任务 |
| `TaskUpdate` | 更新状态、添加阻塞 |
| `TaskList` | 查看所有任务 |
| `TaskGet` | 获取任务详情 |
| `Task` | 部署代理执行工作 |

### 3.3 任务依赖管理

```typescript
// Task 2 依赖 Task 1
TaskUpdate({
  taskId: "2",
  addBlockedBy: ["1"]
})

// 依赖链
Task 1: 基础设置     → 无依赖
Task 2: 实现功能     → blockedBy: ["1"]
Task 3: 编写测试     → blockedBy: ["2"]
Task 4: 最终验证     → blockedBy: ["1", "2", "3"]
```

---

## 4. Subagent 最佳实践

### 4.1 描述字段设计

描述是 Claude 决定何时调用代理的关键：

```yaml
description: "Expert code review specialist. Proactively reviews code for quality, security, and maintainability. Use immediately after writing or modifying code."
```

**要点**：
- 说明代理职责
- 说明使用时机
- 使用主动语言（"Proactively"）
- 包含触发关键词

### 4.2 工具限制

```yaml
# 只读代理
tools: Read, Grep, Glob, Bash
disallowedTools: Write, Edit, MultiEdit

# 构建代理（可写）
tools: Read, Edit, Write, Glob, Grep, Bash

# 数据库代理
tools: Bash
hooks:
  PreToolUse:
    - matcher: "Bash"
      hooks:
        - type: command
          command: "./scripts/validate-readonly-query.sh"
```

### 4.3 Skills 预加载

```yaml
---
name: api-developer
description: Implement API endpoints following team conventions
skills:
  - api-conventions
  - error-handling-patterns
---

实现 API 端点，遵循预加载 skill 中的约定...
```

**注意**：
- Skills 内容被注入到代理上下文
- Subagents 不继承主会话的 Skills
- 内置代理（Explore, Plan）无法使用 Skills

### 4.4 代理级别 Hooks

```yaml
---
name: builder
hooks:
  PostToolUse:
    - matcher: "Write|Edit"
      hooks:
        - type: command
          command: "uv run ruff_validator.py"
---

# Builder

执行任务时自动验证代码...
```

---

## 5. 工作流模式

### 5.1 扇出-汇总模式

```
主代理 Skill
├── 并行启动 N 个 Subagent（扇出）
│   ├── Subagent 1 → 结果 1
│   ├── Subagent 2 → 结果 2
│   └── Subagent N → 结果 N
└── 汇总所有结果 → 最终报告
```

### 5.2 管道模式

```
Subagent A（收集）→ 结果
    ↓
Subagent B（分析）→ 结果
    ↓
Subagent C（生成）→ 结果
```

### 5.3 链式代理

```typescript
// 第一步：分析
Task({
  subagent_type: "analyzer",
  prompt: "分析代码库...",
  description: "分析代码"
})

// 第二步：优化（使用第一步结果）
Task({
  subagent_type: "optimizer",
  prompt: "根据分析结果优化...",
  description: "优化代码"
})
```

---

## 6. 后台执行

### 6.1 前台 vs 后台

| 模式 | 行为 | 用途 |
|------|------|------|
| **前台** | 阻塞主对话 | 需要用户交互 |
| **后台** | 并发执行 | 独立任务 |

### 6.2 后台调用

```typescript
Task({
  description: "Build API",
  prompt: "实现 API...",
  subagent_type: "builder",
  run_in_background: true  // 后台运行
})
```

### 6.3 恢复模式

```typescript
// 首次部署
Task({
  description: "Build user service",
  prompt: "创建用户服务...",
  subagent_type: "builder"
})
// 返回: agentId: "abc123"

// 后续恢复
Task({
  description: "Continue user service",
  prompt: "现在添加验证...",
  subagent_type: "builder",
  resume: "abc123"  // 保留上下文
})
```

---

## 7. 常见模式示例

### 7.1 代码审查代理

```yaml
---
name: code-reviewer
description: Expert code review specialist. Proactively reviews code for quality, security, and maintainability.
tools: Read, Grep, Glob, Bash
model: inherit
---

# Code Reviewer

## Instructions

1. 运行 git diff 查看更改
2. 聚焦修改的文件
3. 立即开始审查

## 审查清单

- 代码清晰可读
- 函数和变量命名良好
- 无重复代码
- 适当的错误处理
- 无暴露的密钥
- 实现输入验证
- 良好的测试覆盖
- 考虑性能

## 输出格式

提供按优先级组织的反馈：
- Critical（必须修复）
- Warnings（应该修复）
- Suggestions（考虑改进）

包括如何修复的具体示例。
```

### 7.2 调试代理

```yaml
---
name: debugger
description: Debugging specialist for errors, test failures, and unexpected behavior. Use proactively when encountering any issues.
tools: Read, Edit, Bash, Grep, Glob
---

# Debugger

## Instructions

1. 捕获错误消息和堆栈跟踪
2. 识别复现步骤
3. 隔离故障位置
4. 实现最小修复
5. 验证解决方案

## 调试过程

- 分析错误消息和日志
- 检查最近的代码更改
- 形成并测试假设
- 添加战略性调试日志
- 检查变量状态

## 输出

对每个问题提供：
- 根因解释
- 支持诊断的证据
- 具体代码修复
- 测试方法
- 预防建议
```

### 7.3 只读数据库代理

```yaml
---
name: db-reader
description: Execute read-only database queries. Use when analyzing data or generating reports.
tools: Bash
hooks:
  PreToolUse:
    - matcher: "Bash"
      hooks:
        - type: command
          command: "./scripts/validate-readonly-query.sh"
---

# Database Reader

你是只读数据库分析师。执行 SELECT 查询来回答问题。

## 规则

- 仅允许 SELECT 查询
- 无法修改数据
- 如被要求 INSERT/UPDATE/DELETE，解释只有只读权限
```

---

## 8. 与其他组件集成

### 8.1 Subagents + Hooks

```yaml
# Subagent 级别的验证
---
name: builder
hooks:
  PostToolUse:
    - matcher: "Write|Edit"
      hooks:
        - type: command
          command: "uv run validator.py"
---

# 项目级别的生命周期
# settings.json
{
  "hooks": {
    "SubagentStart": [
      {
        "matcher": "db-agent",
        "hooks": [
          { "type": "command", "command": "./scripts/setup-db.sh" }
        ]
      }
    ],
    "SubagentStop": [
      {
        "matcher": "db-agent",
        "hooks": [
          { "type": "command", "command": "./scripts/cleanup-db.sh" }
        ]
      }
    ]
  }
}
```

### 8.2 Subagents + Commands

Commands 可以调用 Subagents：

```yaml
## Workflow

1. 分析需求
2. Task 工具调用 Subagent:
   Task({
     subagent_type: "builder",
     prompt: "实现功能...",
     description: "实现认证"
   })
3. 汇总结果
```

### 8.3 Subagents + Skills

```yaml
# 代理中加载 Skills
---
name: research-agent
skills: research-skill, analysis-skill
---

执行任务时使用加载的 skills...
```

---

## 9. 检查清单

### Subagent 开发检查清单

- [ ] 清晰的 `description` 字段
- [ ] 适当的工具限制
- [ ] 合适的工作流步骤
- [ ] 明确的输出格式
- [ ] 必要的 Hooks 配置
- [ ] Skills 预加载（如需要）
- [ ] 版本控制（项目代理）

### 团队协作检查清单

- [ ] Builder 有足够工具但有验证
- [ ] Validator 严格只读
- [ ] 任务有清晰依赖
- [ ] 使用 Task 工具编排
- [ ] 验证失败有明确反馈

---

## 引用文档

| 主题 | 文档 |
|------|------|
| Subagents 官方文档 | [my-claude-docs/subagents/Create custom subagents.md](../subagents/Create%20custom%20subagents.md) |
| Skill 与 Subagent 协作 | [my-claude-docs/skills/SKILL_SUBAGENT_BEST_PRACTICE.md](../skills/SKILL_SUBAGENT_BEST_PRACTICE.md) |
| Hooks 最佳实践 | [my-claude-docs/hooks/Claude Code Hooks 最佳实践.md](../hooks/Claude%20Code%20Hooks%20最佳实践.md) |
| 项目原始文档 | [README.md](../../README.md) |

---

> 文档版本：1.0
> 最后更新：2026-02-15
>
> 基于 Claude Code Hooks Mastery 项目总结
