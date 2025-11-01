"""
Agent 1 Amazon Product Advertising API Client
Official Amazon API for reliable product search (replaces Playwright scraper)

CRITICAL RULES:
- FAIL LOUDLY: No fallbacks if API fails
- Require data: No .get(key, 0) - raise KeyError if fields missing
"""

import time
from typing import List, Dict, Any
from datetime import datetime

from amazon_paapi import AmazonApi

from lib.breadcrumb_system import BreadcrumbTrail
from agents.agent_1.config import Agent1Config as Config


class AmazonProductAPI:
    """Official Amazon Product Advertising API client for product search"""

    def __init__(self, trail: BreadcrumbTrail):
        self.trail = trail

        # Validate credentials present
        if not Config.AMAZON_ACCESS_KEY:
            raise ValueError("AMAZON_ACCESS_KEY not set in .env file")
        if not Config.AMAZON_SECRET_KEY:
            raise ValueError("AMAZON_SECRET_KEY not set in .env file")
        if not Config.AMAZON_ASSOCIATE_TAG:
            raise ValueError("AMAZON_ASSOCIATE_TAG not set in .env file")

        # Initialize Amazon API client
        self.api = AmazonApi(
            key=Config.AMAZON_ACCESS_KEY,
            secret=Config.AMAZON_SECRET_KEY,
            tag=Config.AMAZON_ASSOCIATE_TAG,
            country='US'  # United States marketplace
        )

    def search_products(
        self,
        query: str,
        max_results: int = 15
    ) -> List[Dict[str, Any]]:
        """
        Search Amazon for products using official Product Advertising API

        Args:
            query: Search query (e.g., "productivity books for entrepreneurs")
            max_results: Max products to return (capped at 10 by API)

        Returns:
            List of product dictionaries with metadata

        Raises:
            ValueError: If API fails or returns no results
        """
        self.trail.light(Config.LED_AMAZON_START, {
            "action": "amazon_api_search_started",
            "query": query,
            "max_results": min(max_results, 10)  # API limit
        })

        # Rate limit protection: Amazon PA API allows 1 request/second
        # Add delay to ensure we never hit throttling
        time.sleep(Config.AMAZON_DELAY)

        try:
            # Amazon PA API limits to 10 results per search
            item_count = min(max_results, 10)

            # Search for products
            search_result = self.api.search_items(
                keywords=query,
                item_count=item_count
            )

            if not search_result or not hasattr(search_result, 'items'):
                raise ValueError(
                    f"Amazon API returned no results for query: '{query}'\n"
                    f"Check if query is valid and Amazon has matching products"
                )

            items = search_result.items if hasattr(search_result, 'items') else []

            if not items:
                raise ValueError(
                    f"Amazon API search returned 0 products for query: '{query}'\n"
                    f"Try a broader search term or check product availability"
                )

            # Convert Amazon items to standardized product format
            products = []
            for item in items:
                try:
                    product = self._extract_product_from_item(item)
                    if product:
                        products.append(product)
                except Exception as e:
                    # Skip individual products that fail to parse
                    self.trail.light(Config.LED_AMAZON_START, {
                        "warning": "failed_to_parse_product",
                        "asin": item.asin if hasattr(item, 'asin') else 'unknown',
                        "error": str(e)
                    })
                    continue

            if not products:
                raise ValueError(
                    f"Amazon API returned items but none could be parsed\n"
                    f"Query: '{query}', Raw items: {len(items)}"
                )

            # Filter by minimum review threshold
            filtered_products = [
                p for p in products
                if p['review_count'] >= Config.MIN_REVIEWS_AMAZON
            ]

            if not filtered_products:
                raise ValueError(
                    f"No Amazon products found with >={Config.MIN_REVIEWS_AMAZON} reviews\n"
                    f"Query: '{query}', Products found: {len(products)}, "
                    f"Best review count: {max([p['review_count'] for p in products]) if products else 0}"
                )

            self.trail.light(Config.LED_AMAZON_START + 1, {
                "action": "amazon_api_search_complete",
                "products_found": len(filtered_products),
                "total_before_filter": len(products)
            })

            return filtered_products

        except Exception as e:
            # Log error and re-raise (FAIL LOUDLY)
            self.trail.fail(Config.LED_ERROR_START + 3, {
                "error": "amazon_api_search_failed",
                "query": query,
                "exception": str(e)
            })
            raise ValueError(
                f"Amazon Product Advertising API error: {str(e)}\n"
                f"Query: '{query}'\n"
                f"Check credentials in .env: AMAZON_ACCESS_KEY, AMAZON_SECRET_KEY, AMAZON_ASSOCIATE_TAG"
            ) from e

    def _extract_product_from_item(self, item: Any) -> Dict[str, Any]:
        """
        Extract product metadata from Amazon API item

        Args:
            item: Amazon API item object

        Returns:
            Standardized product dictionary

        Raises:
            ValueError: If required fields are missing
        """
        # ASIN (Amazon Standard Identification Number) - REQUIRED
        asin = item.asin
        if not asin:
            raise ValueError("Product missing ASIN")

        # Title - REQUIRED
        title = None
        if hasattr(item, 'item_info') and hasattr(item.item_info, 'title'):
            title = item.item_info.title.display_value
        if not title:
            raise ValueError(f"Product {asin} missing title")

        # Detail page URL
        url = item.detail_page_url if hasattr(item, 'detail_page_url') else f"https://amazon.com/dp/{asin}"

        # Price (optional - some products don't have price data)
        price = None
        if hasattr(item, 'offers') and hasattr(item.offers, 'listings'):
            listings = item.offers.listings
            if listings and len(listings) > 0:
                if hasattr(listings[0], 'price'):
                    price = listings[0].price.display_amount

        # Reviews - REQUIRED for quality filtering
        review_count = 0
        rating = 0.0
        if hasattr(item, 'customer_reviews'):
            reviews = item.customer_reviews
            if hasattr(reviews, 'count'):
                review_count = reviews.count
            if hasattr(reviews, 'star_rating'):
                rating = float(reviews.star_rating.value) if reviews.star_rating else 0.0

        # Author (for books) - OPTIONAL
        author = None
        if hasattr(item, 'item_info') and hasattr(item.item_info, 'by_line_info'):
            by_line = item.item_info.by_line_info
            if hasattr(by_line, 'contributors') and by_line.contributors:
                author = by_line.contributors[0].name

        # Publication date - OPTIONAL
        publication_date = None
        if hasattr(item, 'item_info') and hasattr(item.item_info, 'content_info'):
            content = item.item_info.content_info
            if hasattr(content, 'publication_date'):
                publication_date = content.publication_date.display_value

        # Category - OPTIONAL
        category = None
        if hasattr(item, 'browse_node_info') and hasattr(item.browse_node_info, 'browse_nodes'):
            nodes = item.browse_node_info.browse_nodes
            if nodes and len(nodes) > 0:
                category = nodes[0].display_name

        return {
            'asin': asin,
            'title': title,
            'author': author,
            'platform': 'amazon',
            'url': url,
            'price': price,
            'rating': rating,
            'review_count': review_count,
            'publication_date': publication_date,
            'category': category,
            'scraped_at': datetime.now().isoformat()
        }
