# Agent Skills 文档目录

本文档提供了 `docs/skills` 目录下三个核心文件的概览，便于后续大模型参考时快速了解每个文件的主要内容。

## 文件概览

### 1. [Agent Skills-Overview.md](Agent%20Skills-Overview.md)
**主要内容：**
- **Agent Skills 概述**：介绍 Agent Skills 是什么，以及它们如何扩展 Claude 的功能
- **使用场景**：说明为什么使用 Skills，包括专业化 Claude、减少重复工作、组合能力等
- **使用方式**：涵盖预构建 Agent Skills 和自定义 Skills 的使用方法
- **工作原理**：详细解释 Skills 的三级加载机制（元数据、指令、资源和代码）
- **架构设计**：Skills 在虚拟机环境中的工作方式，包括渐进式披露机制
- **支持平台**：说明 Skills 在 Claude API、Claude Code、Claude Agent SDK 和 Claude.ai 中的可用性
- **安全考虑**：强调使用可信来源 Skills 的重要性
- **限制和约束**：跨平台可用性、共享范围、运行时环境限制等

**适用场景：** 了解 Agent Skills 的整体概念、架构设计和跨平台支持情况

### 2. [Agent Skills in Claude Code.md](Agent%20Skills%20in%20Claude%20Code.md)
**主要内容：**
- **快速入门**：如何在 Claude Code 中创建第一个 Skill
- **工作原理**：Skills 如何在 Claude Code 中自动触发和执行
- **存储位置**：Skills 的三种存储位置（企业级、个人级、项目级）
- **配置选项**：详细的 SKILL.md 文件结构、元数据字段说明
- **渐进式披露**：如何组织多文件 Skill 结构
- **工具限制**：使用 `allowed-tools` 限制 Skill 可用的工具
- **子代理集成**：Skills 与 subagents 的协作方式
- **分发方式**：如何分享和分发 Skills
- **故障排除**：常见问题的解决方案

**适用场景：** 在 Claude Code 中实际创建、配置和管理 Skills 的详细指南

### 3. [best practices.md](best%20practices.md)
**主要内容：**
- **核心原则**：简洁性、适当的自由度设置、多模型测试
- **Skill 结构**：命名约定、有效的描述编写、渐进式披露模式
- **工作流和反馈循环**：复杂任务的工作流设计、验证循环的实现
- **内容指南**：避免时间敏感信息、使用一致术语
- **常见模式**：模板模式、示例模式、条件工作流模式
- **评估和迭代**：基于评估的开发方法、与 Claude 协作创建 Skills
- **反模式**：需要避免的常见错误
- **高级功能**：包含可执行代码的 Skills 的最佳实践
- **技术说明**：YAML 前置元数据要求、令牌预算管理

**适用场景：** 编写高质量、有效的 Skills 的最佳实践和指导原则

## 使用建议

1. **概念理解**：首先阅读 `Agent Skills-Overview.md` 了解整体概念
2. **实际操作**：参考 `Agent Skills in Claude Code.md` 进行实际的 Skill 创建
3. **质量提升**：使用 `best practices.md` 确保创建的 Skills 高效且易于维护

## 相关资源

- [Equipping agents for the real world with Agent Skills](https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills) - 工程博客
- [Skills cookbook](https://platform.claude.com/cookbook/skills-notebooks-01-skills-introduction) - 完整的 Skills 示例
- [Available Skills](https://docs.claude.com/en/docs/agents-and-tools/agent-skills/overview#available-skills) - 可用的预构建 Skills 列表