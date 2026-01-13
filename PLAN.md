Here is Claude's plan:
╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌
 TrendPulse Development Plan

 Project Overview

 Build a social media sentiment analysis system that:
 1. Scrapes data from Reddit, YouTube, and X/Twitter
 2. Analyzes sentiment using AI (0-100 score, opinion clustering, summaries)
 3. Visualizes results in a Flutter dashboard

 User Profile: Beginner level, backend-first approach, 5-7 day timeline

 Implementation Phases

 Phase 0: Environment Setup (Day 0 - 2 hours)

 Objectives: Set up project structure and obtain API credentials

 Key Tasks:
 1. Create directory structure (see "Critical Files" section)
 2. Obtain API keys:
   - Reddit (30 min): https://www.reddit.com/prefs/apps → Create "script" app
   - YouTube (1 hour): https://console.cloud.google.com → Enable YouTube Data API v3 → Create API key
   - LLM API (provided): Add to .env
 3. Install dependencies:
 cd backend
 python -m venv venv
 source venv/bin/activate
 pip install -r requirements.txt
 playwright install chromium

 Files to Create:
 - backend/.env.example - Template for environment variables
 - backend/.env - Actual API keys (NEVER commit this)
 - backend/requirements.txt - Python dependencies
 - backend/src/config.py - Configuration loader using python-dotenv

 Success Criteria: All API keys obtained, dependencies installed, no import errors

 ---
 Phase 1: Database & Models (Day 1 Morning - 3 hours)

 Objectives: Create database schema and ORM models

 Key Tasks:
 1. Create SQLAlchemy models for Post, Keyword, OpinionCluster, AnalysisJob
 2. Implement DatabaseManager with CRUD operations
 3. Write tests to verify database operations

 Critical Files:
 - /Users/clipg/Projects/company-projs/yingyang-projs/trend-pulse/backend/src/database/models.py
   - Defines Post, Keyword, OpinionCluster, AnalysisJob tables
   - Use SQLAlchemy declarative_base
 - /Users/clipg/Projects/company-projs/yingyang-projs/trend-pulse/backend/src/database/operations.py
   - DatabaseManager class with async methods
   - Key methods: create_keyword(), save_posts(), update_sentiment(), save_opinion_clusters()

 Testing:
 cd backend
 pytest tests/test_database.py -v

 Success Criteria: Can create keywords, save posts, query data

 ---
 Phase 2: Reddit Collector (Day 1 Afternoon - 4 hours)

 Objectives: Build first data collector (easiest platform)

 Key Tasks:
 1. Create BaseCollector abstract class
 2. Implement RedditCollector using PRAW library
 3. Add spam filtering and content cleaning
 4. Test with real searches

 Critical Files:
 - /Users/clipg/Projects/company-projs/yingyang-projs/trend-pulse/backend/src/collectors/base.py
   - PostData dataclass
   - BaseCollector abstract class with search() method
   - Helper methods: clean_content(), is_spam()
 - /Users/clipg/Projects/company-projs/yingyang-projs/trend-pulse/backend/src/collectors/reddit.py
   - RedditCollector class using PRAW
   - _search_sync() method runs in thread pool
   - Returns List[PostData]

 Testing:
 cd backend
 python -m pytest tests/test_reddit_collector.py -v -s
 # or manual test
 python -m src.main

 Success Criteria: Retrieves Reddit posts, cleans content, filters spam

 ---
 Phase 3: YouTube Collector (Day 2 - 4 hours)

 Objectives: Build YouTube collector for video transcripts

 Key Tasks:
 1. Search YouTube Data API v3 for videos
 2. Fetch transcripts using youtube-transcript-api
 3. Handle videos without transcripts gracefully
 4. Expect 30-50% success rate (many videos lack transcripts)

 Critical Files:
 - /Users/clipg/Projects/company-projs/yingyang-projs/trend-pulse/backend/src/collectors/youtube.py
   - YouTubeCollector class
   - _search_videos() using aiohttp
   - _fetch_transcript() using YouTubeTranscriptApi in thread pool

 Testing:
 python -m pytest tests/test_youtube_collector.py -v -s

 Success Criteria: Retrieves video metadata, fetches transcripts, handles errors

 Common Issues:
 - YouTube API quota: 10,000 units/day, 100 units per search
 - Auto-generated transcripts may have poor quality
 - Long transcripts: Consider truncating for AI analysis

 ---
 Phase 4: X/Twitter Collector (Day 3 - 5 hours)

 Objectives: Build Twitter collector (most challenging)

 Approach Options:

 Option A: Playwright (No API Required) - Use if no API access
 - /Users/clipg/Projects/company-projs/yingyang-projs/trend-pulse/backend/src/collectors/twitter.py
 - Uses headless Chrome to scrape Twitter
 - Fragile: DOM structure changes frequently
 - Add anti-detection: user-agent spoofing, delays
 - Expect 40-60% failure rate

 Option B: Official API (Recommended if available)
 - Requires Bearer Token from https://developer.twitter.com/
 - More reliable but limited access
 - Create twitter_api.py instead

 Testing:
 python -m pytest tests/test_twitter_collector.py -v -s

 Success Criteria: Retrieves tweets, extracts text and metrics, handles rate limits

 Note: If this proves too difficult, prioritize Reddit+YouTube (20/30 points) and move on

 ---
 Phase 5: AI Analysis Module (Day 4 - 6 hours)

 Objectives: Implement sentiment analysis, clustering, summarization

 Key Tasks:
 1. Create LLMClient for API calls
 2. Implement SentimentAnalyzer with batch processing
 3. Implement OpinionClusterer to identify 3 main themes
 4. Implement Summarizer for discussion overview
 5. Create AnalysisPipeline to orchestrate all components

 Critical Files:
 - /Users/clipg/Projects/company-projs/yingyang-projs/trend-pulse/backend/src/ai_analysis/client.py
   - LLMClient class with chat_completion() method
   - Handles API authentication and errors
 - /Users/clipg/Projects/company-projs/yingyang-projs/trend-pulse/backend/src/ai_analysis/sentiment.py
   - SentimentAnalyzer class
   - analyze_batch() for efficient token usage
   - Returns 0-100 scores with labels (positive/negative/neutral)
 - /Users/clipg/Projects/company-projs/yingyang-projs/trend-pulse/backend/src/ai_analysis/clustering.py
   - OpinionClusterer class
   - cluster_opinions() identifies 3 main themes
   - Returns label, summary, mention_count
 - /Users/clipg/Projects/company-projs/yingyang-projs/trend-pulse/backend/src/ai_analysis/summarizer.py
   - Summarizer class
   - summarize_discussion() generates 2-3 paragraph summary
 - /Users/clipg/Projects/company-projs/yingyang-projs/trend-pulse/backend/src/ai_analysis/pipeline.py
   - AnalysisPipeline class
   - analyze_posts() orchestrates all AI components
   - Returns complete analysis results

 Prompt Design (document in docs/PROMPTS.md):
 - Sentiment: Ask for JSON with score (0-100), label, confidence
 - Clustering: Ask for 3 distinct themes with sample quotes
 - Summary: Ask for natural language overview of discussion

 Token Optimization:
 - Batch processing: Analyze 10 posts per request
 - Truncate long content: Limit to 500 chars per post
 - Pre-filter: Remove spam/short posts before sending to AI

 Testing:
 python -m pytest tests/test_ai_analysis.py -v -s

 Success Criteria: Sentiment scores reasonable, clusters identify themes, summary coherent

 ---
 Phase 6: End-to-End Integration & API (Day 5 - 5 hours)

 Objectives: Integrate all components, build REST API

 Key Tasks:
 1. Create TrendPulseOrchestrator to coordinate pipeline
 2. Build FastAPI endpoints for Flutter frontend
 3. Implement error handling and logging
 4. Test complete end-to-end workflow

 Critical Files:
 - /Users/clipg/Projects/company-projs/yingyang-projs/trend-pulse/backend/src/orchestrator.py
   - TrendPulseOrchestrator class
   - analyze_keyword() main method
   - Coordinates collectors → database → AI analysis → results
 - /Users/clipg/Projects/company-projs/yingyang-projs/trend-pulse/backend/src/api/main.py
   - FastAPI app with CORS middleware
   - POST /analyze - Main analysis endpoint
   - GET /keywords/{id} - Retrieve past analyses
   - GET /health - Health check

 API Response Format:
 {
   "keyword": "DeepSeek",
   "status": "success",
   "posts_count": 85,
   "overall_sentiment": 72.5,
   "sentiment_label": "positive",
   "summary": "...",
   "opinion_clusters": [
     {"label": "Code Quality", "summary": "...", "mention_count": 32}
   ],
   "posts": [...]
 }

 Testing:
 # Start API server
 cd backend
 python -m src.api.main

 # Test with curl
 curl -X POST http://localhost:8000/analyze \
   -H "Content-Type: application/json" \
   -d '{"keyword": "DeepSeek", "platforms": ["reddit", "youtube"]}'

 # Run integration tests
 python -m pytest tests/test_integration.py -v -s

 Success Criteria: Complete pipeline runs, API returns valid JSON, database persists data

 ---
 Phase 7: Flutter Dashboard (Day 6-7 - 8 hours)

 Objectives: Build Flutter frontend for visualization

 Key Tasks:
 1. Create Flutter project and add dependencies
 2. Build API service for HTTP requests
 3. Create dashboard screen with search input
 4. Implement sentiment gauge widget
 5. Create opinion card and post list widgets
 6. Connect to backend API

 Critical Files:
 - /Users/clipg/Projects/company-projs/yingyang-projs/trend-pulse/frontend/lib/services/api_service.dart
   - ApiService class with analyzeKeyword() method
   - Data models: AnalysisResult, OpinionCluster, Post
   - JSON parsing and error handling
 - /Users/clipg/Projects/company-projs/yingyang-projs/trend-pulse/frontend/lib/screens/dashboard_screen.dart
   - Main screen with search input
   - Displays results when API returns
   - Shows loading indicator during analysis
 - /Users/clipg/Projects/company-projs/yingyang-projs/trend-pulse/frontend/lib/widgets/sentiment_gauge.dart
   - Pie chart gauge using fl_chart
   - Color-coded: red (0-40), orange (40-70), green (70-100)
 - /Users/clipg/Projects/company-projs/yingyang-projs/trend-pulse/frontend/lib/widgets/opinion_card.dart
   - Card widget for each opinion cluster
   - Shows label, summary, mention count
 - /Users/clipg/Projects/company-projs/yingyang-projs/trend-pulse/frontend/lib/widgets/post_list.dart
   - Scrollable list of source posts
   - Platform icons and sentiment badges
   - Tap to open original post URL

 Dependencies (pubspec.yaml):
 dependencies:
   http: ^1.1.0
   provider: ^6.1.0
   fl_chart: ^0.65.0
   shared_preferences: ^2.2.0

 Testing:
 cd frontend
 flutter pub get
 flutter run

 Success Criteria: App launches, can search keywords, displays all data correctly

 ---
 Bonus Features (Optional - Day 7)

 B1. Scheduled Monitoring (5 points)

 - File: backend/src/scheduler.py
 - Check keywords every 6 hours
 - Alert if sentiment < 30
 - Use asyncio.sleep() for scheduling

 B2. Mind Map Generation (5 points)

 - File: backend/src/ai_analysis/mindmap.py
 - Generate Mermaid format mind map from clusters
 - Render in Flutter using mermaid_dart package

 B3. Anti-Scraping Documentation (5 points)

 - File: docs/ANTI_SCRAPING.md
 - Document IP rotation, header spoofing
 - Explain rate limiting and delays
 - Describe Nitter mirrors for Twitter

 ---
 Critical Files Summary

 Backend (Must Create)

 1. backend/src/config.py - Configuration management
 2. backend/src/database/models.py - Database schema
 3. backend/src/database/operations.py - Database operations
 4. backend/src/collectors/base.py - Base collector interface
 5. backend/src/collectors/reddit.py - Reddit collector
 6. backend/src/collectors/youtube.py - YouTube collector
 7. backend/src/collectors/twitter.py - Twitter collector
 8. backend/src/ai_analysis/client.py - LLM API client
 9. backend/src/ai_analysis/sentiment.py - Sentiment analyzer
 10. backend/src/ai_analysis/clustering.py - Opinion clusterer
 11. backend/src/ai_analysis/summarizer.py - Summarizer
 12. backend/src/ai_analysis/pipeline.py - AI pipeline
 13. backend/src/orchestrator.py - Main orchestrator
 14. backend/src/api/main.py - FastAPI endpoints

 Frontend (Must Create)

 1. frontend/lib/services/api_service.dart - API client
 2. frontend/lib/screens/dashboard_screen.dart - Main screen
 3. frontend/lib/widgets/sentiment_gauge.dart - Sentiment visualization
 4. frontend/lib/widgets/opinion_card.dart - Opinion display
 5. frontend/lib/widgets/post_list.dart - Source posts list
 6. frontend/lib/main.dart - App entry point

 Configuration (Must Create)

 1. backend/.env - API keys (NEVER commit)
 2. backend/.env.example - Environment template
 3. backend/requirements.txt - Python dependencies
 4. frontend/pubspec.yaml - Flutter dependencies

 ---
 Testing Strategy

 Unit Tests (Each Phase)

 cd backend
 pytest tests/ -v

 Integration Tests (Phase 6+)

 pytest tests/test_integration.py -v -s

 Manual Testing Checklist

 - Reddit collector retrieves posts
 - YouTube collector fetches transcripts
 - Twitter collector works (if implemented)
 - Sentiment scores 0-100 range
 - Opinion clusters identify themes
 - Summary is readable
 - API returns valid JSON
 - Flutter app displays data
 - No API keys in code

 ---
 Timeline

 | Day | Phase             | Duration |
 |-----|-------------------|----------|
 | 0   | Setup             | 2 hours  |
 | 1   | Database + Reddit | 7 hours  |
 | 2   | YouTube           | 4 hours  |
 | 3   | Twitter           | 5 hours  |
 | 4   | AI Analysis       | 6 hours  |
 | 5   | Integration + API | 5 hours  |
 | 6-7 | Flutter Dashboard | 8 hours  |
 | 7   | Bonus Features    | Optional |

 Total: 5-7 days (37-51 hours)

 ---
 Priority for Maximum Points

 1. Reddit + YouTube (20/30 points) - Must complete
 2. AI Analysis (25 points) - Must complete
 3. Flutter Dashboard (20 points) - Must complete
 4. Add Twitter (+10 points) - Bonus if time permits
 5. Bonus Features (+10 points) - Optional

 Minimum Viable Product: Reddit + YouTube + AI + Flutter = 65/100 points
 Complete System: All three platforms + bonus = 100/100 points

 ---
 Common Pitfalls to Avoid

 1. Hardcoding API keys - Always use environment variables
 2. Not testing incrementally - Test each phase before moving on
 3. Skipping type annotations - Required for grading
 4. Forgetting error handling - Scraping fails frequently
 5. Long AI analysis time - Use batch processing, limit input size
 6. Token cost overruns - Pre-filter spam, truncate long content
 7. Twitter difficulties - Don't spend more than 1 day, prioritize other platforms

 ---
 Success Criteria

 Must Have (for passing grade)

 - At least 2 platforms working (Reddit, YouTube)
 - Sentiment analysis with 0-100 scoring
 - Opinion clustering identifying 3 themes
 - Flutter dashboard with sentiment gauge
 - API keys in environment variables
 - Type annotations on Python code
 - README with setup instructions
 - Demo video showing workflow

 Nice to Have (for bonus points)

 - All 3 platforms working
 - Scheduled monitoring
 - Mind map generation
 - Anti-scraping documentation
 - Unit and integration tests
 - Error handling for all failures

 ---
 Next Steps

 1. Start with Phase 0: Get API keys today
 2. Create project structure: Follow directory layout
 3. Begin Phase 1: Build database models tomorrow
 4. Test incrementally: Run tests after each phase
 5. Document challenges: Note solutions for technical doc

 Remember: Focus on Reddit and YouTube first. They're the most reliable. Add Twitter only if time permits. The key is a working end-to-end system, not perfect implementation of
 every feature.