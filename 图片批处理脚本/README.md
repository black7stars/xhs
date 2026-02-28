# 图片批处理脚本

## 功能说明

本脚本用于批量处理菜品图片，包括：
1. 调用SiliconFlow API进行图片内容分析
2. 生成标准化的YAML配置文件
3. 自动分类并迁移图片到目标目录
4. 支持断点续传和进度追踪

## 安装步骤

```bash
# 1. 进入脚本目录
cd 图片批处理脚本

# 2. 激活虚拟环境
source venv/bin/activate

# 3. 安装依赖
pip install -r requirements.txt
```

## 使用方法

### 1. 处理指定批次

```bash
python migrate.py --batch 1
```

### 2. 测试模式（仅处理第1张）

```bash
python migrate.py --batch 1 --test
```

### 3. 从断点继续

```bash
python migrate.py --resume
```

### 4. 查看进度状态

```bash
python migrate.py --status
```

## 批次说明

- 总图片数：147张
- 批次大小：10张/批
- 预计批次数：15批

## 目录结构

```
图片批处理脚本/
├── venv/                  # Python虚拟环境
├── src/                   # 源代码模块
│   ├── config.py         # 配置管理
│   ├── image_analyzer.py # 图片分析
│   ├── yaml_generator.py # YAML生成
│   ├── file_manager.py   # 文件管理
│   └── progress_tracker.py # 进度追踪
├── data/                  # 数据文件
├── logs/                  # 日志文件
├── migrate.py            # 主入口脚本
├── requirements.txt      # Python依赖
└── .env                  # 环境配置
```

## 注意事项

1. **测试模式**：首次运行建议使用 `--batch 1 --test` 测试单张图片
2. **失败重试**：每张图片失败后会重试3次
3. **断点续传**：使用 `--resume` 可以从上次中断处继续
