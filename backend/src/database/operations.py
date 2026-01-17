"""
Database operations for TrendPulse.
Provides async database operations for all models.
"""
from typing import List, Optional
from datetime import datetime
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy import select
from src.database.models import Base, Post, Keyword, OpinionCluster, AnalysisJob


class DatabaseManager:
    """Manages database operations for TrendPulse."""

    def __init__(self, database_url: str):
        """
        Initialize database manager.

        Args:
            database_url: SQLAlchemy database URL (e.g., 'sqlite+aiosqlite:///./trendpulse.db')
        """
        self.engine = create_async_engine(database_url, echo=False)
        self.async_session = sessionmaker(
            self.engine, class_=AsyncSession, expire_on_commit=False
        )

    async def init_db(self) -> None:
        """Initialize database tables."""
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    def get_session(self) -> Session:
        """
        Get a synchronous database session.
        Note: This is for compatibility with existing code.
        For async code, use async_session instead.
        """
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker as sync_sessionmaker

        # Convert async URL to sync URL
        sync_url = str(self.engine.url).replace("+aiosqlite", "")

        # Create or get sync engine
        if not hasattr(self, '_sync_engine'):
            self._sync_engine = create_engine(sync_url)
            self._sync_session_maker = sync_sessionmaker(bind=self._sync_engine)

        return self._sync_session_maker()

    def close_sync(self):
        """Close the sync engine and dispose of all sessions."""
        if hasattr(self, '_sync_engine'):
            self._sync_engine.dispose()
            delattr(self, '_sync_engine')
            delattr(self, '_sync_session_maker')

    async def create_keyword(self, keyword: str, language: str = "en") -> Keyword:
        """
        Create a new keyword entry.

        Args:
            keyword: Search keyword
            language: Language code

        Returns:
            Created Keyword object
        """
        async with self.async_session() as session:
            db_keyword = Keyword(keyword=keyword, language=language)
            session.add(db_keyword)
            await session.commit()
            await session.refresh(db_keyword)
            return db_keyword

    async def get_or_create_keyword(self, keyword: str, language: str = "en") -> Keyword:
        """
        Get existing keyword or create new one.

        Args:
            keyword: Search keyword
            language: Language code

        Returns:
            Keyword object (existing or newly created)
        """
        async with self.async_session() as session:
            result = await session.execute(
                select(Keyword).where(Keyword.keyword == keyword)
            )
            existing = result.scalar_one_or_none()
            if existing:
                return existing

            new_keyword = Keyword(keyword=keyword, language=language)
            session.add(new_keyword)
            await session.commit()
            await session.refresh(new_keyword)
            return new_keyword

    async def save_posts(self, posts: List[dict], keyword_id: int) -> List[Post]:
        """
        Save multiple posts to database.

        Args:
            posts: List of post dictionaries
            keyword_id: Foreign key to Keyword

        Returns:
            List of saved Post objects
        """
        async with self.async_session() as session:
            db_posts = []
            for post_data in posts:
                post = Post(
                    platform=post_data["platform"],
                    post_id=post_data["post_id"],
                    author=post_data.get("author"),
                    content=post_data["content"],
                    url=post_data.get("url"),
                    upvotes=post_data.get("upvotes", 0),
                    likes=post_data.get("likes", 0),
                    shares=post_data.get("shares", 0),
                    comments_count=post_data.get("comments_count", 0),
                    keyword_id=keyword_id,
                )
                session.add(post)
                db_posts.append(post)

            await session.commit()
            for post in db_posts:
                await session.refresh(post)
            return db_posts

    async def get_posts_by_keyword(self, keyword_id: int) -> List[Post]:
        """
        Retrieve all posts for a keyword.

        Args:
            keyword_id: Keyword ID

        Returns:
            List of Post objects
        """
        async with self.async_session() as session:
            result = await session.execute(
                select(Post).where(Post.keyword_id == keyword_id)
            )
            return list(result.scalars().all())

    async def update_sentiment(self, post_id: int, score: float, label: str) -> None:
        """
        Update sentiment analysis for a post.

        Args:
            post_id: Post ID
            score: Sentiment score (0-100)
            label: Sentiment label (positive/negative/neutral)
        """
        async with self.async_session() as session:
            result = await session.execute(select(Post).where(Post.id == post_id))
            post = result.scalar_one_or_none()
            if post:
                post.sentiment_score = score
                post.sentiment_label = label
                await session.commit()

    async def save_opinion_clusters(
        self, clusters: List[dict], keyword_id: int
    ) -> List[OpinionCluster]:
        """
        Save opinion clusters for a keyword.

        Args:
            clusters: List of cluster dictionaries
            keyword_id: Foreign key to Keyword

        Returns:
            List of saved OpinionCluster objects
        """
        async with self.async_session() as session:
            db_clusters = []
            for cluster_data in clusters:
                cluster = OpinionCluster(
                    keyword_id=keyword_id,
                    cluster_label=cluster_data["label"],
                    cluster_summary=cluster_data["summary"],
                    representative_post_id=cluster_data.get("representative_post_id"),
                    mention_count=cluster_data.get("mention_count", 0),
                )
                session.add(cluster)
                db_clusters.append(cluster)

            await session.commit()
            return db_clusters

    async def update_keyword_analysis(
        self, keyword_id: int, overall_sentiment: float, summary: str
    ) -> None:
        """
        Update analysis results for a keyword.

        Args:
            keyword_id: Keyword ID
            overall_sentiment: Overall sentiment score (0-100)
            summary: Generated summary
        """
        async with self.async_session() as session:
            result = await session.execute(select(Keyword).where(Keyword.id == keyword_id))
            keyword = result.scalar_one_or_none()
            if keyword:
                keyword.overall_sentiment = overall_sentiment
                keyword.summary = summary
                keyword.last_analyzed = datetime.utcnow()
                await session.commit()

    async def get_all_keywords(self) -> List[Keyword]:
        """
        Retrieve all keywords.

        Returns:
            List of all Keyword objects
        """
        async with self.async_session() as session:
            result = await session.execute(select(Keyword))
            return list(result.scalars().all())

    async def get_keyword_by_id(self, keyword_id: int) -> Optional[Keyword]:
        """
        Get a keyword by ID.

        Args:
            keyword_id: Keyword ID

        Returns:
            Keyword object or None
        """
        async with self.async_session() as session:
            result = await session.execute(select(Keyword).where(Keyword.id == keyword_id))
            return result.scalar_one_or_none()

    async def get_opinion_clusters(self, keyword_id: int) -> List[OpinionCluster]:
        """
        Get all opinion clusters for a keyword.

        Args:
            keyword_id: Keyword ID

        Returns:
            List of OpinionCluster objects
        """
        async with self.async_session() as session:
            result = await session.execute(
                select(OpinionCluster).where(OpinionCluster.keyword_id == keyword_id)
            )
            return list(result.scalars().all())

    async def close(self) -> None:
        """Close database connection."""
        await self.engine.dispose()
