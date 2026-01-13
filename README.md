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
- **AI**: Tongyi Qianwen (Alibaba Qwen) via OpenAI-compatible API

### Frontend (Flutter)
- **Framework**: Flutter 3.x
- **Visualization**: fl_chart
- **State Management**: Provider

## Setup Instructions

### Prerequisites

- Python 3.10+
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

### POST /analyze

Analyzes sentiment for a keyword across social media platforms.

**Request**:
```json
{
  "keyword": "DeepSeek",
  "language": "en",
  "platforms": ["reddit", "youtube"],
  "limit_per_platform": 50
}
```

**Response**:
```json
{
  "keyword": "DeepSeek",
  "status": "success",
  "posts_count": 85,
  "overall_sentiment": 72.5,
  "sentiment_label": "positive",
  "summary": "Discussion overview...",
  "opinion_clusters": [
    {
      "label": "Code Quality",
      "summary": "Users praise the code capabilities...",
      "mention_count": 32
    }
  ],
  "posts": [...]
}
```

### GET /keywords

Lists all analyzed keywords.

### GET /keywords/{id}

Retrieves detailed analysis for a specific keyword.

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
