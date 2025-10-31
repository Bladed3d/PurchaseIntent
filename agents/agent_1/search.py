"""
Agent 1 Multi-Source Search Orchestrator
Coordinates parallel searches across Amazon, Reddit, YouTube, Goodreads

CRITICAL RULES:
- FAIL LOUDLY: No fallbacks if search fails
- Parallel execution for speed where possible
"""

import time
from typing import List, Dict, Any, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed

from lib.breadcrumb_system import BreadcrumbTrail
from agents.agent_1.config import Agent1Config as Config
from agents.agent_1.api_clients import RedditClient, YouTubeClient
from agents.agent_1.playwright_scraper import AmazonScraper, GoodreadsScraper


class MultiSourceSearch:
    """Orchestrates product searches across multiple platforms"""

    def __init__(self, trail: BreadcrumbTrail):
        self.trail = trail
        self.reddit_client = RedditClient(trail)
        self.amazon_scraper = AmazonScraper(trail)

        # Optional clients (fail only when used if not configured)
        self.youtube_client = None
        self.goodreads_scraper = None

    def search_all_sources(
        self,
        product_description: str,
        product_category: str = "general",
        enable_youtube: bool = True,
        enable_goodreads: bool = False
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        Execute parallel searches across all enabled sources

        Args:
            product_description: User's product description
            product_category: Product category (book, software, course, general)
            enable_youtube: Whether to search YouTube (costs quota)
            enable_goodreads: Whether to search Goodreads (books only)

        Returns:
            Dictionary with results from each source

        Raises:
            ValueError: If all searches fail or return insufficient data
        """
        # Adjust config for category
        Config.adjust_for_category(product_category)

        # Generate search queries
        queries = self._generate_search_queries(product_description, product_category)

        self.trail.light(Config.LED_INIT + 1, {
            "action": "multi_source_search_started",
            "product_description": product_description,
            "category": product_category,
            "queries": queries
        })

        # Determine which sources to use
        sources_to_search = ['amazon', 'reddit']
        if enable_youtube and Config.YOUTUBE_API_KEY:
            sources_to_search.append('youtube')
        if enable_goodreads and product_category.lower() == 'book':
            sources_to_search.append('goodreads')

        # Execute searches in parallel
        results = {
            'amazon': [],
            'reddit': [],
            'youtube': [],
            'goodreads': []
        }

        with ThreadPoolExecutor(max_workers=4) as executor:
            futures = {}

            # Submit search tasks
            if 'amazon' in sources_to_search:
                futures['amazon'] = executor.submit(
                    self._safe_search_amazon,
                    queries['amazon']
                )

            if 'reddit' in sources_to_search:
                futures['reddit'] = executor.submit(
                    self._safe_search_reddit,
                    queries['reddit']
                )

            if 'youtube' in sources_to_search:
                futures['youtube'] = executor.submit(
                    self._safe_search_youtube,
                    queries['youtube']
                )

            if 'goodreads' in sources_to_search:
                futures['goodreads'] = executor.submit(
                    self._safe_search_goodreads,
                    queries['goodreads']
                )

            # Collect results
            for source, future in futures.items():
                try:
                    results[source] = future.result()
                except Exception as e:
                    # Fail loudly for each source
                    self.trail.fail(Config.LED_ERROR_START + 5, e)
                    print(f"[!] {source.title()} search failed: {str(e)}")
                    # Continue with other sources - we need at least one to succeed

        # Validate we have sufficient data
        total_products = len(results['amazon']) + len(results['goodreads'])
        total_discussions = len(results['reddit']) + len(results['youtube'])

        if total_products == 0:
            raise ValueError(
                f"No products found from any source\n"
                f"Query: '{product_description}'\n"
                f"Tried sources: {sources_to_search}\n"
                f"All product searches failed"
            )

        if total_discussions == 0:
            raise ValueError(
                f"No discussions found from any source\n"
                f"Query: '{product_description}'\n"
                f"Tried sources: {sources_to_search}\n"
                f"Need Reddit or YouTube discussions for demographic analysis"
            )

        self.trail.light(Config.LED_INIT + 2, {
            "action": "multi_source_search_complete",
            "products_found": total_products,
            "discussions_found": total_discussions,
            "sources_used": sources_to_search
        })

        return results

    def _generate_search_queries(
        self,
        product_description: str,
        category: str
    ) -> Dict[str, str]:
        """Generate optimized search queries for each platform"""

        # Base query cleanup
        base_query = product_description.lower().strip()

        # Platform-specific optimizations
        queries = {
            'amazon': base_query,
            'reddit': f"{base_query} recommendation",
            'youtube': f"best {base_query} review 2024",
            'goodreads': base_query.replace('book', '').strip()  # Remove redundant "book"
        }

        # Category-specific adjustments
        if category == 'book':
            queries['reddit'] = f"book recommendation {base_query}"
            queries['youtube'] = f"book review {base_query}"

        elif category in ['software', 'saas', 'app']:
            queries['amazon'] = f"{base_query} software"
            queries['reddit'] = f"{base_query} software review"
            queries['youtube'] = f"{base_query} demo review"

        elif category in ['course', 'training']:
            queries['reddit'] = f"{base_query} course review"
            queries['youtube'] = f"{base_query} course review"

        return queries

    def _safe_search_amazon(self, query: str) -> List[Dict[str, Any]]:
        """Wrapper for Amazon search with error handling"""
        try:
            return self.amazon_scraper.search_products(query, Config.MAX_AMAZON_RESULTS)
        except Exception as e:
            # Re-raise to propagate to executor
            raise ValueError(f"Amazon search failed: {str(e)}")

    def _safe_search_reddit(self, query: str) -> List[Dict[str, Any]]:
        """Wrapper for Reddit search with error handling"""
        try:
            return self.reddit_client.search_product_discussions(
                query,
                subreddits=None,  # Search all subreddits
                limit=Config.MAX_REDDIT_DISCUSSIONS
            )
        except Exception as e:
            raise ValueError(f"Reddit search failed: {str(e)}")

    def _safe_search_youtube(self, query: str) -> List[Dict[str, Any]]:
        """Wrapper for YouTube search with error handling"""
        try:
            if not self.youtube_client:
                self.youtube_client = YouTubeClient(self.trail)
            return self.youtube_client.search_product_reviews(query, Config.MAX_YOUTUBE_VIDEOS)
        except Exception as e:
            raise ValueError(f"YouTube search failed: {str(e)}")

    def _safe_search_goodreads(self, query: str) -> List[Dict[str, Any]]:
        """Wrapper for Goodreads search with error handling"""
        try:
            if not self.goodreads_scraper:
                self.goodreads_scraper = GoodreadsScraper(self.trail)
            return self.goodreads_scraper.search_books(query, Config.MAX_GOODREADS_RESULTS)
        except Exception as e:
            raise ValueError(f"Goodreads search failed: {str(e)}")


class SubredditDetector:
    """Detects relevant subreddits from product description"""

    @staticmethod
    def detect_subreddits(product_description: str, category: str) -> List[str]:
        """
        Suggest relevant subreddits based on product description

        Args:
            product_description: User's product description
            category: Product category

        Returns:
            List of suggested subreddit names
        """
        subreddits = []

        # Category-based defaults
        if category == 'book':
            subreddits.extend(['books', 'suggestmeabook', 'booksuggestions'])

        elif category in ['software', 'saas', 'app']:
            subreddits.extend(['software', 'saas', 'entrepreneur'])

        elif category in ['course', 'training']:
            subreddits.extend(['learnprogramming', 'education', 'courses'])

        # Keyword-based detection
        keywords_to_subs = {
            'productivity': ['productivity', 'getdisciplined'],
            'entrepreneur': ['entrepreneur', 'smallbusiness', 'startups'],
            'fitness': ['fitness', 'bodyweightfitness', 'loseit'],
            'programming': ['learnprogramming', 'coding', 'cscareerquestions'],
            'finance': ['personalfinance', 'investing', 'financialindependence'],
            'marketing': ['marketing', 'socialmedia', 'seo'],
            'design': ['design', 'graphic_design', 'web_design'],
            'writing': ['writing', 'writers', 'selfpublish'],
        }

        for keyword, subs in keywords_to_subs.items():
            if keyword in product_description.lower():
                subreddits.extend(subs)

        # Remove duplicates, keep order
        seen = set()
        unique_subreddits = []
        for sub in subreddits:
            if sub not in seen:
                seen.add(sub)
                unique_subreddits.append(sub)

        return unique_subreddits[:5]  # Limit to top 5
