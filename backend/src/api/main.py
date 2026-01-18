"""
FastAPI application for TrendPulse.
Provides REST API endpoints for the Flutter frontend.
"""
import json
import asyncio
from datetime import datetime
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from typing import List, Optional, AsyncGenerator

from src.database.operations import DatabaseManager
from src.database.models import Subscription, Alert
from src.orchestrator import TrendPulseOrchestrator
from src.scheduler import get_scheduler
from src.config import Config
from src.utils.logger_config import get_api_logger

# Initialize
app = FastAPI(title="TrendPulse API", version="1.0.0")
db = DatabaseManager(Config.DATABASE_URL)
orchestrator = TrendPulseOrchestrator(db)
logger = get_api_logger()
scheduler = None  # Will be initialized on startup

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


class SubscriptionRequest(BaseModel):
    """Request to create/update a subscription."""
    keyword: str = Field(..., description="Keyword to monitor")
    platforms: Optional[List[str]] = Field(default=None, description="Platforms to scrape")
    language: str = Field(default="en", description="Language code")
    post_limit: int = Field(default=50, description="Posts per platform")
    alert_threshold: float = Field(default=30.0, description="Alert if sentiment < threshold")
    interval_hours: int = Field(default=6, description="Check interval in hours")
    user_email: Optional[str] = Field(default=None, description="Email for alerts")


class SubscriptionResponse(BaseModel):
    """Response model for subscription."""
    id: int
    keyword: str
    keyword_id: int
    platforms: Optional[str]
    language: str
    post_limit: int
    alert_threshold: float
    interval_hours: int
    is_active: bool
    created_at: str
    last_checked_at: Optional[str]
    next_check_at: Optional[str]
    user_email: Optional[str]


class AlertResponse(BaseModel):
    """Response model for alert."""
    id: int
    subscription_id: int
    keyword: str
    sentiment_score: float
    sentiment_label: Optional[str]
    posts_count: int
    negative_posts_count: int
    summary: Optional[str]
    is_sent: bool
    created_at: str
    acknowledged_at: Optional[str]


@app.on_event("startup")
async def startup():
    """Initialize database and scheduler on startup."""
    global scheduler
    logger.info("Starting TrendPulse API server...")
    await db.init_db()

    # Initialize and start scheduler
    scheduler = get_scheduler(db)
    await scheduler.refresh_all_subscriptions()

    logger.info("API server started successfully with scheduler")


@app.on_event("shutdown")
async def shutdown():
    """Shutdown scheduler on app shutdown."""
    global scheduler
    if scheduler:
        scheduler.shutdown()
        logger.info("Scheduler shutdown")


@app.get("/")
async def root():
    """API health check."""
    return {"status": "healthy", "service": "TrendPulse API", "version": "1.0.0"}


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "ok"}


@app.post("/analyze/stream")
async def analyze_keyword_stream(request: AnalysisRequest):
    """
    Analyze sentiment for a keyword with streaming progress updates (SSE).

    This endpoint uses Server-Sent Events (SSE) to stream progress updates
    in real-time while the analysis is running.

    Progress events include:
    - init: Analysis started
    - collecting: Data collection from platforms
    - database: Database operations
    - analyzing: AI analysis in progress
    - visualizing: Generating charts
    - complete: Analysis finished
    - error: Error occurred
    - result: Final result data
    """

    async def event_generator() -> AsyncGenerator[str, None]:
        """Generate SSE events for analysis progress."""
        progress_queue: asyncio.Queue = asyncio.Queue()
        final_result = None
        error_occurred = None

        def progress_callback(stage: str, message: str, data: Optional[dict] = None):
            """Callback to receive progress updates from orchestrator."""
            event_data = {
                "stage": stage,
                "message": message,
                "data": data or {},
                "timestamp": datetime.utcnow().isoformat()
            }
            try:
                progress_queue.put_nowait(event_data)
            except asyncio.QueueFull:
                pass  # Skip if queue is full

        async def run_analysis():
            """Run the analysis in background."""
            nonlocal final_result, error_occurred
            try:
                result = await orchestrator.analyze_keyword(
                    keyword=request.keyword,
                    language=request.language,
                    platforms=request.platforms,
                    limit_per_platform=request.limit_per_platform,
                    progress_callback=progress_callback,
                )
                final_result = result
            except Exception as e:
                error_occurred = str(e)
                progress_callback("error", f"Analysis failed: {str(e)}", {"error": str(e)})

        # Start analysis task
        analysis_task = asyncio.create_task(run_analysis())

        try:
            # Stream progress events
            while not analysis_task.done():
                try:
                    # Wait for progress update with timeout
                    event_data = await asyncio.wait_for(
                        progress_queue.get(),
                        timeout=0.5
                    )
                    yield f"data: {json.dumps(event_data)}\n\n"
                except asyncio.TimeoutError:
                    # Send heartbeat to keep connection alive
                    yield f": heartbeat\n\n"
                    continue

            # Drain any remaining events from queue
            while not progress_queue.empty():
                try:
                    event_data = progress_queue.get_nowait()
                    yield f"data: {json.dumps(event_data)}\n\n"
                except asyncio.QueueEmpty:
                    break

            # Wait for task to complete and get any exception
            await analysis_task

            # Send final result or error
            if error_occurred:
                yield f"data: {json.dumps({'stage': 'error', 'message': error_occurred, 'data': {}})}\n\n"
            elif final_result:
                # Send result in a separate event
                yield f"data: {json.dumps({'stage': 'result', 'message': 'Analysis complete', 'data': final_result})}\n\n"

        except asyncio.CancelledError:
            analysis_task.cancel()
            raise

    logger.info(f"Starting streaming analysis for keyword: '{request.keyword}'")

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",  # Disable nginx buffering
        }
    )


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


# ==================== Subscription Management ====================

@app.post("/subscriptions", response_model=SubscriptionResponse)
async def create_subscription(request: SubscriptionRequest):
    """
    Create a new subscription for keyword monitoring.

    The system will check this keyword periodically and trigger alerts if sentiment drops below threshold.
    """
    try:
        from src.database.models import Keyword

        with db.get_session() as session:
            # Find or create keyword
            keyword = session.query(Keyword).filter_by(keyword=request.keyword).first()
            if not keyword:
                keyword = Keyword(keyword=request.keyword, language=request.language)
                session.add(keyword)
                session.commit()
                session.refresh(keyword)

            # Check if subscription already exists
            existing = session.query(Subscription).filter_by(
                keyword_id=keyword.id,
                is_active=True
            ).first()

            if existing:
                raise HTTPException(
                    status_code=400,
                    detail=f"Already subscribed to keyword '{request.keyword}'"
                )

            # Create subscription
            platforms_str = ",".join(request.platforms) if request.platforms else None

            subscription = Subscription(
                keyword_id=keyword.id,
                platforms=platforms_str,
                language=request.language,
                post_limit=request.post_limit,
                alert_threshold=request.alert_threshold,
                interval_hours=request.interval_hours,
                user_email=request.user_email,
                next_check_at=datetime.utcnow(),  # Start immediately
            )

            session.add(subscription)
            session.commit()
            session.refresh(subscription)

            # Schedule the subscription
            if scheduler:
                await scheduler.schedule_subscription(subscription.id)

            logger.info(f"Created subscription for keyword: {request.keyword}")

            return SubscriptionResponse(
                id=subscription.id,
                keyword=keyword.keyword,
                keyword_id=subscription.keyword_id,
                platforms=subscription.platforms,
                language=subscription.language,
                post_limit=subscription.post_limit,
                alert_threshold=subscription.alert_threshold,
                interval_hours=subscription.interval_hours,
                is_active=subscription.is_active,
                created_at=subscription.created_at.isoformat(),
                last_checked_at=subscription.last_checked_at.isoformat() if subscription.last_checked_at else None,
                next_check_at=subscription.next_check_at.isoformat() if subscription.next_check_at else None,
                user_email=subscription.user_email,
            )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating subscription: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/subscriptions", response_model=List[SubscriptionResponse])
async def list_subscriptions():
    """List all active subscriptions."""
    try:
        with db.get_session() as session:
            subscriptions = session.query(Subscription).filter_by(is_active=True).all()

            return [
                SubscriptionResponse(
                    id=sub.id,
                    keyword=sub.keyword.keyword,
                    keyword_id=sub.keyword_id,
                    platforms=sub.platforms,
                    language=sub.language,
                    post_limit=sub.post_limit,
                    alert_threshold=sub.alert_threshold,
                    interval_hours=sub.interval_hours,
                    is_active=sub.is_active,
                    created_at=sub.created_at.isoformat(),
                    last_checked_at=sub.last_checked_at.isoformat() if sub.last_checked_at else None,
                    next_check_at=sub.next_check_at.isoformat() if sub.next_check_at else None,
                    user_email=sub.user_email,
                )
                for sub in subscriptions
            ]

    except Exception as e:
        logger.error(f"Error listing subscriptions: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/subscriptions/{subscription_id}")
async def delete_subscription(subscription_id: int):
    """Cancel (deactivate) a subscription."""
    try:
        with db.get_session() as session:
            subscription = session.query(Subscription).get(subscription_id)

            if not subscription:
                raise HTTPException(status_code=404, detail="Subscription not found")

            subscription.is_active = False
            session.commit()

            # Unschedule
            if scheduler:
                scheduler.unschedule_subscription(subscription_id)

            logger.info(f"Deactivated subscription {subscription_id}")

            return {"message": "Subscription cancelled successfully"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting subscription: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.put("/subscriptions/{subscription_id}", response_model=SubscriptionResponse)
async def update_subscription(subscription_id: int, request: SubscriptionRequest):
    """
    Update an existing subscription.
    Allows modifying keyword, platforms, threshold, interval, etc.
    """
    try:
        from src.database.models import Keyword

        with db.get_session() as session:
            subscription = session.query(Subscription).get(subscription_id)

            if not subscription:
                raise HTTPException(status_code=404, detail="Subscription not found")

            # Update platforms
            platforms_str = ",".join(request.platforms) if request.platforms else None

            # Update subscription fields
            subscription.platforms = platforms_str
            subscription.language = request.language
            subscription.post_limit = request.post_limit
            subscription.alert_threshold = request.alert_threshold
            subscription.interval_hours = request.interval_hours
            subscription.user_email = request.user_email

            # Update keyword if changed
            if subscription.keyword.keyword != request.keyword:
                # Find or create new keyword
                keyword = session.query(Keyword).filter_by(keyword=request.keyword).first()
                if not keyword:
                    keyword = Keyword(keyword=request.keyword, language=request.language)
                    session.add(keyword)
                    session.commit()
                    session.refresh(keyword)

                subscription.keyword_id = keyword.id

            session.commit()
            session.refresh(subscription)

            # Reschedule with new settings
            if scheduler:
                await scheduler.schedule_subscription(subscription.id)

            logger.info(f"Updated subscription {subscription_id}")

            return SubscriptionResponse(
                id=subscription.id,
                keyword=subscription.keyword.keyword,
                keyword_id=subscription.keyword_id,
                platforms=subscription.platforms,
                language=subscription.language,
                post_limit=subscription.post_limit,
                alert_threshold=subscription.alert_threshold,
                interval_hours=subscription.interval_hours,
                is_active=subscription.is_active,
                created_at=subscription.created_at.isoformat(),
                last_checked_at=subscription.last_checked_at.isoformat() if subscription.last_checked_at else None,
                next_check_at=subscription.next_check_at.isoformat() if subscription.next_check_at else None,
                user_email=subscription.user_email,
            )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating subscription: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


# ==================== Alert Management ====================

@app.get("/alerts", response_model=List[AlertResponse])
async def list_alerts(limit: int = 50, acknowledged: Optional[bool] = None):
    """
    List alert history.

    Query parameters:
    - limit: Maximum number of alerts to return (default: 50)
    - acknowledged: Filter by acknowledgment status (true/false)
    """
    try:
        with db.get_session() as session:
            query = session.query(Alert).order_by(Alert.created_at.desc())

            if acknowledged is not None:
                if acknowledged:
                    query = query.filter(Alert.acknowledged_at.isnot(None))
                else:
                    query = query.filter(Alert.acknowledged_at.is_(None))

            alerts = query.limit(limit).all()

            return [
                AlertResponse(
                    id=alert.id,
                    subscription_id=alert.subscription_id,
                    keyword=alert.keyword.keyword,
                    sentiment_score=alert.sentiment_score,
                    sentiment_label=alert.sentiment_label,
                    posts_count=alert.posts_count,
                    negative_posts_count=alert.negative_posts_count,
                    summary=alert.summary,
                    is_sent=alert.is_sent,
                    created_at=alert.created_at.isoformat(),
                    acknowledged_at=alert.acknowledged_at.isoformat() if alert.acknowledged_at else None,
                )
                for alert in alerts
            ]

    except Exception as e:
        logger.error(f"Error listing alerts: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.patch("/alerts/{alert_id}/acknowledge")
async def acknowledge_alert(alert_id: int):
    """Mark an alert as acknowledged."""
    try:
        with db.get_session() as session:
            alert = session.query(Alert).get(alert_id)

            if not alert:
                raise HTTPException(status_code=404, detail="Alert not found")

            alert.acknowledged_at = datetime.utcnow()
            session.commit()

            logger.info(f"Acknowledged alert {alert_id}")

            return {"message": "Alert acknowledged successfully"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error acknowledging alert: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
