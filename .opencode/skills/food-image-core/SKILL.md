---
name: food-image-core
description: 核心生图能力模块，整合Banana API调用、素材匹配、配图建议生成、提示词转换等能力。供文生图、图生图、小红书等命令调用。
---

# Food Image Core Skill

核心生图能力模块，提供完整的菜品图片生成流程。整合Banana API调用、素材匹配、配图建议生成、提示词转换等能力。

## 依赖配置

所有API配置从项目根目录 `.env` 读取：
- Banana API配置（生图）
- SiliconFlow API配置（图片分析）
- 路径配置和默认参数

## 强制结构化输出格式

所有配图建议和Banana提示词必须包含以下**3个结构化标记块**：

### 1. IMAGE_META:validation 验证块

```markdown
<!-- IMAGE_META:validation -->
配图建议完整性: true/false
提示词格式合规: true/false
素材匹配确认: true/false
<!-- END_IMAGE_META -->
```

**用途**：自我验证状态标记

### 2. PLATING:6items 摆盘检查块

```markdown
<!-- PLATING:6items -->
- [ ] 盘子选择: [材质+形状+尺寸+边沿，如：纯白哑光圆形瓷盘，直径26cm，无边沿]
- [ ] 摆盘逻辑: [构图法则+视觉流动方向，如：黄金分割，右上到左下对角线流动]
- [ ] 间距控制: [X-Ycm+分布特点，如：塔壳间距2-3cm，群组式分布]
- [ ] 装饰法则: [装饰物+数量+分布+效果，如：旱金莲叶每塔2-3片，错落有致，自然生长效果]
- [ ] 留白艺术: [位置+比例+作用，如：左侧1/3留白，形成呼吸空间]
- [ ] 整体风格: [定位+对标+场景，如：法式精致感，fine dining标准，Bistro场景]
<!-- END_PLATING -->
```

**要求**：
- 必须全部勾选 `[x]` 才能继续
- 每项必须有具体内容，不能为"待定"或省略
- 间距必须包含具体cm数值
- 装饰法则必须包含"装饰物+数量+分布+效果"四要素

### 3. BANANA_PROMPT:json 提示词块

```json
<!-- BANANA_PROMPT:json -->
{
  "model": "nano-banana-pro",
  "prompt": "masterpiece, best quality, photorealistic food photography, professional food presentation, modern Chinese 'Bistro' (NOT traditional French tavern; reimagined as: Yunnan/Guizhou/Sichuan fusion plates + biodynamic wine + urban refuge aesthetic), 2k uhd, sharp focus, highly detailed, [主体描述], [盘子描述], [摆盘逻辑], [间距描述], [装饰细节], [留白处理], [视角], [光线], [色调], [风格], editorial food photography",
  "aspectRatio": "3:4",
  "imageSize": "2K",
  "shutProgress": false
}
<!-- END_BANANA_PROMPT -->
```

**强制要求**：
- 必须是**合法JSON格式**（不含Midjourney的`--ar`、`--v`等参数）
- **新API参数**：model, prompt, aspectRatio, imageSize
- aspectRatio 必须为 `3:4`（小红书推荐比例）
- imageSize 必须为 `2K`（高清输出）
- prompt 必须以 `masterpiece, best quality` 开头
- 必须包含完整的摆盘6要素转换
- **禁止出现任何Midjourney参数**

---

## 功能模块

### 模块1：需求解析器

从用户输入提取结构化需求：

```yaml
解析维度:
  - 食材类型: [海鲜类, 肉类, 蔬菜类, 菌菇类, 其他]
  - 色调偏好: [暖色调, 冷色调, 中性色]
  - 视角要求: [俯拍, 45度斜俯拍, 平视, 特写]
  - 风格定位: [Bistro轻正餐, 高端西餐, 融合料理, 日式简约]
  - 摆盘要素: [留白比例, 装饰复杂度, 盘子类型]
  - 场景/季节: [春季, 夏季, 秋季, 冬季]
```

**示例输入输出**：
```
输入：春季海鲜类，暖色调，俯拍，适合Bistro菜单，要有精致摆盘和留白

输出：
- 食材类型: 海鲜类
- 色调偏好: 暖色调
- 视角要求: 俯拍
- 风格定位: Bistro轻正餐
- 摆盘要素: 精致摆盘, 有留白
- 场景/季节: 春季
```

### 模块2：素材匹配器

**输入**：解析后的需求
**输出**：最佳匹配素材列表

**匹配优先级**：
1. 食材类型（权重40%）
2. 色调偏好（权重25%）
3. 场景/季节（权重20%）
4. 摆盘风格（权重15%）

**匹配逻辑**：
```python
def match_materials(requirements, material_yaml_list):
    """
    基于YAML标签匹配素材
    返回：[(material_path, match_score), ...]
    """
    # 读取所有素材库YAML
    # 计算每项与需求的匹配度
    # 按匹配度排序返回
    pass
```

**YAML字段映射**：
```yaml
匹配字段:
  primary_ingredient: → 食材类型
  main_colors: → 色调偏好
  season: → 场景/季节
  food_presentation_style: → 风格定位
  composition: → 视角要求
  dish_arrangement.plate: → 盘子类型
  dish_arrangement.negative_space: → 留白程度
```

### 模块3：配图建议生成器

**输入**：匹配素材的YAML数据
**输出**：标准化配图建议文档

**调用文档**：`提示词库/配图规范详解.md`

**核心要求**：
- 必须包含3个结构化标记块（IMAGE_META/PLATING/BANANA_PROMPT）
- PLATING块6项必须全部勾选并含具体数值
- 间距必须包含cm数值，装饰法则必须含四要素

详细格式规范参见 `提示词库/配图规范详解.md`

### 模块4：提示词转换器

**输入**：配图建议文档（含PLATING「摆盘」块）
**输出**：Banana模型提示词（合法JSON格式）

**调用文档**：`提示词库/图片提示词.md`

**核心要求**：
- 4个必需字段：model, prompt, aspectRatio, imageSize
- model="nano-banana-pro", aspectRatio="3:4", imageSize="2K"
- prompt以"masterpiece, best quality"开头，无中文残留
- 禁止Midjourney参数（--ar/--v等）

详细转换规则和完整示例参见 `提示词库/图片提示词.md`

### 模块5：API调用层

**API端点**：`https://grsai.dakka.com.cn/v1/draw/nano-banana`
**模型**：`nano-banana-pro`

**调用参数**：
```json
{
  "model": "nano-banana-pro",
  "prompt": "masterpiece, best quality...",
  "aspectRatio": "3:4",
  "imageSize": "2K",
  "shutProgress": false
}
```

**重试机制**：
- 最大次数：3次
- 策略：通过简化prompt重试（新API不支持steps/cfg_scale调整）

详细API配置和完整参数说明参见 `references/api-config.md`

### 模块6：图片分析器（复用批处理脚本）

**输入**：用户上传图片
**输出**：YAML标签文件 + 分析结果

**调用API**：SiliconFlow (Kimi-K2.5 Vision)

**分析维度**：
```yaml
必需字段:
  dish_name:
    original: 原始菜名
    creative: 创意命名
  classification:
    primary_ingredient: 主要食材分类
    dish_type: 菜品类型
    cuisine_style: 烹饪风格
  visual_analysis:
    main_colors: [主色调列表]
    composition: 构图方式
    food_presentation_style: 摆盘风格描述
    season: 适用季节
    lighting: 光线类型
  content_description: 菜品内容详细描述
  dish_arrangement:
    plate: 盘子描述
    logic: 摆盘逻辑
    spacing: 间距控制
    decoration: 装饰法则
    negative_space: 留白艺术
    overall_style: 整体风格
```

**自动分类保存**：根据食材类型自动保存至 `素材库/图片素材库/{分类}/`

## 使用方式

### 方式1：完整生图流程（供Command调用）

```markdown
调用 skill: food-image-core
参数:
  input_type: "text" | "image"
  user_input: "用户文字描述" | [上传图片]
  count: 4  # 生成数量
  output_dir: "AI生图/文生图/2026-02-28/"
  
返回:
  status: "success" | "partial" | "failed"
  generated_files: ["配图1.jpg", "配图2.jpg", ...]
  failed_list: [...]
  time_cost: "3分42秒"
```

### 方式2：单模块调用

支持单独调用：素材匹配、配图建议生成、提示词转换、API生图、图片分析

详细调用格式参见各模块说明或 `references/workflow.md`

## 输出格式

### 生图简报

输出包含：文件位置、生成统计（总计/成功/失败/耗时）、文件列表、失败详情（如有）

### 生成记录文件

保存至 `AI生图/[类型]/[日期]/生成记录.md`，包含：生成时间、用户输入、匹配素材、提示词、生成结果

## 与Command的协作关系

```
文生图 Command ──────┐
                    │
图生图 Command ──────┼──→ 调用 food-image-core Skill
                    │
小红书 Command ──────┘
```

## 配置引用

本Skill通过读取项目根目录 `.env` 文件获取配置：
- API密钥和端点
- 路径配置
- 默认参数

无需在Skill文档中硬编码配置。

---

**最后更新**：2026-02-28
**整合模块**：原banana-image Skill + 素材匹配 + 图片分析
