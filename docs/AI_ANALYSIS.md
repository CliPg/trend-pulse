# AI 智能分析流程文档

## 目录
- [流程概览](#流程概览)
- [架构设计](#架构设计)
- [详细流程](#详细流程)
  - [1. 情感分析 (Sentiment Analysis)](#1-情感分析-sentiment-analysis)
  - [2. 观点聚类 (Opinion Clustering)](#2-观点聚类-opinion-clustering)
  - [3. 讨论摘要 (Summarization)](#3-讨论摘要-summarization)
- [提示词工程](#提示词工程)
- [Token 优化策略](#token-优化策略)
- [数据流转](#数据流转)

---

## 流程概览

TrendPulse 的 AI 分析流程采用三阶段管道架构：

```
输入数据 (Raw Posts)
    ↓
┌─────────────────────────────────┐
│  1. 情感分析 (Sentiment Analysis)  │
│  - 单条分析 & 批量分析              │
│  - 输出: 0-100 分数 + 标签          │
└─────────────────────────────────┘
    ↓
┌─────────────────────────────────┐
│  2. 观点聚类 (Opinion Clustering) │
│  - 识别主要讨论主题                │
│  - 提取代表性观点                  │
└─────────────────────────────────┘
    ↓
┌─────────────────────────────────┐
│  3. 讨论摘要 (Summarization)      │
│  - 生成人类可读的综合总结           │
└─────────────────────────────────┘
    ↓
输出结果 (Analysis Report)
```

---

## 架构设计

### 核心组件

```python
# src/ai_analysis/pipeline.py
class AnalysisPipeline:
    """完整的 AI 分析管道"""

    def __init__(self):
        self.sentiment_analyzer = SentimentAnalyzer()  # 情感分析器
        self.opinion_clusterer = OpinionClusterer()    # 观点聚类器
        self.summarizer = Summarizer()                 # 摘要生成器

    async def analyze_posts(self, posts: List[Dict]) -> Dict:
        """执行完整分析流程"""
        # 三阶段处理...
```

### LLM 客户端

```python
# src/ai_analysis/client.py
class LLMClient:
    """统一的 LLM API 客户端"""

    def __init__(self, provider: Optional[str] = None):
        """
        支持的提供商:
        - 'openai': OpenAI GPT 模型
        - 'tongyi': 通义千问 (默认)
        """
        self.provider = provider or Config.LLM_PROVIDER
        # 根据 provider 配置 API key 和 base URL
```

---

## 详细流程

### 1. 情感分析 (Sentiment Analysis)

**目标**: 对每个帖子分析情感倾向，输出 0-100 的分数

#### 1.1 单条分析

```python
# src/ai_analysis/sentiment.py:37-100
async def analyze_sentiment(self, text: str) -> Dict:
    """
    分析单个文本的情感

    返回格式:
    {
        "score": 75,           # 0-100 分数
        "label": "positive",   # positive/negative/neutral
        "confidence": 0.85,    # 0-1 置信度
        "reasoning": "..."     # 简短解释
    }
    """
    messages = [
        {"role": "system", "content": self.system_prompt},
        {"role": "user", "content": f"Analyze sentiment: {text}"}
    ]

    response = await self.client.chat_completion(
        messages,
        temperature=0.3  # 低温度保证一致性
    )

    # 解析 JSON 响应，提取结构化数据
    return parse_json_response(response)
```

#### 1.2 批量分析 (Token 优化)

```python
# src/ai_analysis/sentiment.py:102-175
async def analyze_batch(self, texts: List[str]) -> List[Dict]:
    """
    批量分析多个文本，优化 Token 使用

    策略:
    1. 每批处理 10 条文本
    2. 文本截断至 500 字符
    3. 单次 API 调用返回 JSON 数组
    4. 失败时回退到单独分析
    """
    batch_size = 10
    results = []

    for i in range(0, len(texts), batch_size):
        batch = texts[i:i + batch_size]

        # 构建批量提示词
        batch_prompt = f"{self.system_prompt}\n\n"
        batch_prompt += "Analyze these texts and return ONLY a JSON array:\n"
        batch_prompt += "Format: [{\"score\": 0-100, \"label\": \"...\", \"confidence\": 0-1, \"reasoning\": \"...\"}, ...]\n\n"

        for j, text in enumerate(batch, 1):
            truncated_text = text[:500]  # 截断长文本
            batch_prompt += f"{j}. {truncated_text}\n"

        response = await self.client.chat_completion(messages, temperature=0.3)
        batch_results = json.loads(response)
        results.extend(batch_results)

    return results
```

#### 1.3 整体情感计算

```python
# src/ai_analysis/sentiment.py:177-191
def calculate_overall_sentiment(self, sentiment_scores: List[float]) -> float:
    """
    计算整体情感分数

    当前实现: 简单平均
    未来可增强: 按互动量 (点赞/评论) 加权
    """
    if not sentiment_scores:
        return 50.0  # 默认中性

    return sum(sentiment_scores) / len(sentiment_scores)
```

---

### 2. 观点聚类 (Opinion Clustering)

**目标**: 识别讨论中的主要主题和观点，提取 Top 3 聚类

#### 2.1 数据预处理

```python
# src/ai_analysis/clustering.py:48-60
async def cluster_opinions(self, posts: List[Dict], top_n: int = 3) -> List[Dict]:
    """
    聚类观点

    数据预处理:
    1. 过滤短内容 (< 50 字符)
    2. 过滤垃圾内容 (广告、spam)
    3. 采样至 50 条 (控制 Token)
    """
    filtered_posts = [
        p for p in posts
        if len(p.get("content", "")) > 50
        and not self._is_spam(p.get("content", ""))
    ]

    sample_size = min(50, len(filtered_posts))
    sampled_posts = filtered_posts[:sample_size]
```

#### 2.2 聚类提示词设计

```python
# src/ai_analysis/clustering.py:62-84
user_prompt = f"Analyze these {len(sampled_posts)} posts and identify the top {top_n} opinion clusters:\n\n"

for i, post in enumerate(sampled_posts, 1):
    content = post.get("content", "")[:300]  # 截断至 300 字符
    user_prompt += f"\n{i}. {content}"

response = await self.client.chat_completion(messages, temperature=0.5)
result = json.loads(response)

# 返回格式:
# [
#     {
#         "label": "价格讨论",
#         "summary": "用户普遍认为价格偏高，但也有用户认为物有所值",
#         "mention_count": 15,
#         "sample_quotes": ["太贵了", "值得这个价格"]
#     },
#     ...
# ]
```

#### 2.3 垃圾内容检测

```python
# src/ai_analysis/clustering.py:90-111
def _is_spam(self, content: str) -> bool:
    """
    简单垃圾内容检测

    关键词列表:
    - "buy now", "click here"
    - "free trial", "subscribe"
    - "follow me", "link in bio"
    """
    spam_keywords = [
        "buy now", "click here", "free trial",
        "subscribe", "follow me", "check my profile", "link in bio"
    ]

    content_lower = content.lower()
    return any(keyword in content_lower for keyword in spam_keywords)
```

---

### 3. 讨论摘要 (Summarization)

**目标**: 生成 2-3 段人类可读的综合总结

#### 3.1 摘要生成

```python
# src/ai_analysis/summarizer.py:25-70
async def summarize_discussion(self, posts: List[Dict], sentiment_score: float) -> str:
    """
    生成讨论摘要

    策略:
    1. 过滤短内容 (< 50 字符)
    2. 采样至 30 条代表性帖子
    3. 提供整体情感分数作为上下文
    4. 生成自然语言摘要 (避免列表)
    """
    filtered_posts = [p for p in posts if len(p.get("content", "")) > 50]
    sample_size = min(30, len(filtered_posts))
    sampled_posts = filtered_posts[:sample_size]

    sentiment_desc = self._describe_sentiment(sentiment_score)

    user_prompt = f"""Summarize this social media discussion with an overall sentiment of {sentiment_desc} ({sentiment_score:.0f}/100).

Here are {len(sampled_posts)} representative posts:\n"""

    for i, post in enumerate(sampled_posts, 1):
        content = post.get("content", "")[:400]
        user_prompt += f"\n{i}. {content}"

    summary = await self.client.chat_completion(messages, temperature=0.6)
    return summary
```

#### 3.2 情感描述映射

```python
# src/ai_analysis/summarizer.py:72-91
def _describe_sentiment(self, score: float) -> str:
    """
    将情感分数转换为自然语言描述

    分数区间:
    - 80-100: "very positive"
    - 60-79:  "positive"
    - 40-59:  "neutral"
    - 20-39:  "negative"
    - 0-19:   "very negative"
    """
    if score >= 80: return "very positive"
    elif score >= 60: return "positive"
    elif score >= 40: return "neutral"
    elif score >= 20: return "negative"
    else: return "very negative"
```

---

## 提示词工程

### 情感分析提示词

```python
# src/ai_analysis/sentiment.py:15-35
SENTIMENT_SYSTEM_PROMPT = """You are a sentiment analysis expert.
Analyze the sentiment of the given text and respond with ONLY a JSON object in this format:
{
  "score": <0-100 integer>,
  "label": "<positive|negative|neutral>",
  "confidence": <0-1 float>,
  "reasoning": "<brief explanation>"
}

Score guide:
- 0-20: Extremely negative
- 21-40: Negative
- 41-60: Neutral
- 61-80: Positive
- 81-100: Extremely positive

Consider:
- Overall emotional tone
- Specific keywords and phrases
- Context and intent
- Sarcasm and nuance"""
```

### 观点聚类提示词

```python
# src/ai_analysis/clustering.py:15-35
CLUSTERING_SYSTEM_PROMPT = """You are an expert at identifying and clustering opinions.
Analyze the given texts and identify the 3 main themes/opinions being discussed.

Respond with ONLY a JSON object in this format:
{
  "clusters": [
    {
      "label": "<brief theme label>",
      "summary": "<2-3 sentence summary>",
      "mention_count": <number of posts mentioning this>,
      "sample_quotes": ["<representative quote 1>", "<representative quote 2>"]
    }
  ],
  "dominant_sentiment": "<overall positive/negative/neutral>"
}

Focus on:
- Distinct themes and topics
- Points of agreement or controversy
- Common concerns or praise
- Notable trends or patterns"""
```

### 摘要生成提示词

```python
# src/ai_analysis/summarizer.py:15-23
SUMMARIZATION_SYSTEM_PROMPT = """You are an expert at synthesizing social media discussions.
Create a clear, concise summary that captures:
- Main topics being discussed
- Overall sentiment (positive/negative/mixed)
- Key points of consensus or controversy
- Notable trends or patterns

Write in a natural, human-readable style. Avoid lists and bullet points.
Keep the summary to 2-3 paragraphs maximum."""
```

---

## Token 优化策略

### 1. 批量处理

```python
# 情感分析: 10 条/批
batch_size = 10

# 聚类: 采样 50 条
sample_size = min(50, len(filtered_posts))

# 摘要: 采样 30 条
sample_size = min(30, len(filtered_posts))
```

### 2. 文本截断

```python
# 情感分析: 500 字符
truncated_text = text[:500]

# 聚类: 300 字符
content = post.get("content", "")[:300]

# 摘要: 400 字符
content = post.get("content", "")[:400]
```

### 3. 预过滤

```python
# 过滤短内容
if len(content) <= 50:
    continue

# 过滤垃圾内容
if is_spam(content):
    continue
```

### 4. 温度控制

```python
# 情感分析: 低温度 (一致性)
temperature = 0.3

# 聚类: 中等温度 (平衡)
temperature = 0.5

# 摘要: 稍高温度 (创造性)
temperature = 0.6
```

---

## 数据流转

### 输入格式

```python
posts = [
    {
        "content": "I love this product! Best purchase ever.",
        "author": "user123",
        "platform": "reddit",
        "url": "https://...",
        "timestamp": "2025-01-15T10:00:00Z"
    },
    # ... 更多帖子
]
```

### 中间数据

```python
# 情感分析后
posts_with_sentiment = [
    {
        "content": "...",
        "sentiment": {
            "score": 85,
            "label": "positive",
            "confidence": 0.9,
            "reasoning": "Strong positive language"
        }
    },
    # ...
]
```

### 输出格式

```python
result = {
    "sentiment_results": [
        {
            "score": 85,
            "label": "positive",
            "confidence": 0.9,
            "reasoning": "Strong positive language"
        },
        # ...
    ],
    "overall_sentiment": 72.5,  # 平均分数

    "clusters": [
        {
            "label": "产品质量",
            "summary": "用户普遍认为产品质量优秀",
            "mention_count": 25,
            "sample_quotes": ["质量很好", "做工精良"]
        },
        # ... 最多 3 个聚类
    ],

    "summary": "讨论整体呈积极态势，用户普遍赞赏产品质量..."  # 2-3 段文字
}
```

---

## LLM 提供商配置

### 使用 OpenAI

```bash
# .env 文件配置
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-your-openai-key
OPENAI_MODEL=gpt-4o-mini
OPENAI_BASE_URL=https://api.openai.com/v1
```

### 使用通义千问 (默认)

```bash
# .env 文件配置
LLM_PROVIDER=tongyi
TONGYI_API_KEY=your-tongyi-key
TONGYI_MODEL=qwen-plus
TONGYI_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
```

### 代码中指定

```python
# 使用配置文件中的提供商
client = LLMClient()

# 强制使用 OpenAI
client = LLMClient(provider="openai")

# 强制使用通义千问
client = LLMClient(provider="tongyi")
```

---

## 性能指标

### Token 成本估算

假设分析 100 条帖子 (平均 200 字符):

| 阶段 | 输入 Token | 输出 Token | 总计 |
|------|-----------|-----------|------|
| 情感分析 | ~5,000 (10批) | ~2,000 | ~7,000 |
| 观点聚类 | ~4,000 (50条) | ~500 | ~4,500 |
| 讨论摘要 | ~3,000 (30条) | ~300 | ~3,300 |
| **总计** | **~12,000** | **~2,800** | **~14,800** |

### 处理时间

- 单条情感分析: ~1-2 秒
- 批量情感分析 (10条): ~3-5 秒
- 观点聚类: ~5-8 秒
- 讨论摘要: ~3-5 秒
- **完整流程**: ~15-25 秒 (100 条帖子)

---

## 未来优化方向

### 1. 增量分析
- 对新帖子仅分析增量部分
- 复用已有聚类结果

### 2. 缓存机制
- 缓存相似内容的分析结果
- 减少 API 调用次数

### 3. 并行处理
- 情感分析和聚类可并行执行
- 使用 asyncio.gather()

### 4. Map-Reduce 模式
- 对超长文本进行分段处理
- 先分块分析，再汇总结果

### 5. 互动量加权
```python
# 按点赞/评论数加权情感分数
weighted_score = sum(
    s.score * post.engagement_score
    for s, post in zip(sentiments, posts)
) / total_engagement
```

---

## 相关文件

| 文件 | 功能 |
|------|------|
| `src/ai_analysis/client.py` | LLM API 客户端 |
| `src/ai_analysis/pipeline.py` | 分析管道编排 |
| `src/ai_analysis/sentiment.py` | 情感分析模块 |
| `src/ai_analysis/clustering.py` | 观点聚类模块 |
| `src/ai_analysis/summarizer.py` | 摘要生成模块 |
| `src/config.py` | 配置管理 (LLM 提供商选择) |
