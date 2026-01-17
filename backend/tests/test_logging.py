#!/usr/bin/env python3
"""
Test script to demonstrate the unified logging system.
Run this script to see how logs are formatted and saved.
"""
import asyncio
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.utils.logger_config import (
    get_logger,
    get_collector_logger,
    get_ai_logger,
    get_api_logger,
    get_orchestrator_logger,
)


def test_basic_logging():
    """Test basic logging functionality."""
    print("\n" + "=" * 60)
    print("Testing Basic Logging")
    print("=" * 60 + "\n")

    logger = get_logger("test_module")

    logger.debug("This is a DEBUG message")
    logger.info("This is an INFO message")
    logger.warning("This is a WARNING message")
    logger.error("This is an ERROR message")
    # logger.critical("This is a CRITICAL message")


def test_collector_logging():
    """Test collector-specific logging."""
    print("\n" + "=" * 60)
    print("Testing Collector Logging")
    print("=" * 60 + "\n")

    reddit_logger = get_collector_logger("reddit")
    youtube_logger = get_collector_logger("youtube")
    twitter_logger = get_collector_logger("twitter")

    reddit_logger.info("Reddit collector initialized")
    reddit_logger.info("Searching for posts...")
    reddit_logger.info("Collected 15 posts from Reddit")

    youtube_logger.info("YouTube collector initialized")
    youtube_logger.warning("No proxy configured - may encounter IP blocking")
    youtube_logger.info("Found 5 videos")
    youtube_logger.error("Failed to fetch transcript for video xyz123")

    twitter_logger.info("Twitter collector initialized")
    twitter_logger.info("Launching browser...")
    twitter_logger.info("Scraping completed! Collected 20 tweets")


def test_ai_logging():
    """Test AI analysis logging."""
    print("\n" + "=" * 60)
    print("Testing AI Analysis Logging")
    print("=" * 60 + "\n")

    ai_logger = get_ai_logger()

    ai_logger.info("Initializing AI analysis pipeline")
    ai_logger.info("Starting sentiment analysis for 50 posts...")
    ai_logger.info("Batch processing: [1/5] (20%)")
    ai_logger.info("Batch processing: [2/5] (40%)")
    ai_logger.info("Batch processing: [3/5] (60%)")
    ai_logger.info("Batch processing: [4/5] (80%)")
    ai_logger.info("Batch processing: [5/5] (100%)")


def test_api_logging():
    """Test API logging."""
    print("\n" + "=" * 60)
    print("Testing API Logging")
    print("=" * 60 + "\n")

    api_logger = get_api_logger()

    api_logger.info("Starting TrendPulse API server...")
    api_logger.info("Received analysis request for keyword: 'AI technology'")
    api_logger.info("Platforms: ['reddit', 'twitter'], Language: en, Limit: 20")
    api_logger.info("Analysis completed successfully for keyword 'AI technology'")
    api_logger.warning("Keyword 12345 not found")


def test_orchestrator_logging():
    """Test orchestrator logging."""
    print("\n" + "=" * 60)
    print("Testing Orchestrator Logging")
    print("=" * 60 + "\n")

    orchestrator_logger = get_orchestrator_logger()

    orchestrator_logger.info("Starting analysis for keyword: 'climate change'")
    orchestrator_logger.info("Platforms: reddit, youtube, twitter")
    orchestrator_logger.info("Language: en")
    orchestrator_logger.info("Limit: 20 per platform")

    orchestrator_logger.info("Collecting from Reddit...")
    orchestrator_logger.info("Collected 18 posts from Reddit")
    orchestrator_logger.info("Collecting from Twitter...")
    orchestrator_logger.error("Twitter collection failed: Connection timeout")

    orchestrator_logger.info("Total posts collected: 18")
    orchestrator_logger.info("Saving to database...")
    orchestrator_logger.info("Saved 18 posts to database")
    orchestrator_logger.info("Running AI analysis...")
    orchestrator_logger.info("Saving analysis results...")
    orchestrator_logger.info("Analysis complete!")


def main():
    """Run all logging tests."""
    print("\n" + "=" * 60)
    print("TrendPulse Unified Logging System - Test Suite")
    print("=" * 60)
    print("\nThis script demonstrates the unified logging system.")
    print("Logs will be displayed with colors and saved to backend/logs/")
    print("\nLog Levels:")
    print("  - DEBUG (blue): Detailed diagnostic information")
    print("  - INFO (green): General informational messages")
    print("  - WARNING (yellow): Warning messages")
    print("  - ERROR (red): Error messages")
    print("  - CRITICAL (red+bold): Critical error messages")

    try:
        test_basic_logging()
        test_collector_logging()
        test_ai_logging()
        test_api_logging()
        test_orchestrator_logging()

        print("\n" + "=" * 60)
        print("All tests completed!")
        print("=" * 60)
        print("\nLogs have been saved to: backend/logs/trendpulse_<date>.log")
        print("\nYou can now use the unified logging system in your code:")
        print("  from src.utils.logger_config import get_logger")
        print("  logger = get_logger(__name__)")
        print("  logger.info('Your message here')")

    except Exception as e:
        print(f"\nError running tests: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
