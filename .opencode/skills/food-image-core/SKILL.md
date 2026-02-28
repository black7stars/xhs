# Food Image Core Skill

核心生图能力模块，提供完整的菜品图片生成流程。整合Banana API调用、素材匹配、配图建议生成、提示词转换等能力。

## 依赖配置

所有API配置从项目根目录 `.env` 读取：
- Banana API配置（生图）
- SiliconFlow API配置（图片分析）
- 路径配置和默认参数

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

**输出格式**：
```markdown
### 配图X
- **素材**：[素材库路径]
- **菜品名**：[原创命名]
- **核心主体**：[主体物+数量+位置分布]
- **视觉元素清单**：
  - [元素1]：[详细描述]
  - [元素2]：[详细描述]
- **色彩结构**：[主色+辅色+点缀色+氛围]
- **拍摄视角**：[角度描述]
- **光线**：[光源方向+质感]

**摆盘说明（关键）**：
- **盘子选择**：[材质+形状+尺寸]
- **摆盘逻辑**：[构图法则+视觉流动]
- **间距控制**：[间距数值+分布特点]
- **装饰法则**：[装饰物+数量+分布]
- **留白艺术**：[位置+比例+作用]
- **整体风格**：[风格定位+场景契合]
```

### 模块4：提示词转换器

**输入**：配图建议文档
**输出**：Banana模型提示词

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

**标准提示词结构**：
```
[质量标签], [主体描述], [盘子描述], [摆盘逻辑], [间距描述], 
[装饰细节], [留白处理], [视角], [光线], [色调], [风格], [技术参数]
```

### 模块5：API调用层（原banana-image）

**API端点**：`https://grsai.dakka.com.cn/v1/draw/nano-banana-pro`
**模型**：`nano-banana-pro`

**调用参数**：
```json
{
  "prompt": "正向提示词（英文）",
  "negative_prompt": "负向提示词（英文）",
  "width": 1242,
  "height": 1660,
  "steps": 30,
  "cfg_scale": 7.5,
  "seed": -1
}
```

**重试机制**：
```yaml
重试策略:
  最大次数: 3次
  间隔: 5秒
  
参数调整:
  第一次失败:
    cfg_scale: 7.5 → 6.5
    steps: 30 → 35
    
  第二次失败:
    cfg_scale: 6.5 → 6.0
    steps: 35 → 40
    简化提示词: 移除次要细节
    
  第三次失败:
    标记为失败
    保存简化提示词到: [output_path]_待生成.txt
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
