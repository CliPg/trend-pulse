# TrendPulse 日志系统

## 概述

TrendPulse 使用统一的日志系统，提供美观的彩色控制台输出和文件日志存储功能。

## 特性

- **彩色控制台输出**: 不同日志级别使用不同颜色，便于快速识别
- **文件日志存储**: 自动按日期轮转日志文件
- **统一格式**: 所有模块使用一致的日志格式
- **模块化**: 为不同模块提供专用的日志函数

## 日志级别和颜色

| 级别 | 颜色 | 说明 |
|------|------|------|
| DEBUG | 蓝色 | 详细的诊断信息 |
| INFO | 绿色 | 一般信息消息 |
| WARNING | 黄色 | 警告消息 |
| ERROR | 红色 | 错误消息 |
| CRITICAL | 红色+粗体 | 严重错误消息 |

## 日志格式

```
[2025-01-16 14:30:45] [INFO     ] [trendpulse.collector.reddit] Searching for posts...
[2025-01-16 14:30:46] [INFO     ] [trendpulse.collector.reddit] Collected 15 posts from Reddit
```

## 使用方法

### 基本使用

```python
from src.utils.logger_config import get_logger

# 获取 logger 实例
logger = get_logger(__name__)

# 记录不同级别的日志
logger.debug("This is a debug message")
logger.info("This is an info message")
logger.warning("This is a warning message")
logger.error("This is an error message")
```

### 模块专用 Logger

系统为不同模块提供了专用的日志函数：

```python
from src.utils.logger_config import (
    get_collector_logger,
    get_ai_logger,
    get_api_logger,
    get_orchestrator_logger,
    get_db_logger,
)

# 数据采集器日志
reddit_logger = get_collector_logger("reddit")
youtube_logger = get_collector_logger("youtube")
twitter_logger = get_collector_logger("twitter")

# AI 分析日志
ai_logger = get_ai_logger()

# API 日志
api_logger = get_api_logger()

# 编排器日志
orchestrator_logger = get_orchestrator_logger()

# 数据库日志
db_logger = get_db_logger()
```

### 自定义配置

如果需要自定义日志配置，可以直接使用 `setup_logger` 函数：

```python
from src.utils.logger_config import setup_logger

logger = setup_logger(
    name="my_module",
    level=logging.INFO,  # 或者 logging.DEBUG, logging.WARNING 等
    log_file="backend/logs/my_module.log",
    console_output=True,
    max_file_size=10 * 1024 * 1024,  # 10 MB
    backup_count=5,
)
```

## 日志文件位置

日志文件存储在 `backend/logs/` 目录下，文件名格式为：
```
backend/logs/trendpulse_YYYYMMDD.log
```

例如：`backend/logs/trendpulse_20250116.log`

日志文件会自动轮转：
- 单个文件最大 10 MB
- 保留最近 5 个备份文件

## 已更新的模块

以下模块已更新为使用统一日志系统：

### 1. AI 分析模块
- `src/ai_analysis/utils/logger.py`
- `src/ai_analysis/sentiment.py`
- `src/ai_analysis/clustering.py`
- `src/ai_analysis/summarizer.py`
- `src/ai_analysis/pipeline.py`
- `src/ai_analysis/client.py`

### 2. 数据采集器
- `src/collectors/reddit.py` - Reddit 爬虫
- `src/collectors/youtube.py` - YouTube 爬虫
- `src/collectors/twitter.py` - Twitter 爬虫

### 3. API 模块
- `src/api/main.py` - FastAPI 应用

### 4. 编排器
- `src/orchestrator.py` - 主编排器

## 测试日志系统

运行测试脚本来查看日志系统的效果：

```bash
cd backend
python test_logging.py
```

这将展示：
- 不同日志级别的颜色效果
- 各模块的日志输出
- 文件日志的创建

## 最佳实践

1. **使用适当的日志级别**:
   - DEBUG: 详细的调试信息（仅用于开发）
   - INFO: 一般信息（程序正常运行时的信息）
   - WARNING: 警告信息（不影响程序运行但需要注意）
   - ERROR: 错误信息（程序运行出错但可以继续）
   - CRITICAL: 严重错误（程序无法继续运行）

2. **包含有用的上下文信息**:
   ```python
   # 不好的写法
   logger.error("Error occurred")

   # 好的写法
   logger.error(f"Failed to fetch transcript for video {video_id}: {error}")
   ```

3. **使用模块专用 logger**:
   ```python
   # 推荐的写法
   from src.utils.logger_config import get_collector_logger
   logger = get_collector_logger("reddit")

   # 或者使用模块名
   logger = get_logger(__name__)
   ```

4. **避免在循环中记录过多日志**:
   ```python
   # 不好的写法
   for item in items:
       logger.info(f"Processing item {item.id}")  # 可能有数千条

   # 好的写法
   logger.info(f"Processing {len(items)} items")
   for i, item in enumerate(items):
       if i % 100 == 0:  # 每 100 条记录一次
           logger.info(f"Progress: {i}/{len(items)}")
   ```

## 故障排查

### 日志文件未创建

如果日志文件未创建，请检查：
1. `backend/logs/` 目录是否存在且有写权限
2. 程序是否有权限创建文件

### 颜色未显示

如果终端未显示颜色：
- Windows: 使用支持 ANSI 颜色的终端（如 Windows Terminal, PowerShell 7+）
- Linux/macOS: 大多数终端都支持 ANSI 颜色

### 日志级别不生效

确保设置了正确的日志级别：
```python
import logging
logger.setLevel(logging.DEBUG)  # 显示所有级别的日志
```

## 迁移指南

如果你的代码还在使用 `print` 语句，可以按以下步骤迁移：

### 之前：
```python
print(f"Processing {len(posts)} posts")
print(f"Error: {error}")
print("Warning: No proxy configured")
```

### 之后：
```python
from src.utils.logger_config import get_logger

logger = get_logger(__name__)
logger.info(f"Processing {len(posts)} posts")
logger.error(f"Error: {error}")
logger.warning("No proxy configured")
```

## 配置文件

日志配置位于 `src/utils/logger_config.py`。

如需修改日志格式、颜色或文件位置，请编辑该文件。

## 相关文件

- `src/utils/logger_config.py` - 日志配置
- `src/ai_analysis/utils/logger.py` - AI 分析日志包装器（支持 token 追踪）
- `backend/test_logging.py` - 日志系统测试脚本
- `backend/logs/` - 日志文件存储目录
