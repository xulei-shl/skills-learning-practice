# Claude Code Commands 最佳实践

> 基于 Claude Code Hooks Mastery 项目的 Commands 实践经验总结

---

## 1. Commands 核心概念

### 1.1 什么是 Commands

Commands（命令）是自定义的 Slash 命令，允许用户通过 `/command-name` 触发预定义的工作流。

### 1.2 Commands 文件位置

| 位置 | 作用域 | 优先级 |
|------|--------|--------|
| `.claude/commands/` | 当前项目 | 高 |
| `~/.claude/commands/` | 全局用户 | 低 |

---

## 2. Command 文件结构

### 2.1 基本结构

```yaml
---
allowed-tools: Bash, Read
description: Load context for new agent session
---

# Command Name

执行以下步骤来...

## Execute
- `git ls-files`

## Read
- README.md
- docs/*.md

## Report
- 提供理解摘要
```

### 2.2 Frontmatter 字段

| 字段 | 必需 | 说明 |
|------|------|------|
| `description` | ✅ | 命令描述，用于帮助信息 |
| `allowed-tools` | ❌ | 限制可用的工具 |
| `disallowed-tools` | ❌ | 禁用的工具 |
| `argument-hint` | ❌ | 参数提示 |
| `model` | ❌ | 指定模型 |
| `hooks` | ❌ | 命令级别的 Hook |

---

## 3. 自验证命令模式

### 3.1 在 Command 中定义 Hooks

Commands 可以嵌入 Hooks，在命令完成后自动验证输出：

```yaml
---
description: Creates a concise engineering implementation plan
hooks:
  Stop:
    - hooks:
        - type: command
          command: >-
            uv run $CLAUDE_PROJECT_DIR/.claude/hooks/validators/validate_new_file.py
            --directory specs
            --extension .md
        - type: command
          command: >-
            uv run $CLAUDE_PROJECT_DIR/.claude/hooks/validators/validate_file_contains.py
            --directory specs
            --contains '## Task Description'
            --contains '## Objective'
---

# Plan With Team

创建详细的实现计划...
```

**关键要点**：
- Hooks 在命令完成后触发
- 验证失败会阻止命令完成
- 适合确保输出符合预期格式

### 3.2 变量系统

Commands 支持变量替换：

```yaml
## Variables

USER_PROMPT: $1                    # 第一个参数
ORCHESTRATION_PROMPT: $2           # 第二个参数
OUTPUT_DIRECTORY: "specs/"         # 常量
TEAM_MEMBERS: ".claude/agents/*"   # 文件模式
```

**使用方式**：
```bash
/plan_w_team "实现用户认证" "使用 builder-validator 模式"
```

---

## 4. 工作流模式

### 4.1 标准工作流结构

```yaml
# Command Name

基于输入执行任务...

## Variables
INPUT: $1

## Workflow

### Step 1: 分析需求
- 理解用户输入
- 确定任务类型

### Step 2: 执行操作
执行具体操作...

### Step 3: 验证结果
- 检查输出
- 如有问题返回 Step 2

## Output Format

```markdown
# 结果标题

## 执行摘要
[简述]

## 详细结果
[详细信息]
```
```

### 4.2 团队协作模式

```yaml
# Team Workflow Command

## Team Tools

**TaskCreate** - 创建任务:
```typescript
TaskCreate({
  subject: "任务名称",
  description: "任务描述",
  activeForm: "进行中显示"
})
```

**TaskUpdate** - 更新任务:
```typescript
TaskUpdate({
  taskId: "1",
  status: "in_progress",
  owner: "builder-api"
})
```

**Task** - 部署代理:
```typescript
Task({
  description: "任务描述",
  prompt: "详细提示",
  subagent_type: "general-purpose"
})
```

---

## 5. 最佳实践示例

### 5.1 简单分析命令

```yaml
---
allowed-tools: Bash, Read
description: Analyze codebase structure and provide summary
---

# Prime

运行以下命令收集项目信息，然后阅读指定文件理解项目目的。

## Execute
- `git ls-files`

## Read
- README.md
- package.json

## Report

提供项目理解摘要，包括：
- 项目类型和目的
- 主要技术栈
- 关键文件结构
```

### 5.2 复杂规划命令

```yaml
---
description: Create detailed implementation plan
argument-hint: [user prompt] [orchestration]
model: opus
disallowed-tools: Task, EnterPlanMode
hooks:
  Stop:
    - hooks:
        - type: command
          command: >-
            uv run $CLAUDE_PROJECT_DIR/.claude/hooks/validators/validate_new_file.py
            --directory specs
            --extension .md
---

# Plan With Team

## Variables

USER_PROMPT: $1
ORCHESTRATION_PROMPT: $2

## Instructions

- 仅规划，不实现
- 分析需求并创建详细计划
- 保存到 specs/ 目录
- 使用团队编排模式

## Plan Format

```md
# Plan: <task>

## Task Description
<描述>

## Objective
<目标>

## Team Members
- Builder: 执行实现
- Validator: 验证完成

## Step by Step Tasks
### 1. <Task>
- Assigned To: builder
- 详细步骤
```
```

---

## 6. 命令参数处理

### 6.1 位置参数

```yaml
## Variables

FIRST_ARG: $1
SECOND_ARG: $2
THIRD_ARG: $3
```

使用：`/command arg1 arg2 arg3`

### 6.2 可选参数

```yaml
## Variables

USER_PROMPT: $1
OPTIONAL_FLAG: $2  # 如果未提供，为空
```

### 6.3 参数验证

```yaml
## Instructions

- 如果未提供 USER_PROMPT，停止并请求提供
- 如果 OPTIONAL_FLAG 为空，使用默认值
```

---

## 7. 输出格式化

### 7.1 模板输出

```yaml
## Output Format

始终使用以下格式：

```markdown
# [标题]

## 执行摘要
[一句概括]

## 详细
- [要点 1]
- [要点 2]

## 结论
[总结]
```
```

### 7.2 条件输出

```yaml
## Output

<if task_type is feature>
## Problem Statement
[问题描述]
</if>

<if complexity is complex>
## Implementation Phases
### Phase 1: 基础
### Phase 2: 核心
### Phase 3: 集成
</if>
```

---

## 8. 与其他组件集成

### 8.1 Commands + Subagents

```yaml
## Workflow

1. 分析需求
2. 使用 Task 工具调用 Subagent:
   Task({
     subagent_type: "builder",
     prompt: "实现功能...",
     description: "实现认证"
   })
3. Subagent 完成工作
4. 汇总结果
```

### 8.2 Commands + Hooks

```yaml
---
hooks:
  Stop:
    - hooks:
        - type: command
          command: "uv run validator.py"
---

命令完成后自动验证...
```

### 8.3 Commands + Skills

Commands 可以使用加载的 Skills：

```yaml
## Workflow

1. 使用 research-skill 进行研究
2. 使用 analysis-skill 分析结果
3. 生成最终报告
```

---

## 9. 检查清单

### Command 开发检查清单

- [ ] 清晰的 description
- [ ] 适当的 allowed-tools 限制
- [ ] 完整的变量定义
- [ ] 清晰的工作流步骤
- [ ] 定义的输出格式
- [ ] 自验证 Hooks（如果需要）
- [ ] 错误处理说明

### Command 最佳实践

- [ ] 使用动词命名：`/plan`, `/build`, `/review`
- [ ] 保持简洁，不超过 500 行
- [ ] 详细但不过度冗长
- [ ] 使用模板确保一致性
- [ ] 验证输出确保质量

---

## 引用文档

| 主题 | 文档 |
|------|------|
| Slash Commands 官方 | [my-claude-docs/Slash commands.md](../Slash%20commands.md) |
| Hooks 最佳实践 | [my-claude-docs/hooks/Claude Code Hooks 最佳实践.md](../hooks/Claude%20Code%20Hooks%20最佳实践.md) |
| Subagents 最佳实践 | [my-claude-docs/subagents/Create custom subagents.md](../subagents/Create%20custom%20subagents.md) |

---

> 文档版本：1.0
> 最后更新：2026-02-15
>
> 基于 Claude Code Hooks Mastery 项目总结
