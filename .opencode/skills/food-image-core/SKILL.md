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

## 强制结构化输出格式（新增）

为保证输出质量和可验证性，所有配图建议和Banana提示词必须包含以下**3个结构化标记块**：

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
  "prompt": "masterpiece, best quality, photorealistic food photography, professional culinary shot, 8k uhd, sharp focus, highly detailed, [主体描述], [盘子描述], [摆盘逻辑], [间距描述], [装饰细节], [留白处理], [视角], [光线], [色调], [风格], editorial food photography",
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
- **注意**：新API已移除 width/height/steps/cfg_scale/seed/negative_prompt 参数
- **注意**：新API已移除 width/height/steps/cfg_scale/seed/negative_prompt 参数

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
**输出**：标准化配图建议文档（**必须包含结构化标记块**）

**调用文档**：`提示词库/配图规范详解.md`

**输出格式（强制要求）**：

每个配图建议必须包含以下3个标记块：

```markdown
### 配图X - [菜品名]

<!-- IMAGE_META:validation -->
配图建议完整性: true/false
素材匹配确认: true/false
<!-- END_IMAGE_META -->

- **素材**：[素材库路径]
- **菜品名**：[原创命名]
- **核心主体**：[主体物+数量+位置分布]
- **视觉元素清单**：
  - [元素1]：[详细描述]
  - [元素2]：[详细描述]
- **色彩结构**：[主色+辅色+点缀色+氛围]
- **拍摄视角**：[角度描述]
- **光线**：[光源方向+质感]

<!-- PLATING:6items -->
- [ ] 盘子选择: [材质+形状+尺寸+边沿，必须具体到cm]
- [ ] 摆盘逻辑: [构图法则+视觉流动方向]
- [ ] 间距控制: [X-Ycm+分布特点，必须含数值]
- [ ] 装饰法则: [装饰物+数量+分布+效果，四要素齐全]
- [ ] 留白艺术: [位置+X/Y比例+作用]
- [ ] 整体风格: [定位+对标标准+场景契合]
<!-- END_PLATING -->
```

**⚠️ 强制检查点**：
1. PLATING块中的6项必须全部勾选 `[x]` 才能继续
2. 间距控制必须包含具体cm数值（如"2-3cm"）
3. 装饰法则必须包含"装饰物+数量+分布+效果"四要素
4. 留白艺术必须包含具体比例（如"左侧1/3"）
5. 整体风格必须包含对标标准（如"fine dining标准"）

**禁止行为**：
- ❌ 留空或写"待定"
- ❌ 缺少具体数值
- ❌ 6项未全部勾选就继续下一步

---

### 模块3.5：配图建议验证（新增）

在生成配图建议后、转换提示词前，**必须**进行自我验证：

```markdown
**配图建议自检**：
- [ ] 6项摆盘说明全部勾选？
- [ ] 每项都有具体内容（非空）？
- [ ] 间距包含cm数值？
- [ ] 装饰法则包含四要素？
- [ ] 留白包含具体比例？
- [ ] 整体风格包含对标标准？

**自检结果**：全部通过 / 需要补充：[具体项]
```

如果任何一项未通过，**必须**返回补充，不能继续下一步。

### 模块4：提示词转换器

**输入**：配图建议文档（含PLATING块）
**输出**：Banana模型提示词（**必须是合法JSON格式**）

**调用文档**：`提示词库/图片提示词.md`

**转换核心**：摆盘6要素 → 英文关键词

```
摆盘说明子项 → Banana提示词
- 盘子选择 → white matte ceramic plate, 26cm diameter...
- 摆盘逻辑 → golden ratio composition, asymmetric arrangement...
- 间距控制 → 2-3cm spacing between elements...
- 装饰法则 → nasturtium leaves 2-3 pieces per tartlet...
- 留白艺术 → left third negative space, large breathing room...
- 整体风格 → fine dining food presentation, bistro elegance...
```

**⚠️ 强制输出格式（必须严格遵守）**：

```json
<!-- BANANA_PROMPT:json -->
{
  "model": "nano-banana-pro",
  "prompt": "masterpiece, best quality, photorealistic food photography, professional culinary shot, 8k uhd, sharp focus, highly detailed, [主体描述], [盘子描述], [摆盘逻辑], [间距描述], [装饰细节], [留白处理], [视角], [光线], [色调], [风格], editorial food photography",
  "aspectRatio": "3:4",
  "imageSize": "2K",
  "shutProgress": false
}
<!-- END_BANANA_PROMPT -->
```

**🚫 绝对禁止**：
- ❌ Midjourney参数：`--ar`, `--v`, `--q`, `--style`, `--s`, `--c`
- ❌ 非JSON格式（如使用参数标签）
- ❌ 使用旧的API参数：width, height, steps, cfg_scale, seed
- ❌ 缺少质量标签前缀
- ❌ 提示词中包含中文

**✅ 必须包含**：
- [x] 合法的JSON格式
- [x] 4个必需字段：model, prompt, aspectRatio, imageSize
- [x] model="nano-banana-pro"
- [x] aspectRatio="3:4"（小红书推荐）
- [x] imageSize="2K"（高清输出）
- [x] prompt以`masterpiece, best quality`开头
- [x] 摆盘6要素全部转换为英文
- [x] 无中文残留

**注意**：新API已移除 negative_prompt 参数，违规内容过滤由服务端自动处理

**转换自检（生成后必须执行）**：
```markdown
**提示词格式自检**：
- [ ] JSON格式验证通过？
- [ ] 不含Midjourney参数（--ar/--v等）？
- [ ] 不含旧API参数（width/height/steps/cfg_scale/seed）？
- [ ] model="nano-banana-pro"？
- [ ] aspectRatio="3:4"？
- [ ] imageSize="2K"？
- [ ] prompt以masterpiece开头？
- [ ] 6要素全部转换？
- [ ] 无中文残留？

**自检结果**：全部通过 / 需要修正：[具体问题]
```

如果任何一项未通过，**必须**返回修正，不能调用API。

### 模块5：API调用层（原banana-image）

**API端点**：`https://grsai.dakka.com.cn/v1/draw/nano-banana`
**模型**：`nano-banana-pro`

**调用参数（新格式）**：
```json
{
  "model": "nano-banana-pro",
  "prompt": "masterpiece, best quality, photorealistic food photography, [主体描述], [盘子描述], [摆盘逻辑], [装饰细节], [留白处理], [视角], [光线], [色调], [风格]",
  "aspectRatio": "3:4",
  "imageSize": "2K",
  "shutProgress": false
}
```

**参数说明**：
- **model**（必填）：`nano-banana-pro`（保持不变）
- **prompt**（必填）：正向提示词（必须包含质量标签前缀）
- **aspectRatio**（选填）：`3:4`（小红书推荐比例，默认auto）
- **imageSize**（选填）：`2K`（支持1K/2K/4K，默认1K）
- **shutProgress**（选填）：`false`（关闭进度回复，直接返回结果）

**请求头**：
```json
{
  "Content-Type": "application/json",
  "Authorization": "Bearer {api_key}"
}
```

**响应处理**：
```json
{
  "id": "任务ID",
  "results": [
    {
      "url": "https://...",
      "content": "图片描述"
    }
  ],
  "progress": 100,
  "status": "succeeded",
  "failure_reason": "",
  "error": ""
}
```

**重试机制**：
```yaml
重试策略:
  最大次数: 3次
  间隔: 10秒（新API生成时间较长）
  
失败处理:
  第一次失败:
    检查: 提示词长度是否超限
    操作: 简化提示词，移除次要细节
    
  第二次失败:
    检查: 是否包含违规内容
    操作: 进一步简化，保留核心主体描述
    
  第三次失败:
    标记为失败
    保存简化提示词到: [output_path]_待生成.txt
    
注意: 新API不支持steps/cfg_scale调整，只能通过简化prompt重试
```

**错误处理**：
| 错误类型 | 处理方式 |
|---------|---------|
| API超时（>30s） | 重试，超时延长至60s |
| 返回4xx错误 | 检查参数，直接失败 |
| 返回5xx错误 | 重试3次后标记失败 |
| 网络错误 | 重试3次 |
| 配额不足 | 暂停，提示用户充值 |

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

**自动分类保存**：
```python
def save_to_material_library(analysis_result):
    """
    根据分类自动保存到对应目录
    海鲜类/肉类/蔬菜类/菌菇类/其他
    """
    category = analysis_result['classification']['primary_ingredient']
    target_dir = f"素材库/图片素材库/{category}"
    # 生成唯一文件名并保存
```

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

```markdown
# 仅素材匹配
调用 skill: food-image-core
模块: material_matcher
参数:
  requirements: {...}
  
# 仅生成配图建议
调用 skill: food-image-core
模块: suggestion_generator
参数:
  material_yaml: {...}
  
# 仅转换提示词
调用 skill: food-image-core
模块: prompt_converter
参数:
  suggestion: "配图建议文档"
  
# 仅调用API生图
调用 skill: food-image-core
模块: image_generator
参数:
  prompts: ["提示词1", "提示词2"]
  output_dir: "..."
  
# 仅分析图片
调用 skill: food-image-core
模块: image_analyzer
参数:
  image: [上传图片]
  save_to_library: true  # 是否保存到素材库
```

## 输出格式

### 生图简报

```
✅ 生成完成

📁 文件位置：[output_dir]
📊 生成统计：
- 总计：X张
- 成功：Y张
- 失败：Z张
- 耗时：MM分SS秒

📄 文件列表：
✅ 配图1.jpg
✅ 配图2.jpg
❌ 配图3.jpg (失败)
...

[如失败>0]
⚠️ 失败详情：
- 配图3: [错误原因]
  简化提示词已保存至：配图3_待生成.txt
```

### 生成记录文件

保存至 `AI生图/[类型]/[日期]/生成记录.md`：

```markdown
# 生成记录

## 生成时间
2026-02-28 14:32:15

## 用户输入
[原始需求文字或图片信息]

## 匹配素材
1. 素材库/图片素材库/海鲜类/绯焰金鲷_001.yaml (匹配度92%)
2. ...

## 生成的提示词
### 配图1
**正向**：masterpiece, best quality...
**负向**：blurry, low quality...

## 生成结果
- 成功：4张
- 失败：0张
- 耗时：3分42秒
```

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
