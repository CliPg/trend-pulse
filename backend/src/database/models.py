"""
Database models for TrendPulse.
Defines SQLAlchemy ORM models for posts, keywords, and analysis results.
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, Text, DateTime, ForeignKey, Boolean
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


class Subscription(Base):
    """Represents a user's subscription to a keyword for monitoring."""

    __tablename__ = "subscriptions"

    id = Column(Integer, primary_key=True, index=True)
    keyword_id = Column(Integer, ForeignKey("keywords.id"), nullable=False)
    keyword = relationship("Keyword")

    # Subscription configuration
    platforms = Column(String(255))  # comma-separated: "reddit,youtube,twitter"
    language = Column(String(10), default="en")
    post_limit = Column(Integer, default=50)
    alert_threshold = Column(Float, default=30.0)  # Alert if sentiment < threshold

    # Scheduling
    interval_hours = Column(Integer, default=6)  # Check every N hours
    is_active = Column(Boolean, default=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    last_checked_at = Column(DateTime)
    next_check_at = Column(DateTime)

    # User identification (for future multi-user support)
    user_email = Column(String(255))  # For sending alerts


class Alert(Base):
    """Represents a sentiment alert triggered by negative sentiment."""

    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, index=True)
    subscription_id = Column(Integer, ForeignKey("subscriptions.id"), nullable=False)
    subscription = relationship("Subscription")

    keyword_id = Column(Integer, ForeignKey("keywords.id"), nullable=False)
    keyword = relationship("Keyword")

    # Alert details
    sentiment_score = Column(Float, nullable=False)
    sentiment_label = Column(String(50))
    posts_count = Column(Integer, default=0)
    negative_posts_count = Column(Integer, default=0)  # Posts with score < threshold

    # Alert context
    summary = Column(Text)  # What triggered the alert
    top_negative_posts = Column(Text)  # JSON array of worst post IDs

    # Status
    is_sent = Column(Boolean, default=False)  # Whether alert notification was sent
    sent_at = Column(DateTime)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    acknowledged_at = Column(DateTime)  # When user acknowledged the alert
