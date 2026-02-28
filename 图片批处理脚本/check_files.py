#!/usr/bin/env python3
"""
检查并修复素材库中YAML和图片不匹配的问题
"""
import os
from pathlib import Path
import json

def check_directory(base_dir):
    """检查目录中的YAML和图片匹配情况"""
    results = {
        'yaml_without_image': [],
        'image_without_yaml': [],
        'matched_pairs': [],
        'duplicates': []
    }
    
    # 获取所有YAML文件
    yaml_files = list(base_dir.glob('*.yaml'))
    
    # 获取所有图片文件
    image_files = list(base_dir.glob('*.jpg')) + list(base_dir.glob('*.png')) + list(base_dir.glob('*.jpeg'))
    
    # 提取基础名称（不含扩展名和序号）
    yaml_bases = {}
    for yf in yaml_files:
        base = yf.stem
        # 移除序号后缀如 _001, _002
        import re
        match = re.match(r'(.+)_(\d+)$', base)
        if match:
            base_name = match.group(1)
            seq = match.group(2)
        else:
            base_name = base
            seq = '001'
        
        if base_name not in yaml_bases:
            yaml_bases[base_name] = []
        yaml_bases[base_name].append({'file': yf, 'seq': seq, 'full_base': base})
    
    image_bases = {}
    for img in image_files:
        base = img.stem
        # 移除序号后缀
        import re
        match = re.match(r'(.+)_(\d+)$', base)
        if match:
            base_name = match.group(1)
            seq = match.group(2)
        else:
            base_name = base
            seq = '001'
        
        if base_name not in image_bases:
            image_bases[base_name] = []
        image_bases[base_name].append({'file': img, 'seq': seq, 'full_base': base})
    
    # 找出不匹配的
    for base_name, yaml_list in yaml_bases.items():
        if base_name not in image_bases:
            for item in yaml_list:
                results['yaml_without_image'].append(str(item['file']))
        else:
            # 检查是否每个YAML都有对应的图片
            for yaml_item in yaml_list:
                yaml_base = yaml_item['full_base']
                found = False
                for img_item in image_bases[base_name]:
                    if img_item['full_base'] == yaml_base:
                        found = True
                        results['matched_pairs'].append((yaml_item['file'].name, img_item['file'].name))
                        break
                if not found:
                    results['yaml_without_image'].append(str(yaml_item['file']))
    
    for base_name, img_list in image_bases.items():
        if base_name not in yaml_bases:
            for item in img_list:
                results['image_without_yaml'].append(str(item['file']))
        else:
            # 检查是否每个图片都有对应的YAML
            for img_item in img_list:
                img_base = img_item['full_base']
                found = False
                for yaml_item in yaml_bases[base_name]:
                    if yaml_item['full_base'] == img_base:
                        found = True
                        break
                if not found:
                    results['image_without_yaml'].append(str(img_item['file']))
    
    # 检查重复
    for base_name, yaml_list in yaml_bases.items():
        if len(yaml_list) > 1:
            results['duplicates'].append({
                'type': 'yaml',
                'base_name': base_name,
                'files': [str(item['file']) for item in yaml_list]
            })
    
    for base_name, img_list in image_bases.items():
        if len(img_list) > 1:
            results['duplicates'].append({
                'type': 'image',
                'base_name': base_name,
                'files': [str(item['file']) for item in img_list]
            })
    
    return results

def main():
    base_path = Path('/Users/black7stars/workspace/xhs/素材库/图片素材库')
    categories = ['海鲜类', '肉类', '蔬菜类', '菌菇类', '其他']
    
    all_results = {}
    
    for category in categories:
        cat_path = base_path / category
        if cat_path.exists():
            print(f"\n{'='*60}")
            print(f"检查目录: {category}")
            print('='*60)
            
            results = check_directory(cat_path)
            all_results[category] = results
            
            yaml_count = len(list(cat_path.glob('*.yaml')))
            img_count = len(list(cat_path.glob('*.jpg'))) + len(list(cat_path.glob('*.png'))) + len(list(cat_path.glob('*.jpeg')))
            
            print(f"YAML总数: {yaml_count}")
            print(f"图片总数: {img_count}")
            print(f"匹配对数: {len(results['matched_pairs'])}")
            
            if results['yaml_without_image']:
                print(f"\n⚠️  有YAML无图片 ({len(results['yaml_without_image'])}个):")
                for f in results['yaml_without_image'][:5]:
                    print(f"  - {Path(f).name}")
                if len(results['yaml_without_image']) > 5:
                    print(f"  ... 还有 {len(results['yaml_without_image']) - 5} 个")
            
            if results['image_without_yaml']:
                print(f"\n⚠️  有图片无YAML ({len(results['image_without_yaml'])}个):")
                for f in results['image_without_yaml'][:5]:
                    print(f"  - {Path(f).name}")
                if len(results['image_without_yaml']) > 5:
                    print(f"  ... 还有 {len(results['image_without_yaml']) - 5} 个")
            
            if results['duplicates']:
                print(f"\n⚠️  发现重复 ({len(results['duplicates'])}组):")
                for dup in results['duplicates'][:3]:
                    print(f"  {dup['base_name']}: {len(dup['files'])}个{dup['type']}文件")
            
            if not results['yaml_without_image'] and not results['image_without_yaml'] and not results['duplicates']:
                print("\n✅ 所有文件匹配良好！")
    
    # 保存详细报告
    report_path = Path('/Users/black7stars/workspace/xhs/素材库/图片素材库/check_report.json')
    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump(all_results, f, ensure_ascii=False, indent=2)
    
    print(f"\n\n详细报告已保存: {report_path}")

if __name__ == '__main__':
    main()
