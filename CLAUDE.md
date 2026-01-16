# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

TrendPulse 舆情脉冲 is a full-stack social media sentiment analysis application that:
- Scrapes data from X/Reddit/YouTube based on keywords
- Performs AI-powered sentiment analysis and opinion clustering
- Visualizes results in a Flutter dashboard

**Architecture**: Event-driven Python backend + Flutter frontend

## Technology Stack

### Backend (Python)
- **Framework**: asyncio/aiohttp for concurrent scraping
- **Data Collection**:
  - `praw` for Reddit API
  - `youtube-transcript-api` for YouTube captions
  - `Playwright`/`Selenium` for X/Twitter scraping
- **Database**: SQLite
- **AI**: Large Language Model API (使用通义千问)
- **Optional**: LangChain for AI operation chaining

### Frontend (Flutter)
- **Framework**: Flutter 3.x
- **Visualization**: `fl_chart` for charts
- **State Management**: Provider or Riverpod

## Project Structure

```
trend-pulse/
├── backend/                    # Python backend
│   ├── src/
│   │   ├── collectors/        # Platform-specific scrapers (Reddit, YouTube, X)
│   │   ├── ai_analysis/       # AI processing (sentiment, clustering, summarization)
│   │   ├── database/          # DB models and operations
│   │   └── api/               # API endpoints for Flutter frontend
│   ├── requirements.txt
│   └── README.md
├── frontend/                  # Flutter app
│   ├── lib/
│   ├── assets/
│   └── pubspec.yaml
├── docs/                     # Technical documentation
└── README.md                 # Project overview and setup
```

## Core Features

### 1. Multi-Source Data Collection
- **Input**: keyword, language (en/zh), count limit
- **Platforms**: Reddit, YouTube, X/Twitter (minimum 2 required)
- **Output**: Cleaned data in database
- **Challenges**: Anti-bot measures, data cleaning, deduplication

### 2. AI Analysis Pipeline
- **Sentiment scoring**: 0-100 scale (0=very negative, 100=very positive)
- **Opinion clustering**: Extract top 3 discussion points
- **Summary generation**: Convert raw comments to human-readable summary
- **Token optimization**: Process long text efficiently (consider Map-Reduce pattern)
- **Data cleaning**: Filter ads, spam, and garbled text

### 3. Flutter Visualization
- **Dashboard page**: Heat metrics, sentiment gauge, core opinion cards
- **Data flow page**: List of original posts with source links

## Development Commands

### Backend (Python)
```bash
# Install dependencies
cd backend
pip install -r requirements.txt

# Run development server (adjust based on actual implementation)
python -m src.api.main

# Run tests (if implemented)
pytest

# Type checking
mypy src/
```

### Frontend (Flutter)
```bash
cd frontend

# Install dependencies
flutter pub get

# Run development app
flutter run

# Build for specific platform
flutter build apk      # Android
flutter build ios      # iOS
flutter build macos    # macOS

# Run tests
flutter test
```

## Key Implementation Considerations

### Scraping Strategies
- **Reddit**: Use official API via `praw` library
- **YouTube**: Prioritize transcript/caption data (contains valuable opinions)
- **X/Twitter**: Use Nitter mirror sites or headless browsers (anti-scraping challenges)

### AI Prompt Design
- Chain-of-thought processing for sentiment analysis
- Map-Reduce pattern for long text to control token costs
- Explicit instructions to ignore ads/spam in analysis prompts
- Structured output parsing for consistent results

### Token Cost Control
- Pre-filter spam/short comments before sending to AI
- Batch processing with size limits
- Extract key sentences instead of full text when possible
- Consider caching for repeated queries

### Data Quality
- Deduplicate posts across platforms
- Clean markdown/HTML artifacts
- Filter non-relevant content (ads, bots, garbled text)
- Validate language matching user preference

## Security Requirements

- **NEVER** commit API keys to Git repository
- Use environment variables for sensitive data
- Create `.env.example` file showing required variables (without actual values)
- Document all required environment variables in README.md

## Code Quality Standards

- Python: Type annotations required, docstrings for key functions
- Flutter: Follow Dart style guide
- Error handling: Graceful degradation when scraping fails
- Logging: Comprehensive logging for debugging scraping issues

## Deliverables

1. **GitHub Repository** with clear structure and README
2. **README.md** containing:
   - Project introduction
   - Architecture diagram
   - Local setup instructions
   - API documentation
3. **Demo Video** (3-5 minutes) showing complete workflow
4. **Technical Documentation** covering:
   - Scraping strategies for each platform
   - AI prompt design and token optimization
   - Problem-solving approaches (anti-scraping, data cleaning, etc.)

## Bonus Features (Innovation Points)

- Scheduled keyword monitoring (every 6 hours)
- Negative sentiment alerts (score < 30)
- Mind map generation (Mermaid format)
- Anti-scraping documentation (IP rotation, header spoofing, etc.)

## Scoring Criteria

- **Data Collection (30 pts)**: 2 platforms (20 pts), 3 platforms (30 pts) + quality/dedup
- **AI Analysis (25 pts)**: Accuracy, clustering quality, prompt design, token control
- **Flutter Frontend (20 pts)**: UI beauty, interaction smoothness, data clarity
- **Code Quality (15 pts)**: Standards, error handling, logging, docs
- **Innovation (10 pts)**: Scheduling, mind maps, anti-scraping docs, other features

## Timeline

- **Duration**: 5-7 days
- **Deadline**: January 18, 2026

## Tips

You should activate virtual environment before executing a python command.
