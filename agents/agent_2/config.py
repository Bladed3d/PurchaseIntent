"""
Agent 2 Configuration
Demographics Analyst - Extract customer profiles from reviews/comments
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class Agent2Config:
    """Configuration for Agent 2 - Demographics Analyst"""

    # API Credentials (Reddit for subreddit overlap analysis)
    REDDIT_CLIENT_ID = os.getenv('REDDIT_CLIENT_ID')
    REDDIT_CLIENT_SECRET = os.getenv('REDDIT_CLIENT_SECRET')
    REDDIT_USER_AGENT = os.getenv('REDDIT_USER_AGENT', 'Purchase-Intent-Demographics/1.0')

    # Data Collection Limits
    MAX_AMAZON_REVIEWS_PER_PRODUCT = int(os.getenv('AGENT_2_MAX_AMAZON_REVIEWS', '20'))
    MAX_REDDIT_DISCUSSIONS = int(os.getenv('AGENT_2_MAX_REDDIT_DISCUSSIONS', '10'))
    MAX_REDDIT_COMMENTS_PER_THREAD = int(os.getenv('AGENT_2_MAX_REDDIT_COMMENTS', '50'))
    MAX_YOUTUBE_COMMENTS_PER_VIDEO = int(os.getenv('AGENT_2_MAX_YOUTUBE_COMMENTS', '50'))
    MIN_DATA_POINTS_REQUIRED = int(os.getenv('AGENT_2_MIN_DATA_POINTS', '300'))

    # Demographic Extraction Settings
    BATCH_SIZE_FOR_EXTRACTION = int(os.getenv('AGENT_2_BATCH_SIZE', '20'))
    NUM_DEMOGRAPHIC_CLUSTERS = int(os.getenv('AGENT_2_NUM_CLUSTERS', '4'))

    # Confidence Thresholds
    # NOTE: MIN_DATA_SOURCES removed - intelligent pipeline handles source routing dynamically
    HIGH_CONFIDENCE_THRESHOLD = float(os.getenv('AGENT_2_HIGH_CONFIDENCE', '0.70'))  # >70% = proceed autonomously
    LOW_CONFIDENCE_THRESHOLD = float(os.getenv('AGENT_2_LOW_CONFIDENCE', '0.40'))   # <40% = fail loudly
    CONFIDENCE_THRESHOLD = float(os.getenv('AGENT_2_CONFIDENCE_THRESHOLD', '0.80'))  # Checkpoint gate threshold
    MIN_SOURCE_AGREEMENT = float(os.getenv('AGENT_2_MIN_SOURCE_AGREEMENT', '0.70'))
    MIN_BENCHMARK_MATCH = float(os.getenv('AGENT_2_MIN_BENCHMARK_MATCH', '0.80'))

    # Confidence Formula Weights
    WEIGHT_SOURCE_AGREEMENT = 0.40
    WEIGHT_SAMPLE_SIZE = 0.30
    WEIGHT_BENCHMARK_MATCH = 0.30

    # Output Paths
    OUTPUT_DIR = "agents/agent_2/outputs"

    # LED Breadcrumb Ranges (2500-2599)
    LED_INIT = 2500
    LED_SCRAPING_START = 2510
    LED_EXTRACTION_START = 2540
    LED_PIPELINE_ANALYSIS = 2545  # Tier 1 analysis
    LED_PIPELINE_DECISION = 2546  # Single-source warning
    LED_PIPELINE_CONSULTATION = 2547  # User consultation (medium confidence)
    LED_PIPELINE_FAILURE = 2548  # Low confidence failure
    LED_CLUSTERING_START = 2560
    LED_VALIDATION_START = 2570
    LED_CHECKPOINT_START = 2575
    LED_COMPLETE = 2580
    LED_ERROR_START = 2590

    @classmethod
    def validate(cls):
        """Validate required credentials are present"""
        missing = []

        # Reddit is optional for subreddit overlap, but log if missing
        if not cls.REDDIT_CLIENT_ID or not cls.REDDIT_CLIENT_SECRET:
            print("[!] WARNING: Reddit credentials not found - subreddit overlap analysis will be skipped")
            print("    Set REDDIT_CLIENT_ID and REDDIT_CLIENT_SECRET in .env for full functionality")

        # No hard requirements - Agent 2 can work with cached data from Agent 1
        return True
