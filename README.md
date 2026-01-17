# TrendPulse 舆情脉冲

A social media sentiment analysis application that automatically scrapes and analyzes public opinion from Reddit, YouTube, and X/Twitter using AI.

## Features

- **Multi-Platform Data Collection**: Reddit, YouTube, X/Twitter
- **AI-Powered Analysis**:
  - Sentiment scoring (0-100 scale)
  - Opinion clustering (identifies 3 main discussion points)
  - Summarization (human-readable overview)
- **Flutter Dashboard**: Beautiful visualization of sentiment trends and opinions

## Architecture

```
┌─────────────┐
│   Flutter   │  Frontend Dashboard
│   Frontend  │
└──────┬──────┘
       │ HTTP API
       │
┌──────▼──────────────────────────────┐
│         FastAPI Backend             │
│  ┌────────────────────────────────┐ │
│  │     TrendPulseOrchestrator     │ │
│  └────────────────────────────────┘ │
│           │         │               │
│  ┌────────▼────┐  ┌▼──────────┐   │
│  │  Collectors │  │    AI     │   │
│  │  - Reddit  │  │ Analysis  │   │
│  │  - YouTube │  │           │   │
│  │  - Twitter │  │           │   │
│  └────────┬────┘  └───────────┘   │
│           │                         │
│  ┌────────▼────┐                   │
│  │  Database   │                   │
│  │   (SQLite)  │                   │
│  └─────────────┘                   │
└────────────────────────────────────┘
```

## Tech Stack

### Backend (Python)
- **Framework**: FastAPI, asyncio/aiohttp
- **Data Collection**: PRAW (Reddit), youtube-transcript-api (YouTube), Playwright (X/Twitter)
- **Database**: SQLAlchemy with aiosqlite
- **AI**: Tongyi Qianwen (Alibaba Qwen) , OpenAI

### Frontend (Flutter)
- **Framework**: Flutter 3.x
- **Visualization**: fl_chart
- **State Management**: Provider

## Setup Instructions

### Prerequisites

- Python 3.13
- Flutter 3.x
- Reddit API credentials
- YouTube Data API key
- Tongyi Qianwen API key (from [Alibaba DashScope](https://dashscope.aliyun.com/))

### Backend Setup

1. **Clone and navigate to backend**:
   ```bash
   cd backend
   ```

2. **Create virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   playwright install chromium
   ```

4. **Configure environment variables**:
   ```bash
   cp .env.example .env
   # Edit .env with your API keys
   ```

5. **Run the API server**:
   ```bash
   python -m src.api.main
   ```

The API will be available at `http://localhost:8000`

### Frontend Setup

1. **Navigate to frontend**:
   ```bash
   cd frontend
   ```

2. **Install dependencies**:
   ```bash
   flutter pub get
   ```

3. **Run the app**:
   ```bash
   flutter run
   ```

## API Documentation

The TrendPulse API provides REST endpoints for sentiment analysis. The base URL is `http://localhost:8000`.

### Health Check Endpoints

#### GET /
Root endpoint for API health check.

**Response**:
```json
{
  "status": "healthy",
  "service": "TrendPulse API",
  "version": "1.0.0"
}
```

#### GET /health
Health check endpoint.

**Response**:
```json
{
  "status": "ok"
}
```

---

### POST /analyze
Analyzes sentiment for a keyword across social media platforms.

**Note**: This operation can take 30-60 seconds depending on the number of platforms and the limit_per_platform setting.

**Request Body**:

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| keyword | string | Yes | - | Keyword to analyze (e.g., "DeepSeek", "ChatGPT") |
| language | string | No | "en" | Language code: "en" (English) or "zh" (Chinese) |
| platforms | array | No | null | Platforms to scrape: ["reddit", "youtube", "twitter"] |
| limit_per_platform | integer | No | 20 | Maximum number of posts to collect per platform |

**Example Request**:
```json
{
  "keyword": "DeepSeek",
  "language": "en",
  "platforms": ["reddit", "youtube", "twitter"],
  "limit_per_platform": 50
}
```

**Response (200 OK)**:

| Field | Type | Description |
|-------|------|-------------|
| keyword | string | The analyzed keyword |
| status | string | Analysis status: "success" or "failed" |
| posts_count | integer | Total number of posts collected |
| overall_sentiment | float | Sentiment score (0-100: 0=very negative, 100=very positive) |
| sentiment_label | string | Human-readable sentiment: "positive", "neutral", or "negative" |
| summary | string | AI-generated summary of discussions |
| opinion_clusters | array | Top 3 opinion clusters with labels and summaries |
| posts | array | List of analyzed posts with sentiment scores |

**Example Response**:
```json
{
  "keyword": "DeepSeek",
  "status": "success",
  "posts_count": 85,
  "overall_sentiment": 72.5,
  "sentiment_label": "positive",
  "summary": "Users are generally excited about DeepSeek's coding capabilities and performance. Many praise its ability to handle complex programming tasks, though some mention occasional API latency issues.",
  "opinion_clusters": [
    {
      "label": "Code Quality",
      "summary": "Users praise the code capabilities and accuracy",
      "mention_count": 32
    },
    {
      "label": "Performance",
      "summary": "Discussions about speed and efficiency",
      "mention_count": 28
    },
    {
      "label": "API Issues",
      "summary": "Reports of latency and rate limiting",
      "mention_count": 15
    }
  ],
  "posts": [
    {
      "platform": "reddit",
      "author": "user123",
      "content": "DeepSeek is amazing for coding tasks!",
      "url": "https://reddit.com/r/programming/comments/...",
      "sentiment_score": 85.0,
      "sentiment_label": "positive",
      "upvotes": 150,
      "likes": null,
      "shares": null,
      "comments_count": 42
    }
  ]
}
```

**Error Responses**:

- **400 Bad Request**: Invalid input or analysis failed
  ```json
  {
    "detail": "No posts collected for the given keyword"
  }
  ```

- **500 Internal Server Error**: Unexpected server error
  ```json
  {
    "detail": "Error message details"
  }
  ```

---

### GET /keywords
Lists all analyzed keywords from the database.

**Response (200 OK)**:

| Field | Type | Description |
|-------|------|-------------|
| keywords | array | List of keyword summaries |
| keywords[].id | integer | Unique keyword ID |
| keywords[].keyword | string | The keyword text |
| keywords[].language | string | Language code |
| keywords[].overall_sentiment | float | Sentiment score (0-100) |
| keywords[].last_analyzed | string | ISO timestamp of last analysis (null if never) |

**Example Response**:
```json
{
  "keywords": [
    {
      "id": 1,
      "keyword": "DeepSeek",
      "language": "en",
      "overall_sentiment": 72.5,
      "last_analyzed": "2026-01-17T10:30:00"
    },
    {
      "id": 2,
      "keyword": "ChatGPT",
      "language": "en",
      "overall_sentiment": 68.2,
      "last_analyzed": "2026-01-16T15:45:00"
    }
  ]
}
```

---

### GET /keywords/{keyword_id}
Retrieves detailed analysis for a specific keyword by ID.

**Path Parameters**:

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| keyword_id | integer | Yes | The ID of the keyword (obtained from GET /keywords) |

**Response (200 OK)**:

| Field | Type | Description |
|-------|------|-------------|
| id | integer | Keyword ID |
| keyword | string | The keyword text |
| language | string | Language code |
| overall_sentiment | float | Sentiment score (0-100) |
| summary | string | AI-generated summary |
| last_analyzed | string | ISO timestamp of last analysis |
| posts_count | integer | Total number of posts |
| opinion_clusters | array | Opinion clusters (max 3) |
| opinion_clusters[].label | string | Cluster label |
| opinion_clusters[].summary | string | Cluster summary |
| opinion_clusters[].mention_count | integer | Number of mentions |
| posts | array | List of posts (max 50, most recent first) |
| posts[].platform | string | Source platform |
| posts[].author | string | Post author |
| posts[].content | string | Post content |
| posts[].url | string | Source URL |
| posts[].sentiment_score | float | Sentiment score (0-100) |
| posts[].sentiment_label | string | Sentiment category |
| posts[].upvotes | integer/null | Upvotes (Reddit) |
| posts[].likes | integer/null | Likes (YouTube/Twitter) |
| posts[].shares | integer/null | Shares (YouTube/Twitter) |
| posts[].comments_count | integer/null | Number of comments |

**Example Response**:
```json
{
  "id": 1,
  "keyword": "DeepSeek",
  "language": "en",
  "overall_sentiment": 72.5,
  "summary": "Users are generally excited about DeepSeek's coding capabilities...",
  "last_analyzed": "2026-01-17T10:30:00",
  "posts_count": 85,
  "opinion_clusters": [
    {
      "label": "Code Quality",
      "summary": "Users praise the code capabilities",
      "mention_count": 32
    }
  ],
  "posts": [
    {
      "platform": "reddit",
      "author": "user123",
      "content": "DeepSeek is amazing for coding tasks!",
      "url": "https://reddit.com/r/programming/comments/...",
      "sentiment_score": 85.0,
      "sentiment_label": "positive",
      "upvotes": 150,
      "likes": null,
      "shares": null,
      "comments_count": 42
    }
  ]
}
```

**Error Responses**:

- **404 Not Found**: Keyword ID does not exist
  ```json
  {
    "detail": "Keyword not found"
  }
  ```

---

## Interactive API Documentation

When the API server is running, you can access interactive documentation at:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

These interfaces allow you to test API endpoints directly from your browser.

## API Key Setup

### Reddit API (30 minutes)
1. Go to https://www.reddit.com/prefs/apps
2. Click "create application" or "develop an app"
3. Fill in:
   - name: TrendPulse
   - app type: Script
   - description: Social media sentiment analysis
   - about url: http://localhost:8000
   - redirect uri: http://localhost:8080
4. Copy `client_id` and `client_secret`
5. Add to `.env`:
   ```
   REDDIT_CLIENT_ID=your_client_id
   REDDIT_CLIENT_SECRET=your_client_secret
   ```

### YouTube API (1 hour)
1. Go to https://console.cloud.google.com/
2. Create project: "TrendPulse"
3. Enable YouTube Data API v3
4. Create credentials → API Key
5. Add to `.env`:
   ```
   YOUTUBE_API_KEY=your_api_key
   ```

### Tongyi Qianwen API (Provided)
Sign up at https://dashscope.aliyun.com/ and get your API key.

Add to `.env`:
```
LLM_API_KEY=your_api_key
LLM_API_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
LLM_MODEL=qwen-plus
```

## Development

### Running Tests

**Backend**:
```bash
cd backend
pytest tests/ -v
```

**Frontend**:
```bash
cd frontend
flutter test
```

### Project Structure

```
trend-pulse/
├── backend/
│   ├── src/
│   │   ├── collectors/        # Platform scrapers
│   │   ├── ai_analysis/       # AI processing
│   │   ├── database/          # DB models and operations
│   │   ├── api/               # FastAPI endpoints
│   │   ├── config.py          # Configuration
│   │   └── orchestrator.py    # Main pipeline
│   ├── tests/
│   ├── .env.example
│   └── requirements.txt
├── frontend/
│   └── lib/
│       ├── screens/           # UI screens
│       ├── widgets/           # Reusable widgets
│       └── services/          # API client
└── README.md
```

## Performance Notes

- **Analysis Time**: 30-60 seconds per keyword (depending on platforms)
- **Token Usage**: Optimized with batch processing
- **Database**: SQLite for development (PostgreSQL for production)

## Scoring Criteria

| Module | Score | Criteria |
|--------|-------|----------|
| Data Collection | 30 | 2 platforms (20), 3 platforms (30) |
| AI Analysis | 25 | Accuracy, clustering quality, prompts |
| Flutter Frontend | 20 | UI beauty, interaction, clarity |
| Code Quality | 15 | Standards, error handling, docs |
| Innovation | 10 | Scheduling, mind maps, anti-scraping docs |

## License

MIT License - See LICENSE file for details

## Credits

Built for the TrendPulse challenge (2026)
