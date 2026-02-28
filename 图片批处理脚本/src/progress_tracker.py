"""
进度追踪模块 - 管理批次进度和断点续传
"""
import json
from pathlib import Path
from typing import List, Dict, Set

class ProgressTracker:
    """进度追踪器类"""
    
    def __init__(self, data_dir: Path):
        self.data_dir = data_dir
        self.checkpoint_file = data_dir / 'migration_checkpoint.json'
        self.failed_file = data_dir / 'failed_images.json'
        self.data_dir.mkdir(parents=True, exist_ok=True)
    
    def load_checkpoint(self) -> Dict:
        """加载检查点"""
        if self.checkpoint_file.exists():
            with open(self.checkpoint_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {
            'completed_batches': [],
            'completed_images': [],
            'current_batch': None,
            'total_images': 0,
            'processed_count': 0
        }
    
    def save_checkpoint(self, checkpoint: Dict):
        """保存检查点"""
        with open(self.checkpoint_file, 'w', encoding='utf-8') as f:
            json.dump(checkpoint, f, ensure_ascii=False, indent=2)
    
    def load_failed_images(self) -> List[Dict]:
        """加载失败的图片列表"""
        if self.failed_file.exists():
            with open(self.failed_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return []
    
    def save_failed_images(self, failed_list: List[Dict]):
        """保存失败的图片列表"""
        with open(self.failed_file, 'w', encoding='utf-8') as f:
            json.dump(failed_list, f, ensure_ascii=False, indent=2)
    
    def add_failed_image(self, image_name: str, error: str, batch_num: int):
        """添加失败的图片记录"""
        failed_list = self.load_failed_images()
        failed_list.append({
            'image': image_name,
            'error': error,
            'batch': batch_num,
            'retry_count': 0
        })
        self.save_failed_images(failed_list)
    
    def get_completed_images(self) -> Set[str]:
        """获取已完成处理的图片集合"""
        checkpoint = self.load_checkpoint()
        return set(checkpoint.get('completed_images', []))
    
    def is_batch_completed(self, batch_num: int) -> bool:
        """检查批次是否已完成"""
        checkpoint = self.load_checkpoint()
        return batch_num in checkpoint.get('completed_batches', [])
    
    def mark_image_completed(self, image_name: str):
        """标记图片为已完成"""
        checkpoint = self.load_checkpoint()
        if image_name not in checkpoint['completed_images']:
            checkpoint['completed_images'].append(image_name)
            checkpoint['processed_count'] = len(checkpoint['completed_images'])
            self.save_checkpoint(checkpoint)
    
    def mark_batch_completed(self, batch_num: int):
        """标记批次为已完成"""
        checkpoint = self.load_checkpoint()
        if batch_num not in checkpoint['completed_batches']:
            checkpoint['completed_batches'].append(batch_num)
            self.save_checkpoint(checkpoint)
    
    def set_current_batch(self, batch_num: int, image_list: List[str]):
        """设置当前批次"""
        checkpoint = self.load_checkpoint()
        checkpoint['current_batch'] = {
            'batch_num': batch_num,
            'images': image_list,
            'status': 'processing'
        }
        self.save_checkpoint(checkpoint)
    
    def get_progress_summary(self) -> Dict:
        """获取进度摘要"""
        checkpoint = self.load_checkpoint()
        failed_list = self.load_failed_images()
        
        return {
            'completed_batches': len(checkpoint.get('completed_batches', [])),
            'completed_images': len(checkpoint.get('completed_images', [])),
            'total_images': checkpoint.get('total_images', 0),
            'failed_images': len(failed_list),
            'progress_percentage': (checkpoint.get('processed_count', 0) / checkpoint.get('total_images', 1)) * 100 if checkpoint.get('total_images', 0) > 0 else 0
        }
