# 素材库读取优化方案

## 问题描述

在单篇笔记生成过程中，素材库读取失败会直接跳过，虽然不影响主流程，但可能导致内容质量下降（缺少参考素材）。

## 推荐方案：三级重试 + 容错降级机制

### 核心策略

```python
def read_material_library(file_path, max_retries=3):
    """
    读取素材库，带重试和降级机制
    
    策略：
    1. 三级重试（指数退避）
    2. 失败降级（使用默认素材或继续生成）
    3. 日志记录（用于后续优化）
    """
    for attempt in range(max_retries):
        try:
            content = read_file(file_path)
            log(f"✅ 素材库读取成功: {file_path}")
            return content
        except Exception as e:
            if attempt < max_retries - 1:
                wait_time = 2 ** attempt  # 指数退避：2s, 4s, 8s
                log(f"⚠️ 读取失败，{wait_time}秒后重试... (尝试 {attempt+1}/{max_retries}): {e}")
                sleep(wait_time)
            else:
                log(f"❌ 读取素材库失败（已重试{max_retries}次）: {file_path}")
                log(f"   错误信息: {e}")
                
    # 降级处理
    return handle_read_failure(file_path)

def handle_read_failure(file_path):
    """
    读取失败后的降级处理
    """
    # 尝试读取备份文件
    backup_path = file_path.replace('.md', '.backup.md')
    if file_exists(backup_path):
        log(f"🔄 尝试读取备份文件: {backup_path}")
        try:
            return read_file(backup_path)
        except:
            pass
    
    # 使用默认素材模板
    log(f"📄 使用默认素材模板继续生成")
    return get_default_material_template(file_path)

def get_default_material_template(file_path):
    """
    根据素材类型返回默认模板
    """
    if "笔记素材" in file_path:
        return {
            "pain_points": ["菜品研发难", "同质化严重", "出品不稳定"],
            "viewpoints": ["结构比堆砌重要", "标准化是关键"],
            "cases": ["给一家Bistro做菜单升级"]
        }
    elif "菜品素材" in file_path:
        return {
            "dishes": ["春涧云耳", "琥珀牛肋", "绯红桃韵"],
            "techniques": ["低温慢煮", "中西融合", "本土食材国际呈现"]
        }
    else:
        return {}
```

### 优化措施

#### 1. 预防性优化

**A. 缓存预热机制**
```python
# 在生成开始前，预加载所有素材库到内存
def preload_materials():
    """
    预加载素材库到内存缓存
    提前发现文件问题，减少生成过程中的IO等待
    """
    material_cache = {}
    failed_files = []
    
    for file in material_files:
        try:
            material_cache[file] = read_file(file)
            log(f"✅ 预加载成功: {file}")
        except Exception as e:
            failed_files.append((file, str(e)))
            log(f"⚠️ 预加载失败: {file} - {e}")
    
    if failed_files:
        log(f"\n⚠️ 共有 {len(failed_files)} 个素材库文件预加载失败")
        log("将在使用时尝试重试读取\n")
    
    return material_cache, failed_files
```

**B. 文件健康检查**
```python
def validate_material_files():
    """
    定期检查素材库文件完整性
    """
    issues = []
    for file in material_files:
        if not file_exists(file):
            issues.append(f"缺失: {file}")
        elif file_size(file) == 0:
            issues.append(f"空文件: {file}")
        elif not is_readable(file):
            issues.append(f"无法读取: {file}")
    
    if issues:
        log("⚠️ 素材库文件健康检查发现问题：")
        for issue in issues:
            log(f"  - {issue}")
        log("建议及时修复，避免影响内容生成质量")
    
    return issues
```

#### 2. 运行时优化

**A. 异步读取 + 超时控制**
```python
import asyncio

async def read_with_timeout(file_path, timeout=5):
    """
    带超时的异步读取
    防止读取阻塞整个生成流程
    """
    try:
        return await asyncio.wait_for(
            read_file_async(file_path), 
            timeout=timeout
        )
    except asyncio.TimeoutError:
        log(f"⏱️ 读取超时（>{timeout}秒）: {file_path}")
        return None
    except Exception as e:
        log(f"❌ 读取异常: {file_path} - {e}")
        return None
```

**B. 增量备份机制**
```python
def create_material_backup():
    """
    定期创建素材库备份
    主文件损坏时可快速恢复
    """
    for file in material_files:
        backup_file = file.replace('.md', '.backup.md')
        try:
            copy_file(file, backup_file)
            log(f"✅ 备份创建成功: {backup_file}")
        except Exception as e:
            log(f"⚠️ 备份创建失败: {file} - {e}")
```

#### 3. 监控与告警

```python
class MaterialReadMonitor:
    """
    素材库读取监控器
    """
    def __init__(self):
        self.success_count = 0
        self.fail_count = 0
        self.retry_count = 0
        self.fail_details = []
    
    def record_success(self, file_path):
        self.success_count += 1
    
    def record_failure(self, file_path, error, retries):
        self.fail_count += 1
        self.retry_count += retries
        self.fail_details.append({
            'file': file_path,
            'error': str(error),
            'retries': retries,
            'timestamp': datetime.now()
        })
    
    def generate_report(self):
        """
        生成读取统计报告
        """
        total = self.success_count + self.fail_count
        success_rate = (self.success_count / total * 100) if total > 0 else 0
        
        report = f"""
📊 素材库读取统计报告
━━━━━━━━━━━━━━━━━━━━━━
总读取次数: {total}
成功次数: {self.success_count} ({success_rate:.1f}%)
失败次数: {self.fail_count}
总重试次数: {self.retry_count}

失败详情:
"""
        for detail in self.fail_details:
            report += f"  - {detail['file']}: {detail['error']}\n"
        
        return report
```

### 实施建议

#### 阶段1：立即实施（高优先级）
1. ✅ 添加三级重试机制（指数退避）
2. ✅ 实现降级处理（默认素材模板）
3. ✅ 增加读取日志记录

#### 阶段2：短期优化（1周内）
1. 🔄 实现缓存预热机制
2. 🔄 添加文件健康检查
3. 🔄 创建定期备份任务

#### 阶段3：长期完善（1月内）
1. 📊 部署读取监控统计
2. 📊 设置失败告警阈值
3. 📊 建立素材库维护SOP

### 预期效果

| 指标 | 优化前 | 优化后（预期） |
|------|--------|---------------|
| 读取成功率 | ~95% | >99% |
| 失败影响 | 直接跳过 | 降级处理 |
| 问题发现 | 被动发现 | 主动监控 |
| 恢复时间 | 手动修复 | 自动降级 |

### 使用示例

```python
# 在命令文件中集成
@小红书.md 中的素材读取部分:

**读取素材库**
- 尝试读取相关素材库文件
- 失败时自动重试3次（指数退避）
- 仍失败时使用默认素材模板继续生成
- 记录读取日志用于后续优化
```

---

**最后更新**：2026年2月13日
**版本**：v1.0
**状态**：待实施
