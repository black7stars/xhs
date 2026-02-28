"""
YAML生成模块 - 根据分析结果生成标准YAML文件
"""
import yaml
from pathlib import Path
from typing import Dict, Tuple

class YAMLGenerator:
    """YAML生成器类"""
    
    def generate_yaml_content(self, analysis_result: Dict) -> Dict:
        """根据分析结果生成YAML内容字典"""
        # 提取菜品名称（使用原创命名）
        dish_name = analysis_result['dish_name']['creative']
        
        # 生成分类目录名
        category = analysis_result['classification']['primary_ingredient']
        
        # 构建YAML内容
        yaml_content = {
            'filename': '',  # 将在后续填充
            'path': '',      # 将在后续填充
            'primary_ingredient': category,
            'dish_type': analysis_result['classification']['dish_type'],
            'cuisine_style': analysis_result['classification']['cuisine_style'],
            'main_colors': analysis_result['visual_analysis']['main_colors'],
            'composition': analysis_result['visual_analysis']['composition'],
            'food_presentation_style': analysis_result['visual_analysis']['food_presentation_style'],
            'season': analysis_result['visual_analysis']['season'],
            'lighting': analysis_result['visual_analysis']['lighting'],
            'content_description': analysis_result['content_description'],
            'dish_arrangement': {
                'plate': analysis_result['dish_arrangement']['plate'],
                'logic': analysis_result['dish_arrangement']['logic'],
                'spacing': analysis_result['dish_arrangement']['spacing'],
                'decoration': analysis_result['dish_arrangement']['decoration'],
                'negative_space': analysis_result['dish_arrangement']['negative_space'],
                'overall_style': analysis_result['dish_arrangement']['overall_style']
            }
        }
        
        return yaml_content
    
    def determine_target_path(self, analysis_result: Dict, target_base_dir: Path) -> Tuple[Path, str]:
        """确定目标路径和文件名"""
        # 获取分类
        category = analysis_result['classification']['primary_ingredient']
        
        # 确定目标目录
        category_map = {
            '海鲜类': '海鲜类',
            '肉类': '肉类',
            '蔬菜类': '蔬菜类',
            '菌菇类': '菌菇类',
            '其他': '其他'
        }
        
        target_category = category_map.get(category, '其他')
        target_dir = target_base_dir / target_category
        
        # 生成基础文件名（使用原创命名）
        dish_name = analysis_result['dish_name']['creative']
        base_filename = dish_name
        
        return target_dir, base_filename
    
    def find_available_filename(self, target_dir: Path, base_filename: str, extension: str = '.jpg') -> Tuple[str, int]:
        """查找可用的文件名（处理重名）"""
        # 确保目标目录存在
        target_dir.mkdir(parents=True, exist_ok=True)
        
        # 尝试基础文件名
        candidate = f"{base_filename}_001"
        yaml_file = target_dir / f"{candidate}.yaml"
        img_file = target_dir / f"{candidate}{extension}"
        
        if not yaml_file.exists() and not img_file.exists():
            return candidate, 1
        
        # 查找下一个可用序号
        seq = 2
        while seq <= 999:
            candidate = f"{base_filename}_{seq:03d}"
            yaml_file = target_dir / f"{candidate}.yaml"
            img_file = target_dir / f"{candidate}{extension}"
            
            if not yaml_file.exists() and not img_file.exists():
                return candidate, seq
            seq += 1
        
        # 如果超过999，使用时间戳
        import time
        candidate = f"{base_filename}_{int(time.time())}"
        return candidate, 0
    
    def save_yaml(self, yaml_content: Dict, target_path: Path) -> bool:
        """保存YAML文件"""
        try:
            # 确保目录存在
            target_path.parent.mkdir(parents=True, exist_ok=True)
            
            # 使用自定义的yaml representer来处理多行字符串
            def str_representer(dumper, data):
                if '\n' in data:
                    return dumper.represent_scalar('tag:yaml.org,2002:str', data, style='>')
                return dumper.represent_scalar('tag:yaml.org,2002:str', data)
            
            yaml.add_representer(str, str_representer)
            
            with open(target_path, 'w', encoding='utf-8') as f:
                yaml.dump(yaml_content, f, allow_unicode=True, sort_keys=False, default_flow_style=False)
            
            return True
        except Exception as e:
            print(f"保存YAML失败: {e}")
            return False
