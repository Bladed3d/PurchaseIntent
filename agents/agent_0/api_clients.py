"""
Agent 0 API Clients
Handles integration with Google Trends and Reddit APIs
"""

import time
import random
import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from pytrends.request import TrendReq
import praw

from lib.breadcrumb_system import BreadcrumbTrail
from .config import Agent0Config as Config


class GoogleTrendsClient:
    """Google Trends API client using pytrends with retry logic and caching"""

    CACHE_DIR = "cache"
    CACHE_TTL_HOURS = 24

    def __init__(self, trail: BreadcrumbTrail, queue_manager=None):
        self.trail = trail
        self.queue_manager = queue_manager  # Optional queue manager for rate limit tracking
        # Initialize pytrends without retry params (handle retries ourselves)
        self.pytrends = TrendReq(hl='en-US', tz=360)

        # Ensure cache directory exists
        os.makedirs(self.CACHE_DIR, exist_ok=True)

    def _get_cache_path(self, keyword: str) -> str:
        """Get cache file path for a keyword"""
        # Sanitize keyword for filename
        safe_keyword = keyword.replace(' ', '_').replace('/', '_')
        return os.path.join(self.CACHE_DIR, f"trends_{safe_keyword}.json")

    def _load_from_cache(self, keyword: str) -> Optional[Dict]:
        """
        Load cached trend data if available and not expired

        Returns None if cache miss or expired
        """
        cache_path = self._get_cache_path(keyword)

        if not os.path.exists(cache_path):
            return None

        try:
            with open(cache_path, 'r') as f:
                cached = json.load(f)

            # Check if cache is expired (24 hour TTL)
            cached_time = datetime.fromisoformat(cached['cached_at'])
            age = datetime.now() - cached_time

            if age > timedelta(hours=self.CACHE_TTL_HOURS):
                # Cache expired
                self.trail.light(Config.LED_GOOGLE_TRENDS_START + 1, {
                    "action": "cache_expired",
                    "keyword": keyword,
                    "age_hours": round(age.total_seconds() / 3600, 1)
                })
                return None

            # Cache hit
            self.trail.light(Config.LED_GOOGLE_TRENDS_START + 1, {
                "action": "cache_hit",
                "keyword": keyword,
                "age_hours": round(age.total_seconds() / 3600, 1)
            })

            return cached['data']

        except Exception as e:
            # Cache read error - ignore and fetch fresh
            return None

    def _save_to_cache(self, keyword: str, data: Dict):
        """Save trend data to cache"""
        cache_path = self._get_cache_path(keyword)

        try:
            cached = {
                'keyword': keyword,
                'cached_at': datetime.now().isoformat(),
                'data': data
            }

            with open(cache_path, 'w') as f:
                json.dump(cached, f, indent=2)

            self.trail.light(Config.LED_GOOGLE_TRENDS_START + 1, {
                "action": "cache_saved",
                "keyword": keyword
            })

        except Exception as e:
            # Cache write error - log but don't fail
            self.trail.light(Config.LED_GOOGLE_TRENDS_START + 1, {
                "action": "cache_save_failed",
                "keyword": keyword,
                "error": str(e)[:100]
            })

    def _retry_with_backoff(self, func, *args, max_retries=3, **kwargs):
        """
        Retry a function with exponential backoff on rate limit errors

        Based on Grok research: Docs/Grok-Gtrends-limits.md
        Implements exponential backoff with jitter to handle 429 errors
        """
        for attempt in range(max_retries):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                error_str = str(e)

                # Check if it's a rate limit error (429)
                if '429' in error_str or 'Too Many Requests' in error_str or 'request failed' in error_str.lower():
                    if attempt < max_retries - 1:
                        # Exponential backoff: 2^attempt + random jitter (0-1s)
                        sleep_time = (2 ** attempt) + random.random()

                        self.trail.light(Config.LED_GOOGLE_TRENDS_START + 1, {
                            "action": "rate_limit_retry",
                            "attempt": attempt + 1,
                            "sleep_time": round(sleep_time, 2),
                            "error": error_str[:100]
                        })

                        time.sleep(sleep_time)
                    else:
                        # Max retries exceeded
                        raise Exception(f"Max retries ({max_retries}) exceeded due to rate limits: {error_str}")
                else:
                    # Not a rate limit error, re-raise immediately
                    raise e

        raise Exception("Retry logic failed unexpectedly")

    def get_batch_trend_data(self, keywords: List[str]) -> Dict[str, Dict]:
        """
        Query Google Trends for multiple keywords (individually to get absolute scores)

        IMPORTANT: Queries each keyword individually to avoid relative scoring issue
        When batching multiple keywords in one request, Google Trends returns
        relative scores (normalized 0-100 against each other), causing clustering.

        Includes 24-hour local caching to avoid redundant API calls

        Args:
            keywords: List of topic keywords to query

        Returns:
            Dict mapping keyword to trend data dict
        """
        self.trail.light(Config.LED_GOOGLE_TRENDS_START, {
            "action": "batch_query_google_trends",
            "total_keywords": len(keywords)
        })

        results = {}

        # First, check cache for all keywords
        uncached_keywords = []
        for keyword in keywords:
            cached_data = self._load_from_cache(keyword)
            if cached_data:
                results[keyword] = cached_data
                # Log cache hit
                if self.queue_manager:
                    self.queue_manager.log_api_call(keyword, cached=True)
            else:
                uncached_keywords.append(keyword)

        if not uncached_keywords:
            # All keywords found in cache!
            self.trail.light(Config.LED_GOOGLE_TRENDS_START + 2, {
                "action": "all_cached",
                "total_keywords": len(keywords)
            })
            return results

        self.trail.light(Config.LED_GOOGLE_TRENDS_START + 1, {
            "action": "cache_status",
            "cached": len(keywords) - len(uncached_keywords),
            "uncached": len(uncached_keywords)
        })

        # Query each keyword INDIVIDUALLY to get absolute scores
        for idx, keyword in enumerate(uncached_keywords, 1):
            self.trail.light(Config.LED_GOOGLE_TRENDS_START + 1, {
                "action": "querying_individual",
                "keyword": keyword,
                "progress": f"{idx}/{len(uncached_keywords)}"
            })

            try:
                # Build payload for single keyword
                def _query_single():
                    self.pytrends.build_payload([keyword], timeframe='today 12-m')
                    # Respect rate limits
                    time.sleep(Config.GOOGLE_TRENDS_DELAY)
                    return self.pytrends.interest_over_time()

                # Execute with retry logic
                data = self._retry_with_backoff(_query_single)

                if data.empty or keyword not in data.columns:
                    results[keyword] = {
                        "average_interest": 0,
                        "peak_interest": 0,
                        "trend_direction": "no_data",
                        "data_points": 0
                    }
                else:
                    interest_values = data[keyword].values
                    average = float(interest_values.mean())
                    peak = float(interest_values.max())

                    # Determine trend direction
                    mid = len(interest_values) // 2
                    first_half_avg = interest_values[:mid].mean()
                    second_half_avg = interest_values[mid:].mean()

                    if second_half_avg > first_half_avg * 1.1:
                        trend_direction = "rising"
                    elif second_half_avg < first_half_avg * 0.9:
                        trend_direction = "falling"
                    else:
                        trend_direction = "stable"

                    results[keyword] = {
                        "average_interest": round(average, 2),
                        "peak_interest": round(peak, 2),
                        "trend_direction": trend_direction,
                        "data_points": len(interest_values)
                    }

                    # Save to cache
                    self._save_to_cache(keyword, results[keyword])

                    # Log actual API call
                    if self.queue_manager:
                        self.queue_manager.log_api_call(keyword, cached=False)

            except Exception as e:
                self.trail.fail(Config.LED_GOOGLE_TRENDS_START + 2, e)
                # Return empty results for failed keyword
                results[keyword] = {
                    "average_interest": 0,
                    "peak_interest": 0,
                    "trend_direction": "error",
                    "data_points": 0,
                    "error": str(e)[:100]
                }

        self.trail.light(Config.LED_GOOGLE_TRENDS_START + 2, {
            "action": "batch_query_complete",
            "total_keywords": len(keywords),
            "successful": sum(1 for r in results.values() if r['data_points'] > 0)
        })

        return results

    def get_trend_data(self, keyword: str) -> Dict:
        """
        Query Google Trends for keyword interest over time

        Returns dict with:
        - average_interest: 0-100 score
        - peak_interest: highest interest point
        - trend_direction: 'rising', 'falling', 'stable'
        - data_points: number of data points returned
        """
        self.trail.light(Config.LED_GOOGLE_TRENDS_START, {
            "action": "query_google_trends",
            "keyword": keyword
        })

        try:
            # Build payload and query (wrapped in retry logic)
            def _query_trends():
                self.pytrends.build_payload([keyword], timeframe='today 12-m')
                # Respect rate limits
                time.sleep(Config.GOOGLE_TRENDS_DELAY)
                return self.pytrends.interest_over_time()

            # Execute with retry logic
            data = self._retry_with_backoff(_query_trends)

            if data.empty or keyword not in data.columns:
                self.trail.light(Config.LED_GOOGLE_TRENDS_START + 1, {
                    "action": "no_data",
                    "keyword": keyword
                })
                return {
                    "average_interest": 0,
                    "peak_interest": 0,
                    "trend_direction": "no_data",
                    "data_points": 0
                }

            # Calculate metrics
            interest_values = data[keyword].values
            average = float(interest_values.mean())
            peak = float(interest_values.max())

            # Determine trend direction (compare first half to second half)
            mid = len(interest_values) // 2
            first_half_avg = interest_values[:mid].mean()
            second_half_avg = interest_values[mid:].mean()

            if second_half_avg > first_half_avg * 1.1:
                trend_direction = "rising"
            elif second_half_avg < first_half_avg * 0.9:
                trend_direction = "falling"
            else:
                trend_direction = "stable"

            result = {
                "average_interest": round(average, 2),
                "peak_interest": round(peak, 2),
                "trend_direction": trend_direction,
                "data_points": len(interest_values)
            }

            self.trail.light(Config.LED_GOOGLE_TRENDS_START + 2, {
                "action": "trends_success",
                "keyword": keyword,
                **result
            })

            return result

        except Exception as e:
            self.trail.fail(Config.LED_GOOGLE_TRENDS_START + 2, e)
            return {
                "average_interest": 0,
                "peak_interest": 0,
                "trend_direction": "error",
                "data_points": 0,
                "error": str(e)
            }


class RedditClient:
    """Reddit API client using PRAW"""

    def __init__(self, trail: BreadcrumbTrail):
        self.trail = trail
        self.reddit = praw.Reddit(
            client_id=Config.REDDIT_CLIENT_ID,
            client_secret=Config.REDDIT_CLIENT_SECRET,
            user_agent=Config.REDDIT_USER_AGENT
        )

    def search_topic(self, keyword: str) -> Dict:
        """
        Search Reddit for keyword and analyze engagement

        Returns dict with:
        - total_posts: number of relevant posts found
        - total_engagement: sum of scores (upvotes - downvotes)
        - avg_engagement: average score per post
        - top_subreddits: list of most relevant subreddits
        """
        self.trail.light(Config.LED_REDDIT_START, {
            "action": "search_reddit",
            "keyword": keyword
        })

        try:
            # Search across all of Reddit
            posts = list(self.reddit.subreddit('all').search(
                keyword,
                limit=Config.MAX_REDDIT_POSTS,
                sort='relevance'
            ))

            # Respect rate limits
            time.sleep(Config.RATE_LIMIT_DELAY)

            if not posts:
                self.trail.light(Config.LED_REDDIT_START + 1, {
                    "action": "no_posts",
                    "keyword": keyword
                })
                return {
                    "total_posts": 0,
                    "total_engagement": 0,
                    "avg_engagement": 0,
                    "top_subreddits": []
                }

            # Calculate metrics
            total_engagement = sum(post.score for post in posts)
            avg_engagement = total_engagement / len(posts) if posts else 0

            # Find top subreddits
            subreddit_counts = {}
            for post in posts:
                sub = post.subreddit.display_name
                subreddit_counts[sub] = subreddit_counts.get(sub, 0) + 1

            top_subreddits = sorted(
                subreddit_counts.items(),
                key=lambda x: x[1],
                reverse=True
            )[:5]

            # Collect timestamp data for recency analysis
            timestamps = [post.created_utc for post in posts]

            result = {
                "total_posts": len(posts),
                "total_engagement": total_engagement,
                "avg_engagement": round(avg_engagement, 2),
                "top_subreddits": [{"name": name, "count": count} for name, count in top_subreddits],
                "timestamps": timestamps  # NEW: for recency calculation
            }

            self.trail.light(Config.LED_REDDIT_START + 2, {
                "action": "reddit_success",
                "keyword": keyword,
                **result
            })

            return result

        except Exception as e:
            self.trail.fail(Config.LED_REDDIT_START + 2, e)
            return {
                "total_posts": 0,
                "total_engagement": 0,
                "avg_engagement": 0,
                "top_subreddits": [],
                "error": str(e)
            }


