"""
Database models for TrendPulse.
Defines SQLAlchemy ORM models for posts, keywords, and analysis results.
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, Text, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class Post(Base):
    """Represents a post from any social media platform."""

    __tablename__ = "posts"

    id = Column(Integer, primary_key=True, index=True)
    platform = Column(String(50), nullable=False)  # 'reddit', 'youtube', 'twitter'
    post_id = Column(String(255), nullable=False)  # Platform-specific ID
    author = Column(String(255))
    content = Column(Text, nullable=False)
    url = Column(String(2048))
    created_at = Column(DateTime, default=datetime.utcnow)
    collected_at = Column(DateTime, default=datetime.utcnow)

    # Metadata
    upvotes = Column(Integer, default=0)  # Reddit upvotes
    likes = Column(Integer, default=0)  # YouTube likes
    shares = Column(Integer, default=0)  # Twitter shares
    comments_count = Column(Integer, default=0)

    # Analysis results (nullable until analyzed)
    sentiment_score = Column(Float)  # 0-100
    sentiment_label = Column(String(50))  # 'positive', 'negative', 'neutral'

    # Relationships
    keyword_id = Column(Integer, ForeignKey("keywords.id"))
    keyword = relationship("Keyword", back_populates="posts")


class Keyword(Base):
    """Represents a search keyword/query."""

    __tablename__ = "keywords"

    id = Column(Integer, primary_key=True, index=True)
    keyword = Column(String(255), unique=True, nullable=False)
    language = Column(String(10), default="en")
    created_at = Column(DateTime, default=datetime.utcnow)
    last_analyzed = Column(DateTime)  # Track when last analysis was done

    # Analysis results
    overall_sentiment = Column(Float)  # 0-100
    summary = Column(Text)

    # Relationships
    posts = relationship("Post", back_populates="keyword", cascade="all, delete-orphan")


class OpinionCluster(Base):
    """Represents a cluster of similar opinions."""

    __tablename__ = "opinion_clusters"

    id = Column(Integer, primary_key=True, index=True)
    keyword_id = Column(Integer, ForeignKey("keywords.id"))
    cluster_label = Column(String(255), nullable=False)
    cluster_summary = Column(Text, nullable=False)
    representative_post_id = Column(Integer, ForeignKey("posts.id"), nullable=True)
    mention_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)


class AnalysisJob(Base):
    """Tracks analysis jobs for monitoring and debugging."""

    __tablename__ = "analysis_jobs"

    id = Column(Integer, primary_key=True, index=True)
    keyword_id = Column(Integer, ForeignKey("keywords.id"))
    status = Column(String(50), default="pending")  # pending, processing, completed, failed
    platforms_scraped = Column(String(255))  # comma-separated
    posts_collected = Column(Integer, default=0)
    token_used = Column(Integer, default=0)
    error_message = Column(Text)
    started_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime)
