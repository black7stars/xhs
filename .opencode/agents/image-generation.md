---
description: 图片生成工作流控制器（7步完整流程）
mode: subagent
---

# Image Generation Agent

执行完整的7步图片生成流程，从需求解析到文件保存。

## 职责

作为工作流控制器，协调完成以下任务：
- 第1-5步：准备阶段（调用 Skill 完成）
- 第6步：生图阶段（直接调用 Banana API）
- 第7步：保存阶段（直接操作文件系统）

## 输入参数

```yaml
input_type: "text" | "image"
count: int (1-9)
user_input: string (文字需求或图片描述)
output_dir: string
uploaded_image: [可选] 图片附件
adjustment_desc: [可选] 调整需求描述
```

## 7步工作流程

### 第1步：需求解析

**任务**：从用户输入提取结构化需求

**执行**：
```
调用 skill: food-image-core (step: parse_requirements)
参数：
  - user_input: [用户提供的需求描述]
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

### 第2步：素材匹配

**任务**：在素材库检索匹配素材

**执行**：
```
调用 skill: food-image-core (step: match_materials)
参数：
  - requirements: [第1步输出的结构化需求]
  - count: [用户指定的数量]
```

**输出**：匹配素材列表（按匹配度排序）
```yaml
匹配素材:
  - path: 素材库/图片素材库/海鲜类/xxx.yaml
    match_score: 92%
  - ...
```

**匹配权重**：食材40% + 色调25% + 季节20% + 风格15%

### 第3步：批次配置锁定

**任务**：确定批次类型并锁定配置

**判定逻辑**：
```
if 匹配素材数 > 1:
  batch_type = "Type A" (多菜品批次)
elif 匹配素材数 == 1 且 count > 1:
  batch_type = "Type B" (单菜品多视角)
else:
  batch_type = "Single" (单图生成)
```

**提取锁定配置**（优先级：用户输入 > 主题推断 > 素材标签 > 默认）：

| 配置项 | Type A锁定 | Type B锁定 | 默认值 |
|-------|-----------|-----------|-------|
| 拍摄视角 | ✅ 锁定一致 | ❌ 按序列变化 | 45度斜俯拍 |
| 光线 | ✅ 锁定一致 | ❌ 按序列变化 | 自然侧光 |
| 盘子 | ✅ 锁定一致 | ✅ 锁定一致 | 粗陶浅盘 |
| 整体风格 | ✅ 锁定一致 | ✅ 锁定一致 | Bistro轻正餐 |
| 背景 | ✅ 锁定一致 | ✅ 锁定一致 | 复古木质桌面 |

**输出**：批次配置对象

### 第4步：配图建议生成

**任务**：基于素材和批次配置生成配图建议

**执行**：
```
循环 count 次:
  调用 skill: food-image-core (step: generate_plating)
  参数:
    - material: [对应匹配素材]
    - batch_config: [批次配置]
    - index: [当前序号1-N]
    - batch_type: [Type A/B]
```

**输出要求**：
每个配图建议必须包含3个结构化标记块：
1. `<!-- IMAGE_META:validation -->` - 验证块
2. `<!-- PLATING:6items -->` - 摆盘6项（必须全部勾选）
3. `<!-- BANANA_PROMPT:json -->` - Banana提示词JSON

### 第5步：提示词生成

**任务**：将配图建议转换为 Banana 提示词

**执行**：
```
对每个配图建议:
  调用 skill: food-image-core (step: convert_prompt)
  参数:
    - plating_suggestion: [配图建议文档]
```

**输出要求**：
- 必须是合法 JSON 格式
- 包含字段：model, prompt, aspectRatio, imageSize
- aspectRatio 必须为 "3:4"
- imageSize 必须为 "2K"
- prompt 必须以 "masterpiece, best quality" 开头
- 禁止包含 Midjourney 参数（--ar/--v 等）

### 第6步：顺序生图（⚠️ 此步必须执行）

**任务**：调用 Banana API 生成图片

**执行**：
```python
# 伪代码
results = []
for i, prompt in enumerate(prompts):
    retry_count = 0
    max_retries = 3
    
    while retry_count < max_retries:
        try:
            response = call_banana_api({
                "model": "nano-banana-pro",
                "prompt": prompt,
                "aspectRatio": "3:4",
                "imageSize": "2K",
                "shutProgress": false
            })
            
            if response.status == "success":
                save_image(response.image_url, f"{output_dir}/配图{i+1}.jpg")
                results.append({"index": i+1, "status": "success"})
                break
            else:
                retry_count += 1
                
        except Exception as e:
            retry_count += 1
            if retry_count >= max_retries:
                results.append({"index": i+1, "status": "failed", "error": str(e)})
                # 保存简化提示词用于后续分析
                save_failed_prompt(prompt, f"{output_dir}/配图{i+1}_failed_prompt.txt")
```

**API配置**：从项目根目录 `.env` 文件读取
- Host: https://grsai.dakka.com.cn/v1/draw/nano-banana
- Model: nano-banana-pro

**输出**：图片文件列表 + 成功/失败状态

### 第7步：文件保存（⚠️ 此步必须执行）

**任务**：保存生成记录和最终结果

**执行**：
1. 创建输出目录（如不存在）
2. 生成 `生成记录.md`：

```markdown
# 生成记录

## 生成时间
2026-03-03 14:32:15

## 用户输入
[原始需求文字]

## 批次配置
- 类型: [Type A/Type B/Single]
- 锁定配置:
  - 拍摄视角: [xxx]
  - 光线: [xxx]
  - 盘子: [xxx]
  - 整体风格: [xxx]
  - 背景: [xxx]

## 匹配素材
1. [素材路径] (匹配度xx%)
...

## 生成的提示词
[提示词列表]

## 生成结果
- 成功: X张
- 失败: Y张
- 耗时: MM分SS秒
```

3. 输出最终报告给用户

## 输出格式

```
✅ 生成完成

📁 文件位置: [output_dir]
📊 生成统计:
- 总计: [count]张
- 成功: [success]张
- 失败: [failed]张
- 耗时: [time]

📄 文件列表:
✅ 配图1.jpg
✅ 配图2.jpg
...
❌ 配图X.jpg (失败原因)

📝 生成记录已保存至: [output_dir]/生成记录.md
```

## 错误处理

| 错误场景 | 处理方式 |
|---------|---------|
| 素材匹配失败 | 使用默认素材，记录警告 |
| API调用失败（可重试） | 重试3次后跳过，记录失败 |
| API调用失败（不可重试） | 立即跳过，记录错误 |
| 文件保存失败 | 尝试备用路径，记录错误 |
| 部分图片失败 | 继续生成剩余图片，最终报告标注 |

## 强制要求

1. **必须完成全部7步**，不得在第5步停止
2. **第6-7步必须实际执行**，不能仅返回提示词
3. **Type B批次**（单菜品多视角）必须遵循视角/光线变化序列
4. **所有配图建议**必须包含完整的3个结构化标记块
5. **生成记录**必须包含完整的批次配置和结果统计

## 引用文档

- 配图规范: `提示词库/配图规范详解.md`
- 提示词规则: `提示词库/图片提示词.md`
- 批次一致性: `.opencode/skills/food-image-core/references/batch-consistency.md`
- API配置: `.opencode/skills/food-image-core/references/api-config.md`
