"""
Agent 0 Queue Manager
Smart batch processing and rate limit tracking for Google Trends queries
"""

import json
import os
import time
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from pathlib import Path

from lib.breadcrumb_system import BreadcrumbTrail
from .config import Agent0Config as Config


class QueueManager:
    """
    Manages query queuing and rate limit tracking for Agent 0

    Features:
    - Track API call history
    - Estimate batch processing time
    - Schedule queries to respect rate limits
    - Provide next safe query time
    - Export call history for dashboard visualization
    """

    API_HISTORY_FILE = "cache/api_call_history.json"
    MAX_CALLS_PER_HOUR = 15  # Conservative limit for Google Trends
    MIN_DELAY_SECONDS = 12   # Minimum delay between requests

    def __init__(self, trail: BreadcrumbTrail):
        self.trail = trail
        self.history_file = Path(self.API_HISTORY_FILE)
        self.history_file.parent.mkdir(parents=True, exist_ok=True)

    def _load_history(self) -> List[Dict]:
        """Load API call history from JSON file"""
        if not self.history_file.exists():
            return []

        try:
            with open(self.history_file, 'r') as f:
                history = json.load(f)

            # Filter to last hour only
            one_hour_ago = time.time() - 3600
            return [call for call in history if call['timestamp'] > one_hour_ago]

        except Exception as e:
            # Silently fail - not critical
            return []

    def _save_history(self, history: List[Dict]):
        """Save API call history to JSON file"""
        try:
            with open(self.history_file, 'w') as f:
                json.dump(history, f, indent=2)
        except Exception as e:
            # Silently fail - not critical
            pass

    def log_api_call(self, keyword: str, cached: bool = False, source: str = "google_trends"):
        """
        Log an API call for rate limit tracking

        Args:
            keyword: The topic keyword queried
            cached: Whether this was a cache hit (no actual API call)
            source: API source (google_trends, reddit, youtube)
        """
        history = self._load_history()

        call_record = {
            'timestamp': time.time() * 1000,  # JavaScript timestamp (milliseconds)
            'keyword': keyword,
            'cached': cached,
            'source': source,
            'datetime': datetime.now().isoformat()
        }

        history.append(call_record)
        self._save_history(history)

    def get_calls_last_hour(self) -> Dict:
        """
        Get API call statistics for the last hour

        Returns dict with:
        - total_calls: Total queries (including cache hits)
        - actual_api_calls: Real API calls (excluding cache)
        - cache_hits: Number of cache hits
        - cache_hit_rate: Percentage of cache hits
        """
        history = self._load_history()

        total_calls = len(history)
        cache_hits = len([call for call in history if call.get('cached', False)])
        actual_api_calls = total_calls - cache_hits
        cache_hit_rate = (cache_hits / total_calls * 100) if total_calls > 0 else 0

        return {
            'total_calls': total_calls,
            'actual_api_calls': actual_api_calls,
            'cache_hits': cache_hits,
            'cache_hit_rate': round(cache_hit_rate, 1)
        }

    def get_next_safe_query_time(self) -> float:
        """
        Calculate seconds until next safe query

        Returns:
            Seconds to wait (0 if safe to query now)
        """
        history = self._load_history()

        if not history:
            return 0

        # Get timestamp of most recent call
        last_call_time = max(call['timestamp'] for call in history) / 1000  # Convert to seconds
        time_since_last = time.time() - last_call_time

        return max(0, self.MIN_DELAY_SECONDS - time_since_last)

    def estimate_batch_time(self, topics: List[str], cache_status: Optional[Dict[str, bool]] = None) -> Dict:
        """
        Estimate time required to process a batch of topics

        Args:
            topics: List of topic keywords
            cache_status: Optional dict mapping keyword to cached status
                         If None, assumes all need to be queried

        Returns:
            Dict with:
            - total_topics: Number of topics
            - cached_topics: Number already cached
            - new_queries: Number requiring API calls
            - estimated_seconds: Total time estimate
            - estimated_minutes: Total time in minutes (rounded)
        """
        total_topics = len(topics)

        # Determine how many are cached
        if cache_status:
            cached_topics = sum(1 for is_cached in cache_status.values() if is_cached)
        else:
            # Check actual cache files
            from .api_clients import GoogleTrendsClient
            dummy_trail = BreadcrumbTrail("QueueManager_CacheCheck")
            client = GoogleTrendsClient(dummy_trail)
            cached_topics = sum(1 for topic in topics if client._load_from_cache(topic) is not None)

        new_queries = total_topics - cached_topics

        # Estimate time:
        # - Cached queries: ~0.1 seconds each (file read)
        # - New queries: ~14 seconds each (12s delay + 2s API call)
        estimated_seconds = (cached_topics * 0.1) + (new_queries * 14)
        estimated_minutes = round(estimated_seconds / 60, 1)

        return {
            'total_topics': total_topics,
            'cached_topics': cached_topics,
            'new_queries': new_queries,
            'estimated_seconds': round(estimated_seconds, 1),
            'estimated_minutes': estimated_minutes
        }

    def can_process_batch(self, topics: List[str]) -> Dict:
        """
        Check if a batch can be processed safely within rate limits

        Returns:
            Dict with:
            - safe: bool - Can process now
            - reason: str - Explanation
            - wait_seconds: float - Seconds to wait if not safe
            - recommendations: List[str] - Suggested actions
        """
        stats = self.get_calls_last_hour()
        actual_calls = stats['actual_api_calls']

        # Estimate how many new API calls this batch will make
        estimate = self.estimate_batch_time(topics)
        new_api_calls = estimate['new_queries']

        total_after_batch = actual_calls + new_api_calls

        # Check against hourly limit
        if total_after_batch <= self.MAX_CALLS_PER_HOUR:
            # Check immediate delay
            wait_time = self.get_next_safe_query_time()

            if wait_time > 0:
                return {
                    'safe': False,
                    'reason': f'Need to wait {round(wait_time, 1)}s since last query',
                    'wait_seconds': wait_time,
                    'recommendations': [
                        f'Wait {round(wait_time, 1)} seconds',
                        'Or queue batch for automatic scheduling'
                    ]
                }

            return {
                'safe': True,
                'reason': f'Safe to process ({total_after_batch}/{self.MAX_CALLS_PER_HOUR} calls)',
                'wait_seconds': 0,
                'recommendations': []
            }
        else:
            # Would exceed hourly limit
            excess = total_after_batch - self.MAX_CALLS_PER_HOUR

            return {
                'safe': False,
                'reason': f'Would exceed rate limit ({total_after_batch}/{self.MAX_CALLS_PER_HOUR} calls)',
                'wait_seconds': None,  # Need to wait until hour window rolls
                'recommendations': [
                    f'Reduce batch size by {excess} topics',
                    'Or wait for call history to roll past 1-hour window',
                    f'Current rate limit usage: {actual_calls}/{self.MAX_CALLS_PER_HOUR} calls',
                    f'Cache is helping: {stats["cache_hit_rate"]}% hit rate'
                ]
            }

    def export_for_dashboard(self) -> str:
        """
        Export API call history as JavaScript code for dashboard injection

        Returns:
            JavaScript code to set localStorage
        """
        history = self._load_history()

        # Convert to JavaScript-compatible format
        js_code = f"""
        // API call history for rate limit indicator
        try {{
            localStorage.setItem('agent0_api_calls', '{json.dumps(history)}');
        }} catch (e) {{
            console.warn('Failed to save API history to localStorage:', e);
        }}
        """

        return js_code.strip()
