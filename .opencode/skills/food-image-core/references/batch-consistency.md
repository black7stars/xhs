# 批次生图一致性配置

## 批次类型判定

### Type A: 多菜品批次 (Multi-Dish Batch)
- **判定条件**：素材数量 > 1，或用户明确多菜品需求
- **一致性要求**：全部5项锁定
  - camera_angle（拍摄视角）
  - lighting（光线）
  - plate_type（盘子选择）
  - overall_style（整体风格）
  - background（背景）

### Type B: 单菜品多视角 (Single-Dish Multi-View)
- **判定条件**：素材数量 = 1，且生成数量 > 1，或用户使用 `skill: food-image-core` 为单篇笔记配图
- **一致性要求**：锁定3项，释放2项
  - ✅ plate_type（盘子选择）
  - ✅ overall_style（整体风格）
  - ✅ background（背景）
  - ❌ camera_angle（拍摄视角：可变，用于多角度展示）
  - ❌ lighting（光线：可变，用于不同氛围）

## 配置提取优先级

```
用户输入 > 主题推断 > 素材标签 > 默认值
```

### 1. 用户输入（最高优先级）
从用户自然语言输入中提取：
- 视角关键词：俯拍、45度、平视、特写
- 光线关键词：自然光、暖光、冷光、侧光
- 盘子关键词：白盘、粗陶、石板、木盘
- 风格关键词：Bistro、高端西餐、日式
- 背景关键词：木质、大理石、纯色

### 2. 主题推断（次优先级）
根据主题自动推断：
- Bistro主题 → 45度斜俯拍、暖光、粗陶盘、木质背景
- 高端西餐 → 平视、自然光、精致白盘、大理石背景
- 教学/教程 → Type B（单菜品多视角）
- 菜单/清单 → Type A（多菜品批次）

### 3. 素材标签（第三优先级）
从首个匹配素材的YAML标签提取：
- `plating_style` → plate_type
- `lighting` → lighting
- `angle` → camera_angle
- `background` → background

### 4. 默认值（兜底）
- 拍摄视角：45度斜俯拍
- 光线：自然侧光
- 盘子：粗陶浅盘
- 整体风格：Bistro轻正餐
- 背景：复古木质桌面

## 配置锁定时机

在配图建议生成阶段（第3步）锁定，后续所有图片遵循此配置。

### 锁定流程
1. 解析用户输入，提取显式指定的参数
2. 判定批次类型（Type A 或 Type B）
3. 按优先级填充未指定的参数
4. 生成批次配置对象，保存至上下文
5. 所有配图建议必须遵循批次配置

## Type B 多视角变化规则

当批次类型为 Type B（单菜品多视角）时，可变字段按以下顺序变化：

### 拍摄视角变化序列
1. 俯拍（90度）- 整体摆盘展示
2. 45度斜俯拍 - 经典用餐视角
3. 平视 - 强调层次感
4. 特写 - 突出质感细节

### 光线变化序列
1. 自然光 - 真实还原
2. 暖光 - 温馨氛围
3. 侧光 - 强调质感
4. 顶光 - 均匀照明

**说明**：视角和光线按顺序组合，确保每张图呈现不同侧面。

## API层面一致性校验（第5.5步）

### 校验时机
在Banana提示词生成后、API调用前执行（第5.5步）。

### 校验逻辑

#### Type A批次（多菜品）
1. 提取所有配图的Banana提示词JSON
2. 对比以下字段的英文描述：
   - **plate关键词**：`white matte ceramic plate` / `rustic stoneware plate` / `slate plate` 等
   - **background关键词**：`clean wooden table surface` / `marble background` / `white seamless background` 等
   - **style关键词**：`fine dining` / `bistro elegance` / `minimalist` 等
   - **lighting关键词**：`soft window light` / `warm golden light` / `cool crisp light` 等
   - **angle关键词**：`top-down` / `45 degree angle` / `table-level perspective` 等
3. 判定标准：同一批次所有配图的上述关键词必须相同

#### Type B批次（单菜品多视角）
1. 验证锁定字段（plate/background/style）一致性
2. 验证变化字段（angle/lighting）按序列变化
3. 期望序列：
   - 视角：俯拍 → 45度 → 平视 → 特写
   - 光线：自然光 → 暖光 → 侧光 → 顶光

### 自动强制统一机制

**不一致处理流程**：
```
发现不一致 → 提取batch_config锁定值 → 强制覆盖所有配图 → 记录覆盖日志 → 重新验证
```

**强制覆盖规则**：
1. **Type A批次**：任何配图与batch_config不一致 → 自动强制统一为batch_config值
2. **Type B批次**：
   - 锁定字段不一致 → 强制统一为batch_config值
   - 变化字段未按序列 → 自动调整为正确序列
3. **覆盖记录**：记录被覆盖的字段、原值、新值、配图编号

**覆盖日志格式**：
```yaml
consistency_override_log:
  batch_id: "batch_20240304_001"
  timestamp: "2024-03-04T10:30:00Z"
  overrides:
    - dish_index: 2
      field: "background"
      original: "rustic wooden tavern table"
      replaced_with: "clean wooden table surface background, no tavern atmosphere"
      reason: "违反禁止词规则 + 与批次配置不一致"
    - dish_index: 3
      field: "plate_type"
      original: "white round plate"
      replaced_with: "white matte ceramic plate, 26cm diameter"
      reason: "与批次配置不一致"
```

### 一致性哈希验证

为每批次生成一致性指纹，用于快速验证：

```python
# 伪代码示意
def generate_consistency_hash(batch_config, prompts):
    """
    生成批次一致性哈希，用于快速验证
    """
    locked_fields = {
        'plate': batch_config['plate_type'],
        'background': batch_config['background'],
        'style': batch_config['overall_style']
    }
    
    # 对每个提示词提取锁定字段的实际值
    for idx, prompt in enumerate(prompts):
        actual_values = extract_from_prompt(prompt)
        if actual_values != locked_fields:
            # 自动强制统一
            prompt = force_override(prompt, locked_fields)
            log_override(batch_config['batch_id'], idx, actual_values, locked_fields)
    
    return generate_hash(locked_fields)
```

## 引用
- 详细配图规范：`提示词库/配图规范详解.md`
- 提示词转换规则：`提示词库/图片提示词.md`
- API配置：`references/api-config.md`
- 禁止词规则：`SKILL.md` 模块4
