#!/usr/bin/env python3
import os
from pathlib import Path
from collections import defaultdict
import re
import json
from datetime import datetime

def find_files_by_base(directory):
    files_by_base = defaultdict(lambda: {'yaml': [], 'image': []})
    for f in directory.iterdir():
        if f.suffix in ['.yaml', '.jpg', '.png', '.jpeg']:
            stem = f.stem
            match = re.match(r'(.+)_(\d+)$', stem)
            if match:
                base_name = match.group(1)
                seq = int(match.group(2))
            else:
                base_name = stem
                seq = 0
            file_type = 'yaml' if f.suffix == '.yaml' else 'image'
            files_by_base[base_name][file_type].append({'path': f, 'seq': seq, 'mtime': f.stat().st_mtime})
    return files_by_base

def clean_duplicates(directory):
    files_by_base = find_files_by_base(directory)
    deleted = []
    for base_name, files in files_by_base.items():
        if len(files['yaml']) > 1:
            yaml_files = sorted(files['yaml'], key=lambda x: (x['mtime'], x['seq']))
            for f in yaml_files[1:]:
                print(f"删除: {f['path'].name}")
                f['path'].unlink()
                deleted.append(str(f['path']))
        if len(files['image']) > 1:
            img_files = sorted(files['image'], key=lambda x: (x['mtime'], x['seq']))
            for f in img_files[1:]:
                print(f"删除: {f['path'].name}")
                f['path'].unlink()
                deleted.append(str(f['path']))
    return deleted

base_path = Path('/Users/black7stars/workspace/xhs/素材库/图片素材库/肉类')
print(f"清理目录: {base_path}")
deleted = clean_duplicates(base_path)
print(f"\n共删除 {len(deleted)} 个重复文件")
