"""
Scheduler for automated keyword monitoring and alerting.
Uses APScheduler to run periodic collection and analysis tasks.
"""
import logging
from datetime import datetime, timedelta
from typing import Optional, TYPE_CHECKING
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger

from src.database.operations import DatabaseManager
from src.orchestrator import TrendPulseOrchestrator
from src.utils.logger_config import setup_logger

if TYPE_CHECKING:
    from src.database.models import Subscription, Alert

logger = setup_logger(__name__)


class TaskScheduler:
    """Manages scheduled tasks for keyword monitoring."""

    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager
        self.orchestrator = TrendPulseOrchestrator(db_manager)
        self.scheduler = AsyncIOScheduler()
        self.scheduler.start()
        logger.info("Task scheduler initialized")

    async def check_subscription(self, subscription_id: int):
        """Check a subscription for negative sentiment and trigger alerts if needed."""
        try:
            from src.database.models import Subscription, Alert, Keyword

            with self.db.get_session() as session:
                subscription = session.query(Subscription).filter_by(
                    id=subscription_id,
                    is_active=True
                ).first()

                if not subscription:
                    logger.warning(f"Subscription {subscription_id} not found or inactive")
                    return

                logger.info(f"Checking subscription: {subscription.keyword.keyword}")

                # Parse platforms
                platforms = subscription.platforms.split(",") if subscription.platforms else None

                # Run analysis
                result = await self.orchestrator.analyze_keyword(
                    keyword=subscription.keyword.keyword,
                    platforms=platforms,
                    language=subscription.language,
                    limit_per_platform=subscription.post_limit
                )

                # Check if sentiment is below threshold
                if result["overall_sentiment"] < subscription.alert_threshold:
                    logger.warning(
                        f"Negative sentiment detected: {result['overall_sentiment']} "
                        f"< {subscription.alert_threshold}"
                    )

                    # Count negative posts
                    negative_posts = [
                        p for p in result["posts"]
                        if p.get("sentiment_score") and p["sentiment_score"] < subscription.alert_threshold
                    ]

                    # Create alert
                    alert = Alert(
                        subscription_id=subscription.id,
                        keyword_id=subscription.keyword_id,
                        sentiment_score=result["overall_sentiment"],
                        sentiment_label=result.get("sentiment_label"),
                        posts_count=result["posts_count"],
                        negative_posts_count=len(negative_posts),
                        summary=result.get("summary", ""),
                    )

                    session.add(alert)
                    session.commit()

                    # Send alert notification
                    await self._send_alert(alert, subscription, result)

                    logger.info(f"Alert created for subscription {subscription_id}")
                else:
                    logger.info(
                        f"Sentiment OK: {result['overall_sentiment']} >= {subscription.alert_threshold}"
                    )

                # Update subscription timestamps
                subscription.last_checked_at = datetime.utcnow()
                subscription.next_check_at = datetime.utcnow() + timedelta(hours=subscription.interval_hours)
                session.commit()

        except Exception as e:
            logger.error(f"Error checking subscription {subscription_id}: {e}", exc_info=True)

    async def _send_alert(self, alert: "Alert", subscription: "Subscription", analysis_result: dict):
        """Send alert notification (email, log, etc.)."""
        try:
            # For now, just log the alert
            logger.warning(
                f"🚨 ALERT TRIGGERED 🚨\n"
                f"Keyword: {subscription.keyword.keyword}\n"
                f"Sentiment: {alert.sentiment_score:.1f}/100\n"
                f"Threshold: {subscription.alert_threshold}\n"
                f"Negative Posts: {alert.negative_posts_count}/{alert.posts_count}\n"
                f"Summary: {alert.summary[:200]}..."
            )

            # TODO: Implement email notifications
            # if subscription.user_email:
            #     await self._send_email_alert(alert, subscription, analysis_result)

            alert.is_sent = True
            alert.sent_at = datetime.utcnow()

        except Exception as e:
            logger.error(f"Error sending alert: {e}", exc_info=True)

    async def schedule_subscription(self, subscription_id: int):
        """Add a subscription to the scheduler."""
        try:
            from src.database.models import Subscription

            with self.db.get_session() as session:
                subscription = session.query(Subscription).get(subscription_id)

                if not subscription:
                    logger.error(f"Subscription {subscription_id} not found")
                    return

                # Calculate next run time
                interval_hours = subscription.interval_hours or 6
                next_check = subscription.next_check_at or (
                    datetime.utcnow() + timedelta(hours=interval_hours)
                )

                # Remove existing job if any
                job_id = f"subscription_{subscription_id}"
                if self.scheduler.get_job(job_id):
                    self.scheduler.remove_job(job_id)

                # Add new job
                self.scheduler.add_job(
                    self.check_subscription,
                    trigger=IntervalTrigger(hours=interval_hours),
                    id=job_id,
                    args=[subscription_id],
                    next_run_time=next_check,
                )

                logger.info(
                    f"Scheduled subscription {subscription_id} "
                    f"(keyword: {subscription.keyword.keyword}, "
                    f"interval: {interval_hours}h)"
                )

        except Exception as e:
            logger.error(f"Error scheduling subscription {subscription_id}: {e}", exc_info=True)

    def unschedule_subscription(self, subscription_id: int):
        """Remove a subscription from the scheduler."""
        try:
            job_id = f"subscription_{subscription_id}"
            if self.scheduler.remove_job(job_id):
                logger.info(f"Unscheduled subscription {subscription_id}")
            else:
                logger.warning(f"No job found for subscription {subscription_id}")

        except Exception as e:
            logger.error(f"Error unscheduling subscription {subscription_id}: {e}", exc_info=True)

    async def refresh_all_subscriptions(self):
        """Load all active subscriptions and schedule them."""
        try:
            from src.database.models import Subscription

            with self.db.get_session() as session:
                subscriptions = session.query(Subscription).filter_by(is_active=True).all()

                logger.info(f"Found {len(subscriptions)} active subscriptions")

                for subscription in subscriptions:
                    await self.schedule_subscription(subscription.id)

        except Exception as e:
            logger.error(f"Error refreshing subscriptions: {e}", exc_info=True)

    def shutdown(self):
        """Shutdown the scheduler."""
        self.scheduler.shutdown()
        logger.info("Scheduler shutdown")


# Global scheduler instance
_scheduler: Optional[TaskScheduler] = None


def get_scheduler(db_manager: DatabaseManager) -> TaskScheduler:
    """Get or create the global scheduler instance."""
    global _scheduler
    if _scheduler is None:
        _scheduler = TaskScheduler(db_manager)
    return _scheduler
