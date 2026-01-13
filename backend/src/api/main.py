"""
FastAPI application for TrendPulse.
Provides REST API endpoints for the Flutter frontend.
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional

from src.database.operations import DatabaseManager
from src.orchestrator import TrendPulseOrchestrator
from src.config import Config

# Initialize
app = FastAPI(title="TrendPulse API", version="1.0.0")
db = DatabaseManager(Config.DATABASE_URL)
orchestrator = TrendPulseOrchestrator(db)

# CORS middleware for Flutter
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Pydantic models
class AnalysisRequest(BaseModel):
    keyword: str = Field(..., description="Keyword to analyze")
    language: str = Field(default="en", description="Language code (en, zh)")
    platforms: Optional[List[str]] = Field(
        default=None, description="Platforms to scrape (reddit, youtube, twitter)"
    )
    limit_per_platform: int = Field(
        default=50, description="Maximum posts per platform"
    )


class AnalysisResponse(BaseModel):
    keyword: str
    status: str
    posts_count: int
    overall_sentiment: float
    sentiment_label: str
    summary: str
    opinion_clusters: List[dict]
    posts: List[dict]


@app.on_event("startup")
async def startup():
    """Initialize database on startup."""
    await db.init_db()


@app.get("/")
async def root():
    """API health check."""
    return {"status": "healthy", "service": "TrendPulse API", "version": "1.0.0"}


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "ok"}


@app.post("/analyze", response_model=AnalysisResponse)
async def analyze_keyword(request: AnalysisRequest):
    """
    Analyze sentiment for a keyword across social media platforms.

    This endpoint:
    1. Scrapes data from specified platforms
    2. Runs AI sentiment analysis
    3. Returns comprehensive results

    **Note**: This operation can take 30-60 seconds depending on platforms.
    """
    try:
        result = await orchestrator.analyze_keyword(
            keyword=request.keyword,
            language=request.language,
            platforms=request.platforms,
            limit_per_platform=request.limit_per_platform,
        )

        if result["status"] == "failed":
            raise HTTPException(status_code=400, detail=result["message"])

        return result

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/keywords")
async def list_keywords():
    """List all analyzed keywords."""
    keywords = await db.get_all_keywords()
    return {
        "keywords": [
            {
                "id": k.id,
                "keyword": k.keyword,
                "language": k.language,
                "overall_sentiment": k.overall_sentiment,
                "last_analyzed": k.last_analyzed.isoformat() if k.last_analyzed else None,
            }
            for k in keywords
        ]
    }


@app.get("/keywords/{keyword_id}")
async def get_keyword_analysis(keyword_id: int):
    """Get detailed analysis for a specific keyword."""
    keyword = await db.get_keyword_by_id(keyword_id)
    if not keyword:
        raise HTTPException(status_code=404, detail="Keyword not found")

    posts = await db.get_posts_by_keyword(keyword_id)
    clusters = await db.get_opinion_clusters(keyword_id)

    return {
        "id": keyword.id,
        "keyword": keyword.keyword,
        "language": keyword.language,
        "overall_sentiment": keyword.overall_sentiment,
        "summary": keyword.summary,
        "last_analyzed": keyword.last_analyzed.isoformat() if keyword.last_analyzed else None,
        "posts_count": len(posts),
        "opinion_clusters": [
            {
                "label": c.cluster_label,
                "summary": c.cluster_summary,
                "mention_count": c.mention_count,
            }
            for c in clusters
        ],
        "posts": [
            {
                "platform": post.platform,
                "author": post.author,
                "content": post.content,
                "url": post.url,
                "sentiment_score": post.sentiment_score,
                "sentiment_label": post.sentiment_label,
                "upvotes": post.upvotes,
                "likes": post.likes,
                "shares": post.shares,
                "comments_count": post.comments_count,
            }
            for post in posts[:50]
        ],
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
