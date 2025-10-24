"""
Agent 0 Web Search Client
Google Trends alternative using web search for trend signals

LED Breadcrumb Range: 600-609 (Web Search Client)
- 600: Client initialization
- 601: Cache check
- 602: Web search query execution
- 603: Search results received
- 604: Result parsing
- 605: Trend signal extraction
- 606: Data conversion complete
- 607: Cache save
- 608: Error handling
- 609: Cleanup
"""

import json
import time
from typing import List, Dict, Optional
from pathlib import Path
import pandas as pd

from lib.breadcrumb_system import BreadcrumbTrail
from .websearch_analyzer import WebSearchAnalyzer


class GoogleTrendsWebSearchClient:
    """
    Drop-in replacement for GoogleTrendsClient using web search

    Features:
    - Web search for trend signals (Forbes, Healthline, Reddit mentions)
    - 24-hour caching (same as other methods)
    - No rate limits
    - LED breadcrumb instrumentation
    - PyTrends-compatible output format

    Usage:
        client = GoogleTrendsWebSearchClient(trail, web_search_func)
        data = client.get_batch_trend_data(['meditation', 'yoga'])
    """

    def __init__(
        self,
        trail: BreadcrumbTrail,
        cache_dir: str = "cache/websearch",
        cache_ttl_hours: int = 24
    ):
        """
        Initialize web search client

        Args:
            trail: LED breadcrumb trail for debugging
            cache_dir: Directory for cached results
            cache_ttl_hours: Cache time-to-live in hours

        Note:
            This implementation uses the googlesearch-python library
            Install with: pip install googlesearch-python
        """
        self.trail = trail
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.cache_ttl_seconds = cache_ttl_hours * 3600

        self.analyzer = WebSearchAnalyzer(trail)

        # Try to import googlesearch
        try:
            from googlesearch import search
            self.search_func = search
            self.search_available = True
        except ImportError:
            self.trail.light(608, {
                "action": "import_error",
                "message": "googlesearch-python not installed. Install with: pip install googlesearch-python"
            })
            self.search_available = False
            self.search_func = None

        self.trail.light(600, {
            "action": "websearch_client_init",
            "cache_dir": str(self.cache_dir),
            "cache_ttl_hours": cache_ttl_hours,
            "search_available": self.search_available
        })

    def get_batch_trend_data(self, keywords: List[str]) -> Dict[str, pd.DataFrame]:
        """
        Get trend data for multiple keywords using web search

        This is the main interface - same as other clients (pytrends, playwright)

        Args:
            keywords: List of keywords to research

        Returns:
            Dict mapping keyword to DataFrame with trend data
        """
        results = {}

        for keyword in keywords:
            try:
                # Check cache first
                cached_data = self._check_cache(keyword)
                if cached_data:
                    self.trail.light(601, {
                        "action": "cache_hit",
                        "keyword": keyword
                    })
                    results[keyword] = cached_data
                    continue

                # Execute web searches
                search_results = self._search_keyword(keyword)

                # Analyze results
                analysis = self.analyzer.analyze_keyword(keyword, search_results)

                # Convert to PyTrends format
                df = self.analyzer.convert_to_pytrends_format(keyword, analysis)

                # Cache the results
                self._save_cache(keyword, df, analysis)

                results[keyword] = df

                self.trail.light(606, {
                    "action": "keyword_complete",
                    "keyword": keyword,
                    "demand_score": analysis['demand_score'],
                    "confidence": analysis['confidence']
                })

            except Exception as e:
                self.trail.light(608, {
                    "action": "error",
                    "keyword": keyword,
                    "error": str(e)
                })
                # Return empty DataFrame on error
                results[keyword] = pd.DataFrame()

        return results

    def _search_keyword(self, keyword: str) -> List[Dict]:
        """
        Execute web searches for a keyword to gather trend signals

        Strategy (from Grok's recommendation):
        1. Search for trend articles (Forbes, Healthline, Statista)
        2. Search for Reddit/forum discussions
        3. Search for engagement indicators (viral, trending, etc.)

        Args:
            keyword: The keyword to search

        Returns:
            List of search result dicts
        """
        self.trail.light(602, {
            "action": "search_start",
            "keyword": keyword
        })

        all_results = []

        # Query 1: Trend articles from trusted sources
        query1 = f"top trends in {keyword} 2025 site:forbes.com OR site:healthline.com OR site:statista.com"
        results1 = self._execute_search(query1, max_results=5)
        all_results.extend(results1)

        # Query 2: Reddit/Medium discussions
        query2 = f'"{keyword}" demand trends 2025 site:reddit.com OR site:medium.com'
        results2 = self._execute_search(query2, max_results=5)
        all_results.extend(results2)

        # Query 3: Engagement indicators
        query3 = f'"{keyword}" popular viral trending 2025'
        results3 = self._execute_search(query3, max_results=5)
        all_results.extend(results3)

        self.trail.light(603, {
            "action": "search_complete",
            "keyword": keyword,
            "total_results": len(all_results)
        })

        return all_results

    def _execute_search(self, query: str, max_results: int = 10) -> List[Dict]:
        """
        Execute a single web search query using googlesearch-python

        Args:
            query: The search query
            max_results: Maximum results to return

        Returns:
            List of result dicts with title, url, snippet
        """
        if not self.search_available:
            self.trail.light(608, {
                "action": "search_unavailable",
                "message": "googlesearch-python not installed"
            })
            return []

        try:
            # Use googlesearch library
            # Returns URLs only, we'll extract title/snippet from URL
            import time
            time.sleep(2)  # Rate limiting (be respectful)

            urls = list(self.search_func(query, num_results=max_results, lang="en"))

            # Parse results
            parsed_results = []
            for url in urls[:max_results]:
                # Extract domain as title (googlesearch doesn't provide title/snippet)
                domain = url.split('/')[2] if len(url.split('/')) > 2 else url
                parsed_results.append({
                    'title': domain,
                    'url': url,
                    'snippet': f"Result from {domain}"
                })

            self.trail.light(604, {
                "action": "search_parsed",
                "query": query[:50] + "...",
                "result_count": len(parsed_results)
            })

            return parsed_results

        except Exception as e:
            self.trail.light(608, {
                "action": "search_error",
                "query": query[:50] + "...",
                "error": str(e)
            })
            return []

    def _check_cache(self, keyword: str) -> Optional[pd.DataFrame]:
        """
        Check if cached data exists and is still valid

        Args:
            keyword: The keyword to check

        Returns:
            Cached DataFrame if valid, None otherwise
        """
        cache_file = self.cache_dir / f"{self._sanitize_filename(keyword)}.json"

        if not cache_file.exists():
            return None

        # Check age
        age = time.time() - cache_file.stat().st_mtime
        if age > self.cache_ttl_seconds:
            return None

        # Load cached data
        try:
            with open(cache_file, 'r') as f:
                cache_data = json.load(f)

            # Reconstruct DataFrame
            df = pd.DataFrame(cache_data['dataframe'])

            return df

        except Exception:
            return None

    def _save_cache(self, keyword: str, df: pd.DataFrame, analysis: Dict):
        """
        Save search results to cache

        Args:
            keyword: The keyword
            df: The DataFrame with trend data
            analysis: The analysis results
        """
        cache_file = self.cache_dir / f"{self._sanitize_filename(keyword)}.json"

        cache_data = {
            'keyword': keyword,
            'timestamp': time.time(),
            'dataframe': df.to_dict(),
            'analysis': analysis
        }

        try:
            with open(cache_file, 'w') as f:
                json.dump(cache_data, f, indent=2)

            self.trail.light(607, {
                "action": "cache_saved",
                "keyword": keyword,
                "cache_file": str(cache_file)
            })

        except Exception as e:
            self.trail.light(608, {
                "action": "cache_save_error",
                "keyword": keyword,
                "error": str(e)
            })

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
