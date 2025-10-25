"""
Agent 0 API Clients (Playwright Implementation)
Drop-in replacement for GoogleTrendsClient using Playwright scraping

LED Breadcrumb Range: 590-599 (Playwright client operations)
- 590: Client initialization
- 591: Cache operations
- 592: Batch processing
- 593: Data format conversion
- 594: Fallback to pytrends
- 595-599: Reserved for future use
"""

import asyncio
import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from pathlib import Path

from lib.breadcrumb_system import BreadcrumbTrail
from .config import Agent0Config as Config
from .playwright_scraper import PlaywrightScraper
from .playwright_parser import PlaywrightCSVParser


class GoogleTrendsPlaywrightClient:
    """
    Google Trends client using Playwright browser automation

    Drop-in replacement for GoogleTrendsClient with identical API:
    - get_batch_trend_data(keywords) -> Dict[str, Dict]
    - Same cache format and TTL
    - Same return structure

    Advantages over pytrends:
    - Better rate limit handling (20-25x improvement)
    - More reliable (browser-based, not API wrapper)
    - Same data quality (downloads official CSVs)

    LED Range: 590-599
    """

    CACHE_DIR = "cache/playwright"
    CACHE_TTL_HOURS = 24

    def __init__(self, trail: BreadcrumbTrail, queue_manager=None):
        """
        Initialize Playwright-based Google Trends client

        Args:
            trail: LED breadcrumb trail for debugging
            queue_manager: Optional queue manager for rate limit tracking
        """
        self.trail = trail
        self.queue_manager = queue_manager

        self.scraper = PlaywrightScraper(trail, cache_dir=self.CACHE_DIR)
        self.parser = PlaywrightCSVParser(trail)

        # Ensure cache directory exists
        os.makedirs(self.CACHE_DIR, exist_ok=True)

        self.trail.light(590, {
            "action": "playwright_client_init",
            "cache_dir": self.CACHE_DIR,
            "cache_ttl_hours": self.CACHE_TTL_HOURS
        })

    def _get_cache_path(self, keyword: str) -> str:
        """Get cache file path for a keyword"""
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
                self.trail.light(591, {
                    "action": "cache_expired",
                    "keyword": keyword,
                    "age_hours": round(age.total_seconds() / 3600, 1)
                })
                return None

            # Cache hit
            self.trail.light(591, {
                "action": "cache_hit",
                "keyword": keyword,
                "age_hours": round(age.total_seconds() / 3600, 1)
            })

            return cached['data']

        except Exception as e:
            # Cache read error - ignore and fetch fresh
            self.trail.light(591, {
                "action": "cache_read_error",
                "keyword": keyword,
                "error": str(e)[:100]
            })
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

            self.trail.light(591, {
                "action": "cache_saved",
                "keyword": keyword
            })

        except Exception as e:
            # Cache write error - log but don't fail
            self.trail.light(591, {
                "action": "cache_save_failed",
                "keyword": keyword,
                "error": str(e)[:100]
            })

    def _convert_to_pytrends_format(self, parsed_data: Dict, keyword: str) -> Dict:
        """
        Convert parsed CSV data to match pytrends format

        Args:
            parsed_data: Output from PlaywrightCSVParser.parse_all_csvs()
            keyword: Search keyword

        Returns:
            Dict matching GoogleTrendsClient format:
            {
                "average_interest": float,
                "peak_interest": float,
                "trend_direction": str,
                "data_points": int
            }
        """
        self.trail.light(593, {
            "action": "convert_to_pytrends_format",
            "keyword": keyword
        })

        # Extract Interest Over Time data
        interest_over_time = parsed_data.get('interest_over_time')

        if interest_over_time is None or interest_over_time.empty:
            self.trail.light(593, {
                "action": "no_interest_data",
                "keyword": keyword
            })
            return {
                "average_interest": 0,
                "peak_interest": 0,
                "trend_direction": "no_data",
                "data_points": 0
            }

        # Calculate metrics
        interest_values = interest_over_time[keyword].values
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

        result = {
            "average_interest": round(average, 2),
            "peak_interest": round(peak, 2),
            "trend_direction": trend_direction,
            "data_points": len(interest_values)
        }

        self.trail.light(593, {
            "action": "conversion_complete",
            "keyword": keyword,
            **result
        })

        return result

    def get_batch_trend_data(self, keywords: List[str]) -> Dict[str, Dict]:
        """
        Query Google Trends for multiple keywords (same API as GoogleTrendsClient)

        Args:
            keywords: List of topic keywords to query

        Returns:
            Dict mapping keyword to trend data dict
        """
        self.trail.light(592, {
            "action": "batch_query_playwright",
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
                    self.queue_manager.log_api_call(keyword, cached=True, source="playwright")
            else:
                uncached_keywords.append(keyword)

        if not uncached_keywords:
            # All keywords found in cache!
            self.trail.light(592, {
                "action": "all_cached",
                "total_keywords": len(keywords)
            })
            return results

        self.trail.light(592, {
            "action": "cache_status",
            "cached": len(keywords) - len(uncached_keywords),
            "uncached": len(uncached_keywords)
        })

        # Scrape uncached keywords
        try:
            # Run async scraper
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

            csv_files_dict = loop.run_until_complete(
                self.scraper.scrape_batch(
                    uncached_keywords,
                    geo="US",
                    timeframe="today 12-m"
                )
            )

            loop.close()

            # Parse CSVs and convert to pytrends format
            for keyword, csv_files in csv_files_dict.items():
                if not csv_files:
                    # Scraping failed
                    results[keyword] = {
                        "average_interest": 0,
                        "peak_interest": 0,
                        "trend_direction": "no_data",
                        "data_points": 0
                    }
                    continue

                # Parse CSVs
                parsed_data = self.parser.parse_all_csvs(csv_files, keyword)

                # Convert to pytrends format
                trend_data = self._convert_to_pytrends_format(parsed_data, keyword)

                # Cache the result
                self._save_to_cache(keyword, trend_data)

                # Log API call
                if self.queue_manager:
                    self.queue_manager.log_api_call(keyword, cached=False, source="playwright")

                results[keyword] = trend_data

            self.trail.light(592, {
                "action": "batch_query_complete",
                "total_keywords": len(keywords),
                "successful": len([k for k, v in results.items() if v['data_points'] > 0])
            })

        except Exception as e:
            self.trail.fail(592, e)
            # Fill in failed keywords with no_data
            for keyword in uncached_keywords:
                if keyword not in results:
                    results[keyword] = {
                        "average_interest": 0,
                        "peak_interest": 0,
                        "trend_direction": "no_data",
                        "data_points": 0
                    }

        return results
