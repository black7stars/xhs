"""
图片分析模块 - 调用SiliconFlow API进行菜品图片分析
"""
import base64
import json
import time
from pathlib import Path
from typing import Dict, Optional, Tuple
from openai import OpenAI
from .config import (
    SILICONFLOW_API_KEY, 
    SILICONFLOW_BASE_URL, 
    MODEL_NAME, 
    MAX_RETRIES, 
    RETRY_DELAY,
    SYSTEM_PROMPT
)

class ImageAnalyzer:
    """图片分析器类"""
    
    def __init__(self):
        self.client = OpenAI(
            api_key=SILICONFLOW_API_KEY,
            base_url=SILICONFLOW_BASE_URL
        )
    
    def encode_image(self, image_path: Path) -> str:
        """将图片转为base64编码"""
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')
    
    def analyze_image(self, image_path: Path, filename: str) -> Tuple[Optional[Dict], Optional[str]]:
        """
        分析单张图片
        
        Args:
            image_path: 图片完整路径
            filename: 原始文件名
            
        Returns:
            (analysis_result, error_message)
            成功时analysis_result为分析结果字典，error_message为None
            失败时analysis_result为None，error_message为错误信息
        """
        # 编码图片
        try:
            base64_image = self.encode_image(image_path)
        except Exception as e:
            return None, f"图片编码失败: {str(e)}"
        
        # 构建消息
        messages = [
            {
                "role": "system",
                "content": SYSTEM_PROMPT
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": f"请分析这张菜品图片。原始文件名：{filename}"
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{base64_image}"
                        }
                    }
                ]
            }
        ]
        
        # 重试机制
        last_error = None
        for attempt in range(MAX_RETRIES):
            try:
                response = self.client.chat.completions.create(
                    model=MODEL_NAME,
                    messages=messages,
                    max_tokens=2000,
                    temperature=0.7
                )
                
                # 解析响应
                content = response.choices[0].message.content
                
                # 提取JSON部分
                try:
                    # 尝试直接解析
                    result = json.loads(content)
                except json.JSONDecodeError:
                    # 尝试从文本中提取JSON
                    import re
                    json_match = re.search(r'\{.*\}', content, re.DOTALL)
                    if json_match:
                        result = json.loads(json_match.group())
                    else:
                        raise ValueError("无法从响应中提取JSON")
                
                # 验证必要字段
                required_fields = ['dish_name', 'classification', 'visual_analysis', 'dish_arrangement']
                for field in required_fields:
                    if field not in result:
                        raise ValueError(f"缺少必要字段: {field}")
                
                # 添加原始文件名
                result['original_filename'] = filename
                
                return result, None
                
            except Exception as e:
                last_error = str(e)
                if attempt < MAX_RETRIES - 1:
                    time.sleep(RETRY_DELAY)
                    continue
                else:
                    break
        
        return None, f"API调用失败（重试{MAX_RETRIES}次）: {last_error}"
