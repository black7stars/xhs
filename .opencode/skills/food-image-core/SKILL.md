---
name: food-image-core
description: 图片生成的原子能力集合：需求解析、素材匹配、配图建议生成、提示词转换。供 image-generation agent 在第1-5步调用。
---

# Skill: food-image-core

## 职责定位

本 Skill 提供**原子能力**，供 `image-generation` agent 在 7 步工作流的第 1-5 步调用。

**不执行的工作**：
- ❌ 不控制完整流程（由 Agent 控制）
- ❌ 不调用 Banana API（由 Agent 执行）
- ❌ 不保存文件（由 Agent 执行）

**提供的能力**：
- ✅ 需求解析（第1步）
- ✅ 素材匹配（第2步）
- ✅ 配图建议生成（第4步）
- ✅ 提示词转换（第5步）

## 模块1：需求解析

**调用方式**：
```
skill: food-image-core
step: parse_requirements
参数:
  - user_input: "用户文字描述"
```

**输出**：结构化需求对象
```yaml
食材类型: [海鲜类/肉类/蔬菜类/菌菇类/其他]
色调偏好: [暖色调/冷色调/中性色]
视角要求: [俯拍/45度斜俯拍/平视/特写]
风格定位: [Bistro轻正餐/高端西餐/融合料理]
摆盘要素: [留白比例/装饰复杂度/盘子类型]
场景季节: [春季/夏季/秋季/冬季]
```

**解析规则**：
- 从自然语言提取关键词
- 未明确项使用默认值

## 模块2：素材匹配

**调用方式**：
```
skill: food-image-core
step: match_materials
参数:
  - requirements: [结构化需求对象]
  - count: [需要匹配的素材数量]
```

**输出**：匹配素材列表
```yaml
匹配素材:
  - path: 素材库/图片素材库/[分类]/[菜名]_001.yaml
    match_score: 92%
  - ...
```

**匹配权重**：食材40% + 色调25% + 季节20% + 风格15%

**匹配字段**：
- `primary_ingredient` → 食材类型
- `main_colors` → 色调偏好
- `season` → 场景季节
- `food_presentation_style` → 风格定位

## 模块3：配图建议生成

**调用方式**：
```
skill: food-image-core
step: generate_plating
参数:
  - material: [匹配素材的YAML数据]
  - batch_config: [批次配置对象]
  - index: [当前配图序号]
  - batch_type: [Type A/B]
```

**输出**：配图建议文档

**必须包含3个结构化标记块**：

### IMAGE_META:validation
```markdown
<!-- IMAGE_META:validation -->
配图建议完整性: true/false
提示词格式合规: true/false
素材匹配确认: true/false
<!-- END_IMAGE_META -->
```

### PLATING:6items
```markdown
<!-- PLATING:10items -->
### 菜品呈现维度（6项）
- [ ] 盘子选择: [材质+形状+尺寸+边沿]
- [ ] 摆盘逻辑: [构图法则+视觉流动方向]
- [ ] 间距控制: [X-Ycm+分布特点]
- [ ] 装饰法则: [装饰物+数量+分布+效果]
- [ ] 留白艺术: [位置+比例+作用]
- [ ] 整体风格: [定位+对标+场景]

### 摄影技术维度（2项）
- [ ] 摄影技术: [视角+景深+焦距+构图]
  - 视角: [俯拍90°/45度斜俯拍/平视/特写]
  - 景深: [浅景深f/2.8虚化背景 / 全景深f/8清晰]
  - 焦距: [50mm标准 / 85mm人像 / 100mm微距]
  - 构图: [中心构图 / 三分法 / 对角线 / 黄金分割]
- [ ] 光线控制: [光源+方向+质感+色温]
  - 光源: [自然光/柔光箱/LED面板]
  - 方向: [侧光45°/顶光/逆光]
  - 质感: [硬光强调纹理 / 柔光均匀照明]
  - 色温: [5500K日光 / 3200K暖光]

### 物理环境维度（2项）
- [ ] 背景处理: [类型+材质+禁止元素]
  - 类型: 纯桌子表面（菜单用图专用）
  - 材质: [浅色木质/大理石/混凝土纹理]
  - 禁止元素: [人物/窗户/餐厅环境/其他桌椅/装饰物/文字标识]
  - 保留元素: 仅有桌面表面本身 + 菜品阴影
- [ ] 表面质感: [桌面反光+阴影类型+环境反射]
  - 桌面: [哑光/轻微反光/纹理质感]
  - 阴影: [柔和投影/清晰投影/无投影]
  - 环境反射: [控制反光/无杂乱反射]
<!-- END_PLATING -->
```

**要求**：
- 必须全部勾选 `[x]`
- 间距必须含 cm 数值
- 装饰法则必须含四要素

### BANANA_PROMPT:json
```json
{
  "model": "nano-banana-pro",
  "prompt": "masterpiece, best quality...",
  "aspectRatio": "3:4",
  "imageSize": "2K",
  "shutProgress": false
}
```

**要求**：
- 合法 JSON 格式
- 禁止 Midjourney 参数
- aspectRatio 必须为 "3:4"
- imageSize 必须为 "2K"

## 模块4：提示词转换

**调用方式**：
```
skill: food-image-core
step: convert_prompt
参数:
  - plating_suggestion: [配图建议文档]
```

**输出**：Banana 提示词（JSON）

**转换规则**（参见 `提示词库/图片提示词.md`）：

| 摆盘子项 | 提取关键词 | 提示词转换 |
|---------|-----------|-----------|
| 盘子选择 | 纯白哑光圆形盘/26cm/无边沿 | `white matte ceramic plate, 26cm diameter` |
| 摆盘逻辑 | 黄金分割/对角线流动 | `golden ratio composition, diagonal visual flow` |
| 间距控制 | 2-3cm/群组感 | `2-3cm spacing between elements` |
| 装饰法则 | 旱金莲叶2-3片/错落有致 | `nasturtium leaves 2-3 pieces, organic placement` |
| 留白艺术 | 左侧1/3留白 | `left third negative space, breathing room` |
| 整体风格 | 法式精致感/fine dining | `fine dining food presentation, michelin star` |

### 禁止词映射表（第5步强制执行）

**转换前必须替换以下禁止词**：

| 禁止词 | 强制替换为 | 替换原因 |
|-------|-----------|---------|
| `bistro` | `Modern Chinese fusion restaurant aesthetic (NOT traditional French bistro tavern; reimagined as refined small plates + curated wine selection + urban dining culture, contemporary minimalist interior design)` | AI误解为法式廉价小酒馆 |
| `tavern` | `contemporary dining establishment` | 易生成酒吧氛围 |
| `cozy atmosphere` | `clean minimalist presentation` | 情感模糊词 |
| `restaurant interior` | `clean table surface background` | 避免生成餐厅环境 |
| `dining scene` | `food presentation only` | 避免生成用餐场景 |
| `window` | `neutral background` | 避免生成窗户/临窗 |
| `patrons` / `diners` / `guests` | `[REMOVE]` | 禁止出现食客 |
| `waiter` / `chef` / `staff` | `[REMOVE]` | 禁止出现人物 |

**替换规则**：
1. 生成提示词后立即执行禁止词扫描
2. 发现禁止词 → 立即替换为对应转述词
3. 替换后再次扫描确认无残留
4. 如有无法自动处理的歧义 → 标记待人工确认

### 背景处理规范（菜单用图专用）

**默认背景定义**：纯桌子表面

```yaml
背景处理标准:
  类型: 纯桌子表面背景
  描述: "干净的桌面/台面表面，无任何其他物体或环境元素"
  材质选项:
    - 浅色木质纹理 (light natural wood grain)
    - 大理石纹理 (white/grey marble texture)  
    - 混凝土纹理 (concrete texture)
  禁止元素:
    - 人物（食客/服务员/主厨）
    - 窗户/自然光线来源
    - 其他桌椅/餐厅家具
    - 装饰物（花瓶/餐具/餐巾）
    - 环境氛围（灯光/阴影暗示空间）
    - 品牌标识/文字
  保留元素:
    - 仅有桌面/台面表面本身
    - 自然的桌面纹理（木纹/石纹）
    - 菜品投射的柔和阴影
```

**Banana提示词转换**：

| 配图建议 | Banana提示词 |
|---------|-------------|
| 纯桌子表面背景 | `clean wooden table surface background, no other objects, no environment, no people, no windows, no dining scene, seamless table texture filling entire background, only table surface visible` |
| 禁止人物 | `no people, no human presence, no hands, no figures, no patrons, no diners` |
| 禁止环境 | `no restaurant interior visible, no dining room, no ambient surroundings, no architectural elements` |
| 禁止临窗 | `no window light source, no natural light from window, no outdoor view, no window frame` |
| 禁止其他物体 | `no cutlery, no napkins, no glassware, no decorative items, no tableware except main plate` |

## 引用文档

- 配图规范: `提示词库/配图规范详解.md`
- 提示词规则: `提示词库/图片提示词.md`
- 批次一致性: `references/batch-consistency.md`
- 工作流配置: `/.env` (WORKFLOW_MAX_BATCH_SIZE, WORKFLOW_DEFAULT_COUNT)

## 协作关系

```
image-generation agent
    ├── 第1步 → skill: food-image-core (模块1:需求解析)
    ├── 第2步 → skill: food-image-core (模块2:素材匹配)
    ├── 第3步 → agent 内部逻辑 (批次配置锁定)
    ├── 第4步 → skill: food-image-core (模块3:配图建议)
    ├── 第5步 → skill: food-image-core (模块4:提示词转换)
    ├── 第5.5步 → skill: image-validator (API输入验证)
    ├── 第6步 → agent 直接调用 Banana API
    └── 第7步 → agent 直接保存文件
```

**第5.5步说明**：
- 在Banana提示词生成后、API调用前执行
- 验证内容：禁止词替换、批次一致性、背景规范
- 验证失败 → 拒绝API调用 → 返回修正
- 验证通过 → 允许进入第6步

**分批处理说明**：
- 由于 SiliconFlow Kimi-K2.5 API 限制，单次最多处理 3 张图片
- 如需生成更多，由 Command 层分多次调用 agent
- 本 Skill 保持原子能力，不处理分批逻辑

---

**最后更新**: 2026-03-03
**架构调整**: 明确为原子能力 Skill，不控制流程
