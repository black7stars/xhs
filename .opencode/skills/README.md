# Skills 技能目录

本目录包含项目使用的各种技能（Skills），用于扩展功能和自动化处理。

## 技能列表

### content-review（内容审查）

**路径**：`content-review/`

**功能**：
- 小红书笔记内容质量审查
- 人设一致性检查
- 结构完整性验证
- 违禁词检测

**使用方式**：
```
skill: content-review
```

**检查项**：
- 人设：8年+ALMA+我
- 结构：4步结构完整（痛点→观点→案例→结尾）
- 痛点：3-5句话展开
- 观点：有具体例子支撑
- 违禁词：无违规

---

### prohibited-words（违禁词检测）

**路径**：`prohibited-words/`

**功能**：
- 自动检测笔记中的违禁词
- 提供风险评级和替代表述
- 支持单篇和批量检测

**使用方式**：
```
skill: prohibited-words
```

**词库位置**：`references/word-library.md`

**检测等级**：
- 高危词：必须修改
- 中危词：建议修改
- 低危词：视场景调整

---

### food-image-core（菜品图片核心处理）

**路径**：`food-image-core/`

**功能**：
- 图片素材匹配
- 配图建议生成（含结构化标记块）
- Banana API 调用（新API格式）
- 图片生成工作流管理

**使用方式**：
被其他命令内部调用，如 `/小红书`、`/文生图`、`/图生图`

**核心流程**：
1. 素材匹配（基于主题、食材、色调）
2. 配图建议生成（含 PLATING:6items 标记块）
3. 提示词转换（转为 Banana 新API格式）
4. **后验检查**（调用 image-validator）
5. API 调用生成图片

**参考文档**：
- `references/workflow.md` - 工作流程说明
- `references/api-config.md` - API 配置说明

**重要更新（2026-03-02）**：
- API端点更新：`/v1/draw/nano-banana`
- 参数更新：使用 `aspectRatio` 和 `imageSize` 替代 width/height
- 新增结构化输出：强制3个标记块约束

---

### image-validator（图片生成后验检查）

**路径**：`image-validator/`

**功能**：
- 对 food-image-core 的输出进行强制质量检查
- 验证配图建议的6项摆盘说明完整性
- 验证Banana提示词的JSON格式合规性
- 拦截不合规输出，确保生图质量

**使用方式**：
在 food-image-core 工作流中自动调用，无需手动执行

**检查流程**：
1. 结构化标记检查（3个标记块）
2. 配图建议完整性检查（6项全部勾选）
3. Banana提示词格式检查（新API参数）
4. 素材引用检查

**添加时间**：2026-03-02

---

## 技能开发规范

1. **目录结构**：
   ```
   skill-name/
   ├── SKILL.md          # 技能主文档（必须）
   ├── references/       # 参考资料
   │   └── xxx.md
   └── scripts/          # 脚本文件（可选）
       └── xxx.py
   ```

2. **文档格式**：
   - 使用 Markdown 格式
   - 包含清晰的功能描述
   - 提供使用示例
   - 说明依赖关系

3. **命名规范**：
   - 目录名：小写，连字符分隔
   - 主文件：SKILL.md
   - 参考资料：references/ 子目录

---

## 添加新技能

如需添加新技能：

1. 在 `skills/` 下创建新目录
2. 编写 `SKILL.md` 主文档
3. 添加必要的参考资料
4. 在主 README 中更新技能列表

---

**更新时间**：2026年3月2日
