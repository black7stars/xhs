#!/usr/bin/env python3
"""
图片批处理迁移脚本 - 主入口

功能：
1. 批量分析菜品图片（调用SiliconFlow API）
2. 生成标准YAML文件
3. 自动分类并移动图片到目标目录
4. 支持断点续传和进度追踪

使用方法：
    python migrate.py --batch 1          # 处理第1批（10张）
    python migrate.py --batch 1 --test   # 测试第1批的第1张图片
    python migrate.py --resume           # 从断点继续
    python migrate.py --status           # 查看进度状态

作者：AI Assistant
日期：2026-02-27
"""

import argparse
import sys
import logging
from pathlib import Path
from datetime import datetime

# 添加src目录到路径
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from src.image_analyzer import ImageAnalyzer
from src.yaml_generator import YAMLGenerator
from src.file_manager import FileManager
from src.progress_tracker import ProgressTracker
from src.config import (
    SOURCE_DIR, 
    TARGET_BASE_DIR, 
    BATCH_SIZE,
    LOG_LEVEL
)

# 设置日志
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(f'logs/migration_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log')
    ]
)
logger = logging.getLogger(__name__)


class MigrationRunner:
    """迁移运行器"""
    
    def __init__(self):
        self.analyzer = ImageAnalyzer()
        self.yaml_generator = YAMLGenerator()
        self.file_manager = FileManager(SOURCE_DIR, TARGET_BASE_DIR)
        self.tracker = ProgressTracker(Path(__file__).parent / 'data')
        
    def process_single_image(self, image_path: Path, batch_num: int) -> bool:
        """处理单张图片"""
        filename = image_path.name
        logger.info(f"处理图片: {filename}")
        
        try:
            # 1. 分析图片
            analysis_result, error = self.analyzer.analyze_image(image_path, filename)
            if error:
                logger.error(f"图片分析失败 {filename}: {error}")
                self.tracker.add_failed_image(filename, error, batch_num)
                return False
            
            logger.info(f"分析完成: {analysis_result['dish_name']['creative']}")
            
            # 2. 生成YAML内容
            yaml_content = self.yaml_generator.generate_yaml_content(analysis_result)
            
            # 3. 确定目标路径
            target_dir, base_filename = self.yaml_generator.determine_target_path(
                analysis_result, TARGET_BASE_DIR
            )
            
            # 4. 查找可用文件名
            extension = self.file_manager.get_image_extension(filename)
            available_name, seq_num = self.yaml_generator.find_available_filename(
                target_dir, base_filename, extension
            )
            
            # 5. 更新YAML内容中的文件名和路径
            relative_path = f"素材库/图片素材库/{target_dir.name}/"
            yaml_content['filename'] = f"{available_name}{extension}"
            yaml_content['path'] = relative_path
            
            # 6. 保存YAML文件
            yaml_path = target_dir / f"{available_name}.yaml"
            if not self.yaml_generator.save_yaml(yaml_content, yaml_path):
                logger.error(f"保存YAML失败: {yaml_path}")
                return False
            
            logger.info(f"YAML已保存: {yaml_path}")
            
            # 7. 移动图片文件
            success, error = self.file_manager.move_image_file(
                image_path, target_dir, available_name
            )
            if not success:
                logger.error(f"移动图片失败 {filename}: {error}")
                return False
            
            logger.info(f"图片已移动: {target_dir}/{available_name}{extension}")
            
            # 8. 标记为已完成
            self.tracker.mark_image_completed(filename)
            
            return True
            
        except Exception as e:
            logger.error(f"处理图片 {filename} 时发生异常: {str(e)}")
            self.tracker.add_failed_image(filename, str(e), batch_num)
            return False
    
    def process_batch(self, batch_num: int, test_mode: bool = False) -> dict:
        """处理一个批次"""
        logger.info(f"开始处理第 {batch_num} 批")
        
        # 获取该批次的图片
        batch_images = self.file_manager.get_batch_images(batch_num, BATCH_SIZE)
        
        if not batch_images:
            logger.warning(f"第 {batch_num} 批没有图片")
            return {'success': 0, 'failed': 0, 'total': 0}
        
        # 设置当前批次
        self.tracker.set_current_batch(batch_num, [img.name for img in batch_images])
        
        logger.info(f"本批次共 {len(batch_images)} 张图片")
        
        # 测试模式只处理第1张
        if test_mode:
            batch_images = batch_images[:1]
            logger.info("测试模式：仅处理第1张图片")
        
        # 处理每张图片
        success_count = 0
        failed_count = 0
        
        for idx, image_path in enumerate(batch_images, 1):
            logger.info(f"[{idx}/{len(batch_images)}] 处理: {image_path.name}")
            
            if self.process_single_image(image_path, batch_num):
                success_count += 1
            else:
                failed_count += 1
        
        # 标记批次完成
        if not test_mode:
            self.tracker.mark_batch_completed(batch_num)
        
        result = {
            'success': success_count,
            'failed': failed_count,
            'total': len(batch_images)
        }
        
        logger.info(f"第 {batch_num} 批处理完成: 成功 {success_count}, 失败 {failed_count}")
        
        return result
    
    def show_status(self):
        """显示当前进度状态"""
        summary = self.tracker.get_progress_summary()
        
        print("\n" + "="*60)
        print("图片迁移进度报告")
        print("="*60)
        print(f"已完成批次: {summary['completed_batches']}")
        print(f"已处理图片: {summary['completed_images']}/{summary['total_images']}")
        print(f"失败图片数: {summary['failed_images']}")
        print(f"完成进度: {summary['progress_percentage']:.1f}%")
        print("="*60 + "\n")
        
        # 显示失败的图片
        failed_list = self.tracker.load_failed_images()
        if failed_list:
            print("失败的图片列表:")
            for item in failed_list:
                print(f"  - {item['image']} (批次{item['batch']}): {item['error']}")
            print()


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description='菜品图片批处理迁移工具',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python migrate.py --batch 1              # 处理第1批
  python migrate.py --batch 1 --test       # 测试第1批的第1张
  python migrate.py --resume               # 从断点继续
  python migrate.py --status               # 查看进度
        """
    )
    
    parser.add_argument('--batch', type=int, help='处理指定批次（从1开始）')
    parser.add_argument('--test', action='store_true', help='测试模式：仅处理第1张图片')
    parser.add_argument('--resume', action='store_true', help='从上次中断处继续')
    parser.add_argument('--status', action='store_true', help='显示当前进度状态')
    
    args = parser.parse_args()
    
    # 创建日志目录
    Path('logs').mkdir(exist_ok=True)
    
    runner = MigrationRunner()
    
    if args.status:
        runner.show_status()
        return
    
    if args.resume:
        # 从断点继续
        checkpoint = runner.tracker.load_checkpoint()
        last_batch = max(checkpoint.get('completed_batches', [0]))
        next_batch = last_batch + 1
        logger.info(f"从第 {next_batch} 批继续")
        result = runner.process_batch(next_batch)
    elif args.batch:
        # 处理指定批次
        result = runner.process_batch(args.batch, test_mode=args.test)
    else:
        parser.print_help()
        return
    
    # 显示结果摘要
    print("\n" + "="*60)
    print("批次处理结果")
    print("="*60)
    print(f"成功: {result['success']}")
    print(f"失败: {result['failed']}")
    print(f"总计: {result['total']}")
    print("="*60)
    
    # 显示整体进度
    runner.show_status()


if __name__ == '__main__':
    main()
