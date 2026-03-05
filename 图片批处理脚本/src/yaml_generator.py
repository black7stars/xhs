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
        
        # 构建YAML内容（10维度配图规范）
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
            # 菜品呈现维度（6项）
            'dish_arrangement': {
                'plate': analysis_result['dish_arrangement']['plate'],
                'logic': analysis_result['dish_arrangement']['logic'],
                'spacing': analysis_result['dish_arrangement']['spacing'],
                'decoration': analysis_result['dish_arrangement']['decoration'],
                'negative_space': analysis_result['dish_arrangement']['negative_space'],
                'overall_style': analysis_result['dish_arrangement']['overall_style']
            },
            # 摄影技术维度（2项）
            'photography': {
                'angle': analysis_result.get('photography', {}).get('angle', '45度斜俯拍'),
                'depth_of_field': analysis_result.get('photography', {}).get('depth_of_field', '浅景深f/2.8'),
                'focal_length': analysis_result.get('photography', {}).get('focal_length', '85mm人像'),
                'composition_rule': analysis_result.get('photography', {}).get('composition_rule', '三分法')
            },
            # 光线控制维度（2项）
            'lighting_control': {
                'source': analysis_result.get('lighting_control', {}).get('source', '自然光'),
                'direction': analysis_result.get('lighting_control', {}).get('direction', '侧光45°'),
                'quality': analysis_result.get('lighting_control', {}).get('quality', '柔和照明'),
                'color_temperature': analysis_result.get('lighting_control', {}).get('color_temperature', '5500K日光')
            },
            # 背景处理维度（菜单用图专用）
            'background': {
                'type': analysis_result.get('background', {}).get('type', '纯桌子表面'),
                'material': analysis_result.get('background', {}).get('material', '浅色木质纹理'),
                'prohibited_elements': analysis_result.get('background', {}).get('prohibited_elements', [
                    '人物', '窗户', '餐厅环境', '其他桌椅', '装饰物', '品牌标识', '文字'
                ]),
                'allowed_elements': analysis_result.get('background', {}).get('allowed_elements', [
                    '桌面表面本身', '菜品投射的柔和阴影'
                ])
            },
            # 表面质感维度
            'surface_texture': {
                'desktop_finish': analysis_result.get('surface_texture', {}).get('desktop_finish', '哑光'),
                'shadow_type': analysis_result.get('surface_texture', {}).get('shadow_type', '柔和投影'),
                'environment_reflection': analysis_result.get('surface_texture', {}).get('environment_reflection', '控制反光')
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
