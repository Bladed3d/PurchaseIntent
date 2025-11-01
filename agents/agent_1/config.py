"""
Agent 1 Configuration
Loads settings from environment variables with sensible defaults
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class Agent1Config:
    """Configuration for Agent 1 - Product Researcher"""

    # API Credentials
    REDDIT_CLIENT_ID = os.getenv('REDDIT_CLIENT_ID')
    REDDIT_CLIENT_SECRET = os.getenv('REDDIT_CLIENT_SECRET')
    REDDIT_USER_AGENT = os.getenv('REDDIT_USER_AGENT', 'Purchase-Intent-Research/1.0')

    # YouTube API (optional - for video discovery)
    YOUTUBE_API_KEY = os.getenv('YOUTUBE_API_KEY')

    # Amazon Product Advertising API (required for product search)
    AMAZON_ACCESS_KEY = os.getenv('AMAZON_ACCESS_KEY')
    AMAZON_SECRET_KEY = os.getenv('AMAZON_SECRET_KEY')
    AMAZON_ASSOCIATE_TAG = os.getenv('AMAZON_ASSOCIATE_TAG')

    # Rate Limiting
    RATE_LIMIT_DELAY = float(os.getenv('AGENT_1_RATE_LIMIT_DELAY', '2.0'))
    REDDIT_DELAY = 2.0  # Delay between Reddit API calls
    YOUTUBE_DELAY = 1.0  # Delay between YouTube API calls
    AMAZON_DELAY = 2.0  # Delay before Amazon API calls (1 req/sec limit)

    # Query Limits
    MAX_COMPARABLES = int(os.getenv('AGENT_1_MAX_COMPARABLES', '10'))
    MAX_REDDIT_DISCUSSIONS = int(os.getenv('AGENT_1_MAX_REDDIT_DISCUSSIONS', '20'))
    MAX_YOUTUBE_VIDEOS = int(os.getenv('AGENT_1_MAX_YOUTUBE_VIDEOS', '10'))
    MAX_AMAZON_RESULTS = int(os.getenv('AGENT_1_MAX_AMAZON_RESULTS', '15'))
    MAX_GOODREADS_RESULTS = int(os.getenv('AGENT_1_MAX_GOODREADS_RESULTS', '10'))

    # Minimum Thresholds for Quality
    MIN_REVIEWS_AMAZON = int(os.getenv('AGENT_1_MIN_REVIEWS_AMAZON', '50'))
    MIN_COMMENTS_YOUTUBE = int(os.getenv('AGENT_1_MIN_COMMENTS_YOUTUBE', '20'))
    MIN_COMMENTS_REDDIT = int(os.getenv('AGENT_1_MIN_COMMENTS_REDDIT', '10'))
    MIN_TOTAL_COMMENTS = int(os.getenv('AGENT_1_MIN_TOTAL_COMMENTS', '300'))

    # Subreddit Overlap Analysis
    MAX_USERS_OVERLAP = int(os.getenv('AGENT_1_MAX_USERS_OVERLAP', '500'))
    MIN_OVERLAP_MULTIPLIER = float(os.getenv('AGENT_1_MIN_OVERLAP_MULTIPLIER', '2.0'))
    TOP_OVERLAPS = int(os.getenv('AGENT_1_TOP_OVERLAPS', '10'))

    # Scoring Weights for Comparables Ranking
    WEIGHT_SALES_SIGNAL = 0.30  # Amazon BSR, YouTube views
    WEIGHT_REVIEW_VOLUME = 0.30  # Review/comment counts
    WEIGHT_RECENCY = 0.20  # Publication/upload date
    WEIGHT_SEMANTIC = 0.20  # Similarity to user input

    # Cache Settings
    CACHE_DIR = "cache"
    CACHE_DURATION_DAYS = 30  # Reuse comparables cache for 30 days

    # Output Paths
    OUTPUT_DIR = "outputs"

    # LED Ranges (1500-1599)
    LED_INIT = 1500
    LED_AMAZON_START = 1510
    LED_REDDIT_START = 1520
    LED_YOUTUBE_START = 1530
    LED_GOODREADS_START = 1540
    LED_COMPARABLES_START = 1550
    LED_OVERLAP_START = 1560
    LED_CHECKPOINT_START = 1570
    LED_OUTPUT_START = 1580
    LED_ERROR_START = 1590

    @classmethod
    def validate(cls):
        """Validate required credentials are present"""
        missing = []

        # Reddit is required for discussions and overlap analysis
        if not cls.REDDIT_CLIENT_ID:
            missing.append('REDDIT_CLIENT_ID')
        if not cls.REDDIT_CLIENT_SECRET:
            missing.append('REDDIT_CLIENT_SECRET')

        # Amazon is required for product search
        if not cls.AMAZON_ACCESS_KEY:
            missing.append('AMAZON_ACCESS_KEY')
        if not cls.AMAZON_SECRET_KEY:
            missing.append('AMAZON_SECRET_KEY')
        if not cls.AMAZON_ASSOCIATE_TAG:
            missing.append('AMAZON_ASSOCIATE_TAG')

        # YouTube is optional (can skip if not available)
        # No validation check - fails loudly when used if missing

        if missing:
            raise ValueError(
                f"Missing required environment variables: {', '.join(missing)}\n"
                f"Please check your .env file"
            )

        return True

    @classmethod
    def adjust_for_category(cls, category: str):
        """Adjust configuration based on product category"""
        if category.lower() == 'book':
            # Books: prioritize Goodreads, Amazon, Reddit discussions
            cls.MAX_GOODREADS_RESULTS = 15
            cls.MAX_AMAZON_RESULTS = 10
            cls.MAX_YOUTUBE_VIDEOS = 5
        elif category.lower() in ['software', 'saas', 'app']:
            # Software: prioritize Reddit discussions, YouTube reviews
            cls.MAX_REDDIT_DISCUSSIONS = 30
            cls.MAX_YOUTUBE_VIDEOS = 15
            cls.MAX_AMAZON_RESULTS = 5
            cls.MAX_GOODREADS_RESULTS = 0
        elif category.lower() in ['course', 'training']:
            # Courses: prioritize YouTube reviews, Reddit discussions
            cls.MAX_YOUTUBE_VIDEOS = 20
            cls.MAX_REDDIT_DISCUSSIONS = 25
            cls.MAX_AMAZON_RESULTS = 5
            cls.MAX_GOODREADS_RESULTS = 0
        # Default: balanced approach for physical products
