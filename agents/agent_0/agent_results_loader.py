"""
Agent 0 Agent Results Loader
Loads AI agent research results from cache files

LED Breadcrumb Range: 620-629 (Agent Results Loading)
- 620: Loader initialization
- 621: Cache check
- 622: Results loaded
- 623: Results parsing
- 624: Data conversion
- 625: Validation
- 626: Conversion complete
- 627: Cache miss
- 628: Error handling
- 629: Cleanup
"""

import json
import time
from typing import Optional, Dict
from pathlib import Path
import pandas as pd

from lib.breadcrumb_system import BreadcrumbTrail


class AgentResultsLoader:
    """
    Loads AI agent research results from cache files

    Agent results provide web search trend signals to replace Google Trends.
    Results are cached permanently and can be used across sessions.

    File format (JSON):
    {
        "keyword": "meditation",
        "demand_score": 87,
        "confidence": 92,
        "signals": {
            "mention_count": 94,
            "source_quality": 88,
            "recency_score": 95,
            "engagement_score": 91
        },
        "top_sources": [...]
    }
    """

    def __init__(self, trail: BreadcrumbTrail, cache_dir: str = "cache/agent_results"):
        """
        Initialize agent results loader

        Args:
            trail: LED breadcrumb trail for debugging
            cache_dir: Directory containing agent result JSON files
        """
        self.trail = trail
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)

        self.trail.light(620, {
            "action": "loader_init",
            "cache_dir": str(self.cache_dir)
        })

    def load_results(self, keyword: str) -> Optional[Dict]:
        """
        Load agent research results for a keyword

        Args:
            keyword: The keyword to load results for

        Returns:
            Dict with agent results, or None if not found
        """
        cache_file = self.cache_dir / f"{self._sanitize_filename(keyword)}.json"

        self.trail.light(621, {
            "action": "cache_check",
            "keyword": keyword,
            "cache_file": str(cache_file)
        })

        if not cache_file.exists():
            self.trail.light(627, {
                "action": "cache_miss",
                "keyword": keyword
            })
            return None

        try:
            # Load JSON file
            with open(cache_file, 'r') as f:
                data = json.load(f)

            self.trail.light(622, {
                "action": "results_loaded",
                "keyword": keyword,
                "demand_score": data.get('demand_score', 0),
                "confidence": data.get('confidence', 0)
            })

            # Validate structure
            if not self._validate_results(data):
                self.trail.light(628, {
                    "action": "validation_error",
                    "keyword": keyword,
                    "message": "Invalid result structure"
                })
                return None

            self.trail.light(625, {
                "action": "validation_passed",
                "keyword": keyword
            })

            return data

        except Exception as e:
            self.trail.light(628, {
                "action": "load_error",
                "keyword": keyword,
                "error": str(e)
            })
            return None

    def convert_to_trends_format(self, keyword: str, agent_results: Dict) -> pd.DataFrame:
        """
        Convert agent results to Google Trends-compatible DataFrame format

        This allows agent results to be used in place of Google Trends data
        in the existing scoring system.

        Args:
            keyword: The keyword
            agent_results: Agent research results dict

        Returns:
            DataFrame compatible with existing trends processing
        """
        self.trail.light(624, {
            "action": "convert_to_trends_format",
            "keyword": keyword
        })

        # Create simple DataFrame with demand score
        # The scoring system will extract the value it needs
        df = pd.DataFrame({
            keyword: [agent_results.get('demand_score', 0)]
        })

        self.trail.light(626, {
            "action": "conversion_complete",
            "keyword": keyword,
            "demand_score": agent_results.get('demand_score', 0)
        })

        return df

    def get_result_age_hours(self, keyword: str) -> Optional[float]:
        """
        Get age of cached agent results in hours

        Args:
            keyword: The keyword

        Returns:
            Age in hours, or None if not cached
        """
        cache_file = self.cache_dir / f"{self._sanitize_filename(keyword)}.json"

        if not cache_file.exists():
            return None

        age_seconds = time.time() - cache_file.stat().st_mtime
        return age_seconds / 3600.0

    def _validate_results(self, data: Dict) -> bool:
        """
        Validate agent results structure

        Args:
            data: Results dict to validate

        Returns:
            True if valid, False otherwise
        """
        required_fields = ['keyword', 'demand_score', 'confidence', 'signals']

        for field in required_fields:
            if field not in data:
                return False

        # Validate signals structure
        if 'signals' in data:
            signals = data['signals']
            required_signals = ['mention_count', 'source_quality', 'recency_score', 'engagement_score']
            for signal in required_signals:
                if signal not in signals:
                    return False

        return True

    def _sanitize_filename(self, keyword: str) -> str:
        """
        Sanitize keyword for use as filename

        Args:
            keyword: The keyword

        Returns:
            Sanitized filename
        """
        # Replace spaces and special chars with underscores
        sanitized = keyword.lower().replace(' ', '_')
        sanitized = ''.join(c if c.isalnum() or c == '_' else '_' for c in sanitized)
        return sanitized
