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
from src.utils.logger_config import get_api_logger

# Initialize
app = FastAPI(title="TrendPulse API", version="1.0.0")
db = DatabaseManager(Config.DATABASE_URL)
orchestrator = TrendPulseOrchestrator(db)
logger = get_api_logger()

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
        default=20, description="Maximum posts per platform"
    )


class MermaidCharts(BaseModel):
    """Mermaid diagram code for visualizations."""
    mindmap: str = Field(..., description="Mermaid mindmap code")
    pie_chart: str = Field(..., description="Mermaid pie chart code")
    flowchart: str = Field(..., description="Mermaid flowchart code")


class AnalysisResponse(BaseModel):
    keyword: str
    status: str
    posts_count: int
    overall_sentiment: float
    sentiment_label: str
    summary: str
    opinion_clusters: List[dict]
    posts: List[dict]
    mermaid: Optional[MermaidCharts] = Field(default=None, description="Mermaid visualization charts")


@app.on_event("startup")
async def startup():
    """Initialize database on startup."""
    logger.info("Starting TrendPulse API server...")
    await db.init_db()
    logger.info("API server started successfully")


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
        logger.info(f"Received analysis request for keyword: '{request.keyword}'")
        logger.info(f"Platforms: {request.platforms}, Language: {request.language}, Limit: {request.limit_per_platform}")

        result = await orchestrator.analyze_keyword(
            keyword=request.keyword,
            language=request.language,
            platforms=request.platforms,
            limit_per_platform=request.limit_per_platform,
        )

        if result["status"] == "failed":
            logger.error(f"Analysis failed for keyword '{request.keyword}': {result['message']}")
            raise HTTPException(status_code=400, detail=result["message"])

        logger.info(f"Analysis completed successfully for keyword '{request.keyword}'")
        return result

    except ValueError as e:
        logger.error(f"Validation error for keyword '{request.keyword}': {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error analyzing keyword '{request.keyword}': {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/keywords")
async def list_keywords():
    """List all analyzed keywords."""
    keywords = await db.get_all_keywords()
    logger.info(f"Retrieved {len(keywords)} keywords")
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
        logger.warning(f"Keyword {keyword_id} not found")
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
