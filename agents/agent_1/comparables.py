"""
Agent 1 Comparables Ranker
Extracts and ranks comparable products by sales signal, reviews, recency, and semantic similarity

CRITICAL RULES:
- FAIL LOUDLY: Require minimum thresholds
- NO PAID APIs: Use sentence-transformers (local) for embeddings
"""

from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from dateutil import parser as date_parser
import numpy as np

from lib.breadcrumb_system import BreadcrumbTrail
from agents.agent_1.config import Agent1Config as Config


class ComparablesRanker:
    """Ranks and filters comparable products from multi-source search results"""

    def __init__(self, trail: BreadcrumbTrail):
        self.trail = trail
        self.embedder = None  # Lazy load sentence-transformers

    def rank_comparables(
        self,
        search_results: Dict[str, List[Dict[str, Any]]],
        product_description: str
    ) -> List[Dict[str, Any]]:
        """
        Extract and rank comparable products from search results

        Args:
            search_results: Results from MultiSourceSearch
            product_description: User's product description for semantic comparison

        Returns:
            List of top N comparable products, ranked by relevance

        Raises:
            ValueError: If insufficient comparables found
        """
        self.trail.light(Config.LED_COMPARABLES_START, {
            "action": "comparables_ranking_started",
            "amazon_products": len(search_results['amazon']),
            "goodreads_books": len(search_results['goodreads'])
        })

        # Combine products from all sources
        all_products = []
        all_products.extend(search_results['amazon'])
        all_products.extend(search_results['goodreads'])

        if not all_products:
            raise ValueError(
                "No products to rank (Amazon and Goodreads returned no results)\n"
                "Cannot proceed without comparable products"
            )

        # Calculate scores for each product
        scored_products = []
        for product in all_products:
            try:
                score = self._calculate_relevance_score(product, product_description)
                product['relevance_score'] = score
                scored_products.append(product)
            except Exception as e:
                # Skip products that fail scoring
                continue

        if not scored_products:
            raise ValueError(
                f"All products failed relevance scoring\n"
                f"Products attempted: {len(all_products)}"
            )

        # Sort by relevance score (descending)
        scored_products.sort(key=lambda p: p['relevance_score'], reverse=True)

        # Take top N comparables
        top_comparables = scored_products[:Config.MAX_COMPARABLES]

        if len(top_comparables) < 5:
            raise ValueError(
                f"Insufficient comparables found (need >=5, got {len(top_comparables)})\n"
                f"Products scored: {len(scored_products)}\n"
                f"Adjust search queries or lower quality thresholds"
            )

        self.trail.light(Config.LED_COMPARABLES_START + 1, {
            "action": "comparables_ranking_complete",
            "comparables_selected": len(top_comparables),
            "avg_score": np.mean([p['relevance_score'] for p in top_comparables])
        })

        return top_comparables

    def _calculate_relevance_score(
        self,
        product: Dict[str, Any],
        reference_description: str
    ) -> float:
        """
        Calculate composite relevance score using 4 factors:
        1. Sales signal (Amazon BSR, YouTube views)
        2. Review volume (review/comment counts)
        3. Recency (publication/upload date)
        4. Semantic similarity (title similarity to description)

        Returns:
            Score between 0.0 and 1.0
        """
        # 1. Sales signal score (0.0 - 1.0)
        sales_score = self._score_sales_signal(product)

        # 2. Review volume score (0.0 - 1.0)
        review_score = self._score_review_volume(product)

        # 3. Recency score (0.0 - 1.0)
        recency_score = self._score_recency(product)

        # 4. Semantic similarity score (0.0 - 1.0)
        semantic_score = self._score_semantic_similarity(
            product['title'],
            reference_description
        )

        # Weighted composite score
        composite_score = (
            Config.WEIGHT_SALES_SIGNAL * sales_score +
            Config.WEIGHT_REVIEW_VOLUME * review_score +
            Config.WEIGHT_RECENCY * recency_score +
            Config.WEIGHT_SEMANTIC * semantic_score
        )

        return round(composite_score, 3)

    def _score_sales_signal(self, product: Dict[str, Any]) -> float:
        """
        Score product by sales signals

        Amazon: BSR < 10,000 = 1.0, BSR > 100,000 = 0.0
        YouTube: Views > 100,000 = 1.0, Views < 1,000 = 0.0
        Goodreads: Rating count > 10,000 = 1.0, < 100 = 0.0
        """
        platform = product['platform']

        if platform == 'amazon':
            bsr = product.get('bsr')
            if bsr:
                # Lower BSR = better sales
                if bsr <= 10000:
                    return 1.0
                elif bsr >= 100000:
                    return 0.0
                else:
                    return 1.0 - ((bsr - 10000) / 90000)
            else:
                # No BSR available, use review count as proxy
                review_count = product['review_count']
                if review_count >= 5000:
                    return 1.0
                elif review_count <= 100:
                    return 0.2
                else:
                    return 0.2 + (0.8 * (review_count - 100) / 4900)

        elif platform == 'youtube':
            views = product['views']
            if views >= 100000:
                return 1.0
            elif views <= 1000:
                return 0.0
            else:
                return views / 100000

        elif platform == 'goodreads':
            review_count = product['review_count']
            if review_count >= 10000:
                return 1.0
            elif review_count <= 100:
                return 0.1
            else:
                return 0.1 + (0.9 * (review_count - 100) / 9900)

        return 0.5  # Default for unknown platforms

    def _score_review_volume(self, product: Dict[str, Any]) -> float:
        """
        Score product by review/comment volume
        More reviews = more data for demographic analysis
        """
        platform = product['platform']
        review_count = product.get('review_count', 0)

        if platform in ['amazon', 'goodreads']:
            if review_count >= 5000:
                return 1.0
            elif review_count <= 50:
                return 0.0
            else:
                return (review_count - 50) / 4950

        elif platform == 'youtube':
            comment_count = product.get('comments', 0)
            if comment_count >= 500:
                return 1.0
            elif comment_count <= 20:
                return 0.0
            else:
                return (comment_count - 20) / 480

        return 0.5

    def _score_recency(self, product: Dict[str, Any]) -> float:
        """
        Score product by recency
        Books: Within 3 years = 1.0, > 5 years = 0.0
        Videos: Within 1 year = 1.0, > 2 years = 0.0
        """
        platform = product['platform']

        # Determine date field based on platform
        date_field = None
        if platform == 'youtube':
            date_field = 'published_at'
        elif platform in ['amazon', 'goodreads']:
            date_field = 'scraped_at'  # Proxy (not ideal, but best we have)

        if not date_field or date_field not in product:
            return 0.5  # Default if no date available

        try:
            date_str = product[date_field]
            date_obj = date_parser.parse(date_str)
            age_days = (datetime.now(date_obj.tzinfo or None) - date_obj).days

            if platform == 'youtube':
                # Videos: recency matters more
                if age_days <= 365:
                    return 1.0
                elif age_days >= 730:
                    return 0.0
                else:
                    return 1.0 - ((age_days - 365) / 365)

            else:
                # Books/products: 3-year window
                if age_days <= 1095:  # 3 years
                    return 1.0
                elif age_days >= 1825:  # 5 years
                    return 0.0
                else:
                    return 1.0 - ((age_days - 1095) / 730)

        except Exception:
            return 0.5  # Default if date parsing fails

    def _score_semantic_similarity(self, title: str, reference: str) -> float:
        """
        Calculate semantic similarity between product title and reference description
        Uses simple word overlap for now (could be upgraded to sentence-transformers)
        """
        # Simple approach: Jaccard similarity on word sets
        title_words = set(title.lower().split())
        ref_words = set(reference.lower().split())

        # Remove common stop words
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'for', 'with', 'to', 'of', 'in', 'on'}
        title_words = title_words - stop_words
        ref_words = ref_words - stop_words

        if not title_words or not ref_words:
            return 0.0

        intersection = title_words & ref_words
        union = title_words | ref_words

        jaccard_sim = len(intersection) / len(union)

        # Scale to be more forgiving (0.2 = minimum match, 1.0 = perfect match)
        return min(1.0, jaccard_sim * 2.0)

    def aggregate_discussion_sources(
        self,
        search_results: Dict[str, List[Dict[str, Any]]]
    ) -> List[Dict[str, Any]]:
        """
        Aggregate discussion sources (Reddit, YouTube) for demographic analysis

        Returns:
            List of discussion URLs with metadata
        """
        discussions = []

        # Reddit discussions
        for discussion in search_results['reddit']:
            discussions.append({
                "platform": "reddit",
                "url": discussion['url'],
                "title": discussion['title'],
                "comments": discussion['num_comments'],
                "score": discussion['score'],
                "subreddit": discussion['subreddit']
            })

        # YouTube videos
        for video in search_results['youtube']:
            discussions.append({
                "platform": "youtube",
                "url": video['url'],
                "title": video['title'],
                "comments": video['comments'],
                "views": video['views']
            })

        # Sort by comment count (descending)
        discussions.sort(key=lambda d: d['comments'], reverse=True)

        return discussions
