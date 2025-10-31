"""
Agent 0 Configuration
Loads settings from environment variables with sensible defaults
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class Agent0Config:
    """Configuration for Agent 0 - Topic Research"""

    # API Credentials
    REDDIT_CLIENT_ID = os.getenv('REDDIT_CLIENT_ID')
    REDDIT_CLIENT_SECRET = os.getenv('REDDIT_CLIENT_SECRET')
    REDDIT_USER_AGENT = os.getenv('REDDIT_USER_AGENT', 'Purchase-Intent-Research/1.0')

    # Rate Limiting
    RATE_LIMIT_DELAY = float(os.getenv('AGENT_0_RATE_LIMIT_DELAY', '2.5'))
    GOOGLE_TRENDS_DELAY = 12.0  # Increased to 12s to avoid 429 rate limits (was 5.0)

    # Query Limits
    MAX_TOPICS = int(os.getenv('AGENT_0_MAX_TOPICS', '10'))
    MAX_REDDIT_POSTS = int(os.getenv('AGENT_0_MAX_REDDIT_POSTS', '50'))

    # Scoring Weights (sum to 1.0) - Reddit + Google Trends only
    WEIGHT_GOOGLE_TRENDS = 0.50
    WEIGHT_REDDIT = 0.50

    # Output Paths
    OUTPUT_DIR = "outputs"
    OUTPUT_JSON = os.path.join(OUTPUT_DIR, "topic-selection.json")
    OUTPUT_HTML = os.path.join(OUTPUT_DIR, "agent0-dashboard.html")

    # LED Ranges
    LED_INIT = 500
    LED_GOOGLE_TRENDS_START = 510
    LED_REDDIT_START = 520
    LED_SCORING_START = 540
    LED_DASHBOARD_START = 550
    LED_OUTPUT_START = 560
    LED_DRILL_DOWN_START = 570  # Drill-down navigation system (570-589)

    @classmethod
    def validate(cls):
        """Validate required credentials are present"""
        missing = []

        if not cls.REDDIT_CLIENT_ID:
            missing.append('REDDIT_CLIENT_ID')
        if not cls.REDDIT_CLIENT_SECRET:
            missing.append('REDDIT_CLIENT_SECRET')

        if missing:
            raise ValueError(
                f"Missing required environment variables: {', '.join(missing)}\n"
                f"Please check your .env file"
            )

        return True
