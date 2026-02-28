"""
文件管理模块 - 处理文件移动和目录操作
"""
import shutil
from pathlib import Path
from typing import Tuple, Optional

class FileManager:
    """文件管理器类"""
    
    def __init__(self, source_dir: Path, target_base_dir: Path):
        self.source_dir = source_dir
        self.target_base_dir = target_base_dir
        
        # 确保目录存在
        self.source_dir.mkdir(parents=True, exist_ok=True)
        self.target_base_dir.mkdir(parents=True, exist_ok=True)
    
    def get_image_extension(self, filename: str) -> str:
        """获取图片扩展名"""
        ext = Path(filename).suffix.lower()
        if ext in ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp']:
            return ext
        return '.jpg'  # 默认
    
    def move_image_file(self, source_path: Path, target_dir: Path, target_name: str) -> Tuple[bool, Optional[str]]:
        """
        移动图片文件到目标目录
        
        Args:
            source_path: 源文件路径
            target_dir: 目标目录
            target_name: 目标文件名（不含扩展名）
            
        Returns:
            (success, error_message)
        """
        try:
            # 确保目标目录存在
            target_dir.mkdir(parents=True, exist_ok=True)
            
            # 获取扩展名
            extension = self.get_image_extension(source_path.name)
            
            # 构建目标路径
            target_path = target_dir / f"{target_name}{extension}"
            
            # 复制文件（保留源文件作为备份）
            shutil.copy2(source_path, target_path)
            
            return True, None
            
        except Exception as e:
            return False, f"文件移动失败: {str(e)}"
    
    def get_all_images(self) -> list:
        """
        获取源目录中所有图片文件，按文件名数字排序
        
        Returns:
            图片文件路径列表
        """
        image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp'}
        
        images = []
        for file_path in self.source_dir.iterdir():
            if file_path.is_file() and file_path.suffix.lower() in image_extensions:
                images.append(file_path)
        
        # 按文件名数字排序
        def extract_number(filename):
            import re
            match = re.search(r'(\d+)', filename)
            return int(match.group(1)) if match else float('inf')
        
        images.sort(key=lambda x: extract_number(x.name))
        
        return images
    
    def get_batch_images(self, batch_num: int, batch_size: int) -> list:
        """
        获取指定批次的图片
        
        Args:
            batch_num: 批次号（从1开始）
            batch_size: 批次大小
            
        Returns:
            该批次的图片路径列表
        """
        all_images = self.get_all_images()
        
        start_idx = (batch_num - 1) * batch_size
        end_idx = start_idx + batch_size
        
        return all_images[start_idx:end_idx]
