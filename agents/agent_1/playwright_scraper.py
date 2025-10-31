"""
Agent 1 Playwright Scraper
Web scraping for Amazon and Goodreads product data

CRITICAL RULES:
- FAIL LOUDLY: No fallbacks if scraping fails
- Require data: No .get(key, 0) - raise KeyError if fields missing
"""

import time
import re
from typing import List, Dict, Any, Optional
from datetime import datetime
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout, Page

from lib.breadcrumb_system import BreadcrumbTrail
from agents.agent_1.config import Agent1Config as Config


class AmazonScraper:
    """Playwright-based Amazon scraper for product search"""

    def __init__(self, trail: BreadcrumbTrail):
        self.trail = trail

    def search_products(
        self,
        query: str,
        max_results: int = 15
    ) -> List[Dict[str, Any]]:
        """
        Scrape Amazon search results for comparable products

        Args:
            query: Search query (e.g., "productivity books for entrepreneurs")
            max_results: Max products to return

        Returns:
            List of product dictionaries with metadata

        Raises:
            ValueError: If scraping fails or returns no results
        """
        self.trail.light(Config.LED_AMAZON_START, {
            "action": "amazon_scrape_started",
            "query": query,
            "max_results": max_results
        })

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0")

            try:
                # Navigate to Amazon search
                search_url = f"https://www.amazon.com/s?k={query.replace(' ', '+')}"
                page.goto(search_url, timeout=30000)

                # Wait for results to load
                page.wait_for_selector('[data-component-type="s-search-result"]', timeout=10000)

                # Extract product cards
                products = []
                result_cards = page.query_selector_all('[data-component-type="s-search-result"]')

                for card in result_cards[:max_results]:
                    try:
                        product = self._extract_product_from_card(card)
                        if product:
                            products.append(product)
                    except Exception as e:
                        # Skip individual products that fail to parse
                        continue

                browser.close()

                if not products:
                    raise ValueError(
                        f"Amazon scraping returned no products for query: '{query}'\n"
                        f"URL: {search_url}\n"
                        f"Possible anti-bot detection or rate limiting"
                    )

                # Filter by minimum review threshold
                filtered_products = [p for p in products if p['review_count'] >= Config.MIN_REVIEWS_AMAZON]

                if not filtered_products:
                    raise ValueError(
                        f"No Amazon products found with >={Config.MIN_REVIEWS_AMAZON} reviews\n"
                        f"Query: '{query}', Products found: {len(products)}"
                    )

                self.trail.light(Config.LED_AMAZON_START + 1, {
                    "action": "amazon_scrape_complete",
                    "products_found": len(filtered_products)
                })

                return filtered_products

            except PlaywrightTimeout as e:
                browser.close()
                self.trail.fail(Config.LED_ERROR_START + 3, e)
                raise ValueError(
                    f"Amazon scraping timed out for query: '{query}'\n"
                    f"URL: {search_url}\n"
                    f"Error: {str(e)}"
                )
            except Exception as e:
                browser.close()
                self.trail.fail(Config.LED_ERROR_START + 3, e)
                raise ValueError(f"Amazon scraping failed: {str(e)}")

    def _extract_product_from_card(self, card) -> Optional[Dict[str, Any]]:
        """Extract product data from a single Amazon result card"""
        try:
            # Title and URL
            title_elem = card.query_selector('h2 a span')
            link_elem = card.query_selector('h2 a')
            if not title_elem or not link_elem:
                return None

            title = title_elem.inner_text().strip()
            url = "https://www.amazon.com" + link_elem.get_attribute('href').split('?')[0]

            # ASIN (product ID)
            asin_match = re.search(r'/dp/([A-Z0-9]{10})', url)
            if not asin_match:
                return None
            asin = asin_match.group(1)

            # Rating and review count
            rating_elem = card.query_selector('[class*="a-icon-star-small"] span')
            rating = float(rating_elem.inner_text().split()[0]) if rating_elem else 0.0

            review_count_elem = card.query_selector('[class*="a-size-base"]')
            review_count = 0
            if review_count_elem:
                review_text = review_count_elem.inner_text()
                review_match = re.search(r'([\d,]+)', review_text)
                if review_match:
                    review_count = int(review_match.group(1).replace(',', ''))

            # Price
            price_elem = card.query_selector('[class*="a-price"] span.a-offscreen')
            price = price_elem.inner_text().strip() if price_elem else "$0.00"

            # BSR (Best Sellers Rank) - not available in search results, would need product page

            return {
                "id": asin,
                "title": title,
                "url": url,
                "platform": "amazon",
                "price": price,
                "rating": rating,
                "review_count": review_count,
                "bsr": None,  # Would need product page scrape
                "category": None,  # Would need product page scrape
                "scraped_at": datetime.now().isoformat()
            }

        except Exception:
            return None


class GoodreadsScraper:
    """Playwright-based Goodreads scraper for book-specific research"""

    def __init__(self, trail: BreadcrumbTrail):
        self.trail = trail

    def search_books(
        self,
        query: str,
        max_results: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Scrape Goodreads search results for comparable books

        Args:
            query: Search query (e.g., "productivity entrepreneurs")
            max_results: Max books to return

        Returns:
            List of book dictionaries with metadata

        Raises:
            ValueError: If scraping fails or returns no results
        """
        self.trail.light(Config.LED_GOODREADS_START, {
            "action": "goodreads_scrape_started",
            "query": query,
            "max_results": max_results
        })

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0")

            try:
                # Navigate to Goodreads search
                search_url = f"https://www.goodreads.com/search?q={query.replace(' ', '+')}"
                page.goto(search_url, timeout=30000)

                # Wait for results
                page.wait_for_selector('.bookTitle', timeout=10000)

                # Extract book data
                books = []
                book_rows = page.query_selector_all('tr[itemtype="http://schema.org/Book"]')

                for row in book_rows[:max_results]:
                    try:
                        book = self._extract_book_from_row(row)
                        if book:
                            books.append(book)
                    except Exception:
                        continue

                browser.close()

                if not books:
                    raise ValueError(
                        f"Goodreads scraping returned no books for query: '{query}'\n"
                        f"URL: {search_url}\n"
                        f"Possible anti-bot detection"
                    )

                self.trail.light(Config.LED_GOODREADS_START + 1, {
                    "action": "goodreads_scrape_complete",
                    "books_found": len(books)
                })

                return books

            except PlaywrightTimeout as e:
                browser.close()
                self.trail.fail(Config.LED_ERROR_START + 4, e)
                raise ValueError(
                    f"Goodreads scraping timed out for query: '{query}'\n"
                    f"URL: {search_url}\n"
                    f"Error: {str(e)}"
                )
            except Exception as e:
                browser.close()
                self.trail.fail(Config.LED_ERROR_START + 4, e)
                raise ValueError(f"Goodreads scraping failed: {str(e)}")

    def _extract_book_from_row(self, row) -> Optional[Dict[str, Any]]:
        """Extract book data from a single Goodreads result row"""
        try:
            # Title and URL
            title_elem = row.query_selector('.bookTitle')
            if not title_elem:
                return None

            title = title_elem.inner_text().strip()
            url = "https://www.goodreads.com" + title_elem.get_attribute('href')

            # Book ID
            book_id_match = re.search(r'/show/(\d+)', url)
            if not book_id_match:
                return None
            book_id = book_id_match.group(1)

            # Author
            author_elem = row.query_selector('.authorName')
            author = author_elem.inner_text().strip() if author_elem else "Unknown"

            # Rating
            rating_elem = row.query_selector('.minirating')
            rating = 0.0
            review_count = 0
            if rating_elem:
                rating_text = rating_elem.inner_text().strip()
                rating_match = re.search(r'([\d.]+) avg rating', rating_text)
                review_match = re.search(r'([\d,]+) ratings', rating_text)

                if rating_match:
                    rating = float(rating_match.group(1))
                if review_match:
                    review_count = int(review_match.group(1).replace(',', ''))

            return {
                "id": book_id,
                "title": title,
                "url": url,
                "platform": "goodreads",
                "author": author,
                "rating": rating,
                "review_count": review_count,
                "want_to_read": None,  # Would need book page scrape
                "scraped_at": datetime.now().isoformat()
            }

        except Exception:
            return None
