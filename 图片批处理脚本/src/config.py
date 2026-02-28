"""
配置文件加载模块
"""
import os
from dotenv import load_dotenv
from pathlib import Path

# 加载.env文件
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(env_path)

# API配置
SILICONFLOW_API_KEY = os.getenv('SILICONFLOW_API_KEY')
SILICONFLOW_BASE_URL = os.getenv('SILICONFLOW_BASE_URL', 'https://api.siliconflow.cn/v1')
MODEL_NAME = os.getenv('MODEL_NAME', 'Pro/moonshotai/Kimi-K2.5')

# 路径配置
SOURCE_DIR = Path(os.getenv('SOURCE_DIR', '/Users/black7stars/workspace/xhs/参考图'))
TARGET_BASE_DIR = Path(os.getenv('TARGET_BASE_DIR', '/Users/black7stars/workspace/xhs/素材库/图片素材库'))

# 处理配置
BATCH_SIZE = int(os.getenv('BATCH_SIZE', '10'))
MAX_RETRIES = int(os.getenv('MAX_RETRIES', '3'))
RETRY_DELAY = int(os.getenv('RETRY_DELAY', '2'))

# 日志配置
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')

# 分类目录映射
CATEGORY_DIRS = {
    '海鲜类': TARGET_BASE_DIR / '海鲜类',
    '肉类': TARGET_BASE_DIR / '肉类',
    '蔬菜类': TARGET_BASE_DIR / '蔬菜类',
    '菌菇类': TARGET_BASE_DIR / '菌菇类',
    '其他': TARGET_BASE_DIR / '其他',
}

# 系统Prompt
SYSTEM_PROMPT = """你是一位专业的美食摄影师和高端Bistro餐厅主厨。

请分析这张菜品图片，并按照以下JSON格式输出分析结果：

{
  "original_filename": "原始文件名如1.jpg",
  "dish_name": {
    "analyzed": "根据图片内容识别的菜品描述",
    "creative": "原创命名（2-8字，符合命名规范）"
  },
  "classification": {
    "primary_ingredient": "海鲜类/肉类/蔬菜类/菌菇类/其他",
    "dish_type": "主菜/甜点/前菜/汤品/小吃",
    "cuisine_style": "融合料理"
  },
  "visual_analysis": {
    "main_colors": ["主色1", "主色2", "点缀色"],
    "composition": "俯拍/45度斜俯拍/平视",
    "food_presentation_style": "摆盘风格描述",
    "season": "春/夏/秋/冬/全年",
    "lighting": "自然光/暖光/冷光"
  },
  "content_description": "菜品详细描述（80-120字）",
  "dish_arrangement": {
    "plate": "盘子选择（材质+形状+尺寸+边沿）",
    "logic": "摆盘逻辑（构图法则+视觉流动方向）",
    "spacing": "间距控制",
    "decoration": "装饰法则（装饰物+数量+分布+效果）",
    "negative_space": "留白艺术（位置+比例+作用）",
    "overall_style": "整体风格（定位+对标+场景）"
  }
}

命名规范要求：
1. 使用季节/颜色/意境/技法元素
2. 示例：绯红蟹肉塔、春涧云耳、琥珀牛尾、炭火牛肋、夏澄鲜虾
3. 禁止使用简单描述，必须有创意和记忆点
4. 符合高端Bistro定位，洋气但不晦涩
5. 字数控制在2-8个字（不含连接词）

分析要求：
1. 仔细观察图片中的食材、摆盘、色彩、光线
2. 基于视觉内容推断菜品类型和风格
3. 提供详细的摆盘6要素说明（盘子选择、摆盘逻辑、间距控制、装饰法则、留白艺术、整体风格）
4. 原创命名必须体现主厨创意和审美
"""
