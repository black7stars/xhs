# API配置引用

本Skill所有API配置从项目根目录 `.env` 文件读取。

## 配置读取方式

```python
# 伪代码示例
def load_config():
    """从项目根目录.env加载配置"""
    env_path = Path(PROJECT_ROOT) / ".env"
    # 读取配置项
    return config
```

## Banana API配置项

```yaml
BANANA_API_HOST: https://grsai.dakka.com.cn/v1/draw/nano-banana-pro
BANANA_MODEL: nano-banana-pro
BANANA_API_KEY: [从.env读取]
```

## SiliconFlow API配置项

```yaml
SILICONFLOW_BASE_URL: https://api.siliconflow.cn/v1
SILICONFLOW_MODEL: Pro/moonshotai/Kimi-K2.5
SILICONFLOW_API_KEY: [从.env读取]
```

## 路径配置

```yaml
PROJECT_ROOT: /Users/black7stars/workspace/xhs
MATERIAL_BASE_DIR: 素材库/图片素材库
AI_IMAGE_OUTPUT_DIR: AI生图
NOTES_OUTPUT_DIR: 笔记
```

## 生图参数配置

```yaml
DEFAULT_IMAGE_COUNT: 4
DEFAULT_WIDTH: 1242
DEFAULT_HEIGHT: 1660
DEFAULT_STEPS: 30
DEFAULT_CFG: 7.5
```

## 重试配置

```yaml
MAX_RETRIES: 3
RETRY_DELAY: 2
```

---

**注意**：所有配置均从 `.env` 读取，不在本文件中硬编码敏感信息。
