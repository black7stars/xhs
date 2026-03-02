# 更新日志

## [2026-02-28] 生图功能全面重构

### 主要变更

#### 1. API端点修正
- **旧端点**: `https://grsai.dakka.com.cn/v1/draw/nano-banana-pro`
- **新端点**: `https://grsai.dakka.com.cn/v1/draw/nano-banana`
- **说明**: 根据GRS官方API文档，正确的端点不应包含模型名称，模型应在请求体中指定

#### 2. API参数完全重构

**移除的旧参数**:
- `width`, `height` (替换为 `aspectRatio`)
- `steps`, `cfg_scale`, `seed` (新API自动处理)
- `negative_prompt` (新API自动过滤违规内容)

**新增参数**:
- `aspectRatio`: "3:4" (小红书推荐比例)
- `imageSize`: "2K" (高清输出)
- `shutProgress`: false (直接返回结果)

#### 3. 结构化输出强制约束

新增 **3个强制标记块**:
1. `IMAGE_META:validation` - 验证状态标记
2. `PLATING:6items` - 6项摆盘说明强制检查
3. `BANANA_PROMPT:json` - JSON格式提示词块

#### 4. 新增后验检查机制

新建 `image-validator` skill:
- 4步强制检查流程
- 拦截不合规的输出
- 确保配图建议和提示词符合规范

#### 5. 技术操作规范

在 `AGENTS.md` 中新增 EISDIR 错误防范指南:
- 写入前验证路径类型
- 使用 glob 工具避免手动拼接
- "先读再写"原则

### 修改的文件

1. `.opencode/skills/food-image-core/SKILL.md` - 重构API调用层和输出格式
2. `.opencode/skills/food-image-core/references/api-config.md` - 更新API配置说明
3. `.opencode/command/小红书.md` - 更新端点配置
4. `.opencode/command/小红书-图片后处理.md` - 更新端点和参数
5. `AGENTS.md` - 新增技术操作规范

### 新增文件

1. `.opencode/skills/image-validator/SKILL.md` - 后验检查机制

### 已知问题

**生图质量堪忧，计划下次更新修复这一问题。**

当前生图功能虽然能正常调用API，但生成的图片质量可能不稳定。后续计划：
- 优化提示词模板
- 调整API参数组合
- 增加质量评估机制

---

## 历史版本

### [2026-02-13] 初始版本
- 项目基础架构搭建
- 小红书笔记生成功能
- 基础生图功能实现
