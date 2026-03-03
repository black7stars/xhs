# Command 目录

本目录包含所有可执行的命令文件，采用三层架构设计。

## 架构说明

```
用户输入 → Command 层 → Agent 层 → Skill 层
```

- **Command 层**: 用户入口，解析参数，路由到 Agent
- **Agent 层**: 工作流控制器，执行完整流程
- **Skill 层**: 原子能力单元，供 Agent 按需调用

## Command 列表

### 核心命令

| 命令文件 | 功能 | Agent |
|---------|------|-------|
| `文生图.md` | 文字生成图片 | image-generation |
| `图生图.md` | 图片生成变体 | image-generation |
| `小红书.md` | 单篇笔记生成 | xiaohongshu-content |
| `小红书批量生成.md` | 批量笔记生成 | xiaohongshu-content |
| `小红书-图片后处理.md` | 图片修复调整 | image-post-process |
| `图片素材迁移.md` | 批量迁移素材 | image-migration |

## 使用方式

所有 Command 统一使用换行输入格式：

```
/命令名
参数1
参数2
参数3...
```

示例：
```
/文生图
6
春季海鲜类，暖色调，俯拍

/小红书
春季菜单焕新
笔记/2026春季/
```

## 依赖关系

- 所有命令都依赖项目根目录 `.env` 文件中的API配置
- 图片相关命令通过 Agent 调用 `skill: food-image-core`
- 小红书命令通过 Agent 调用 `skill: content-review` 和 `skill: prohibited-words`

## 文件格式

所有 Command 文件遵循标准格式：

```markdown
---
description: 命令描述
agent: agent名称
---

[参数解析逻辑]

[执行流程说明]

[使用示例]
```

---

**架构文档**: `ARCHITECTURE.md`
**更新时间**: 2026年3月3日
