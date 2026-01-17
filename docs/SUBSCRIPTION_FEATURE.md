# 定时任务与报警功能文档

## 功能概述

TrendPulse 现在支持自动化的关键词监控和负面舆情报警功能。

### 核心功能

1. **关键词订阅** - 用户可以订阅需要持续监控的关键词
2. **定时采集** - 系统每 6 小时（可配置）自动采集和分析
3. **智能报警** - 情绪分数低于阈值（默认 30）时自动触发报警
4. **报警历史** - 查看所有历史报警记录

---

## 数据库模型

### Subscription (订阅表)

```python
- id: 订阅ID
- keyword_id: 关键词ID
- platforms: 采集平台 (reddit,youtube,twitter)
- language: 语言 (en/zh)
- post_limit: 每次采集数量
- alert_threshold: 报警阈值 (0-100)
- interval_hours: 检查间隔 (小时)
- is_active: 是否激活
- user_email: 用户邮箱 (用于邮件通知)
- created_at: 创建时间
- last_checked_at: 上次检查时间
- next_check_at: 下次检查时间
```

### Alert (报警表)

```python
- id: 报警ID
- subscription_id: 订阅ID
- keyword_id: 关键词ID
- sentiment_score: 情绪分数
- sentiment_label: 情绪标签
- posts_count: 总帖子数
- negative_posts_count: 负面帖子数
- summary: 报警摘要
- is_sent: 是否已发送通知
- created_at: 创建时间
- acknowledged_at: 确认时间
```

---

## API 端点

### 订阅管理

#### 创建订阅
```http
POST /subscriptions
Content-Type: application/json

{
  "keyword": "iPhone 16 Pro",
  "platforms": ["reddit", "youtube"],
  "language": "en",
  "post_limit": 50,
  "alert_threshold": 30.0,
  "interval_hours": 6,
  "user_email": "user@example.com"  // 可选
}
```

#### 获取所有订阅
```http
GET /subscriptions
```

#### 取消订阅
```http
DELETE /subscriptions/{subscription_id}
```

### 报警管理

#### 获取报警列表
```http
GET /alerts?limit=50&acknowledged=false
```

参数:
- `limit`: 返回数量限制 (默认 50)
- `acknowledged`: 过滤确认状态 (true/false/null)

#### 确认报警
```http
PATCH /alerts/{alert_id}/acknowledge
```

---

## 前端使用

### 1. 订阅管理页面

访问"订阅"标签页，可以：

- **查看订阅列表**: 显示所有活跃订阅
- **创建订阅**: 点击右下角 + 按钮
  - 输入关键词
  - 选择平台 (Reddit/YouTube/Twitter)
  - 设置报警阈值 (0-100)
  - 设置检查间隔 (小时)
  - 设置采集数量
- **取消订阅**: 点击订阅卡片上的删除按钮

### 2. 报警历史

在"订阅"标签页的"报警历史"子标签中：

- **查看所有报警**: 按时间倒序显示
- **筛选报警**:
  - 全部报警
  - 未确认报警 (红色边框高亮)
  - 已确认报警
- **确认报警**: 点击"确认"按钮标记为已处理

### 3. 导航

应用底部有两个导航标签：

- **分析**: 手动分析关键词
- **订阅**: 管理订阅和查看报警

---

## 后端配置

### 1. 安装依赖

```bash
cd backend
pip install -r requirements.txt
```

新增依赖:
- `apscheduler>=3.10.0` - 任务调度

### 2. 启动服务器

```bash
cd backend
python -m src.api.main
```

服务器启动时会自动:
- 初始化数据库表
- 加载所有活跃订阅
- 启动定时任务调度器

### 3. 定时任务工作流程

```
订阅创建 → 加入调度队列 → 定时执行
  ↓
采集数据 → AI分析 → 检查情绪分数
  ↓
分数 < 阈值? → YES → 创建报警 → 发送通知
  ↓                   ↓
 NO                  记录到数据库
  ↓
更新下次检查时间 → 等待下一次执行
```

---

## 报警触发逻辑

```python
# 在 scheduler.py:check_subscription() 中

if result["overall_sentiment"] < subscription.alert_threshold:
    # 触发报警
    negative_posts = [
        p for p in posts
        if p["sentiment_score"] < threshold
    ]

    alert = Alert(
        subscription_id=subscription.id,
        sentiment_score=result["overall_sentiment"],
        negative_posts_count=len(negative_posts),
        summary=result["summary"]
    )
```

### 默认配置

- **报警阈值**: 30 分 (满分 100)
- **检查间隔**: 6 小时
- **采集数量**: 50 条/平台

---

## 通知方式

当前实现:
- ✅ **日志记录**: 所有报警记录到后端日志
- ✅ **数据库存储**: 报警历史保存到数据库
- ✅ **前端展示**: 在订阅页面显示报警列表

未来扩展:
- 📧 **邮件通知**: 发送报警邮件到用户邮箱
- 🔔 **推送通知**: 移动端推送通知
- 💬 **Webhook**: 集成到 Slack/Teams/DingTalk

---

## 示例场景

### 场景 1: 品牌监控

```
订阅关键词: "iPhone 16 Pro"
平台: Reddit, YouTube
阈值: 30 分
间隔: 6 小时

系统每 6 小时自动检查，如果情绪分数低于 30 分，
立即创建报警，通知用户关注负面舆情。
```

### 场景 2: 竞品分析

```
订阅关键词: "Samsung Galaxy S24"
平台: 全平台
阈值: 40 分 (更敏感)
间隔: 3 小时 (更频繁)

更密切监控竞品的负面反馈，及时了解市场动态。
```

---

## 故障排查

### 订阅未自动执行

1. 检查后端日志: `logs/trendpulse.log`
2. 确认服务器正常运行
3. 检查数据库 `subscriptions.next_check_at` 字段
4. 验证 scheduler 已启动: 查看启动日志 "Scheduler initialized"

### 报警未触发

1. 确认情绪分数确实低于阈值
2. 检查 `alert_threshold` 设置
3. 查看后端日志中的报警记录
4. 验证 AI 分析是否成功完成

### 数据库表不存在

首次启动时运行:
```bash
cd backend
python -c "from src.database.operations import DatabaseManager; from src.config import Config; import asyncio; db = DatabaseManager(Config.DATABASE_URL); asyncio.run(db.init_db())"
```

---

## 技术架构

### 后端组件

- **src/database/models.py** - Subscription 和 Alert 数据模型
- **src/scheduler.py** - APScheduler 任务调度器
- **src/api/main.py** - 订阅和报警 API 端点

### 前端组件

- **lib/screens/subscriptions_screen.dart** - 订阅管理页面
- **lib/widgets/alert_history_widget.dart** - 报警历史展示
- **lib/services/api_service.dart** - API 调用方法

---

## 性能优化建议

1. **批量处理**: 如果订阅数量很多，考虑分批执行
2. **异步执行**: 使用 asyncio 并发处理多个订阅
3. **资源限制**: 限制同时运行的采集任务数量
4. **缓存优化**: 缓存 AI 分析结果，避免重复分析

---

## 安全建议

1. **用户认证**: 未来添加多用户支持时需要身份验证
2. **权限控制**: 限制用户只能管理自己的订阅
3. **数据隐私**: 邮箱等敏感信息加密存储
4. **API 限流**: 防止滥用订阅功能

---

## 未来改进方向

- [ ] 支持自定义报警条件（如负面帖子比例）
- [ ] 邮件通知集成（SMTP/API）
- [ ] 移动端推送通知
- [ ] 报警趋势图表
- [ ] 导出报警报告
- [ ] 多用户支持
- [ ] 订阅分组管理
- [ ] 高级调度策略（如避开工作时间）
