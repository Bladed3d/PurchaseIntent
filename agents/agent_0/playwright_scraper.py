"""
Agent 0 Playwright Scraper
Core browser automation for scraping Google Trends data

LED Breadcrumb Range: 570-579 (Playwright operations)
- 570: Scraper initialization
- 571: Browser launch
- 572: Page navigation
- 573: Cookie consent handling
- 574: Widget detection
- 575: Download operations
- 576: CSV save operations
- 577: Rate limit detection
- 578: Error handling
- 579: Cleanup operations
"""

import asyncio
import os
import time
import random
from typing import List, Dict, Optional
from pathlib import Path
from playwright.async_api import async_playwright, Browser, BrowserContext, Page, Download

from lib.breadcrumb_system import BreadcrumbTrail
from .config import Agent0Config as Config


class PlaywrightScraper:
    """
    Google Trends scraper using Playwright browser automation

    Features:
    - Stealth mode (anti-detection)
    - User agent rotation
    - Random delays (mimic human behavior)
    - Exponential backoff on rate limits
    - LED breadcrumb instrumentation
    - CSV download handling
    """

    # User agents (Chrome 134-135, 2025)
    USER_AGENTS = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36',
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36',
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36',
    ]

    # Viewport sizes (common resolutions)
    VIEWPORTS = [
        {'width': 1920, 'height': 1080},
        {'width': 1366, 'height': 768},
        {'width': 1536, 'height': 864},
        {'width': 1440, 'height': 900},
        {'width': 1280, 'height': 720},
    ]

    # Rate limiting
    MIN_DELAY_BETWEEN_REQUESTS = 15.0  # Seconds (4 requests/minute target)
    MAX_RETRIES = 3
    BASE_BACKOFF = 5.0  # Seconds

    def __init__(self, trail: BreadcrumbTrail, cache_dir: str = "cache/playwright"):
        """
        Initialize Playwright scraper

        Args:
            trail: LED breadcrumb trail for debugging
            cache_dir: Directory for downloaded CSV files
        """
        self.trail = trail
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)

        self.last_request_time = 0

        self.trail.light(570, {
            "action": "playwright_scraper_init",
            "cache_dir": str(self.cache_dir)
        })

    def _get_random_user_agent(self) -> str:
        """Get random user agent from list"""
        return random.choice(self.USER_AGENTS)

    def _get_random_viewport(self) -> Dict[str, int]:
        """Get random viewport size"""
        return random.choice(self.VIEWPORTS)

    def _wait_for_rate_limit(self):
        """Enforce minimum delay between requests"""
        elapsed = time.time() - self.last_request_time
        if elapsed < self.MIN_DELAY_BETWEEN_REQUESTS:
            wait_time = self.MIN_DELAY_BETWEEN_REQUESTS - elapsed
            self.trail.light(577, {
                "action": "rate_limit_wait",
                "wait_seconds": round(wait_time, 2)
            })
            time.sleep(wait_time)

        self.last_request_time = time.time()

    async def scrape_keyword(
        self,
        keyword: str,
        geo: str = "US",
        timeframe: str = "today 12-m",
        retry_count: int = 0
    ) -> Optional[List[str]]:
        """
        Scrape Google Trends data for a single keyword

        Args:
            keyword: Search term (e.g., "romance novels")
            geo: Geographic region (e.g., "US")
            timeframe: Time range (e.g., "today 12-m")
            retry_count: Current retry attempt (for exponential backoff)

        Returns:
            List of downloaded CSV file paths, or None on failure
        """
        self.trail.light(570, {
            "action": "scrape_keyword_start",
            "keyword": keyword,
            "geo": geo,
            "timeframe": timeframe,
            "retry_count": retry_count
        })

        # Enforce rate limiting
        self._wait_for_rate_limit()

        try:
            async with async_playwright() as p:
                # Launch browser
                self.trail.light(571, {
                    "action": "browser_launch",
                    "headless": True
                })

                browser = await p.chromium.launch(
                    headless=True,
                    args=[
                        '--disable-blink-features=AutomationControlled',
                        '--disable-dev-shm-usage',
                        '--no-sandbox'
                    ]
                )

                # Create context with anti-detection
                user_agent = self._get_random_user_agent()
                viewport = self._get_random_viewport()

                self.trail.light(571, {
                    "action": "browser_context_create",
                    "user_agent": user_agent[:50] + "...",
                    "viewport": viewport
                })

                context = await browser.new_context(
                    viewport=viewport,
                    user_agent=user_agent,
                    accept_downloads=True,
                    locale='en-US',
                    timezone_id='America/New_York'
                )

                page = await context.new_page()

                try:
                    # Build URL
                    base_url = "https://trends.google.com/trends/explore"
                    params = f"?date={timeframe}&geo={geo}&q={keyword.replace(' ', '%20')}"
                    url = base_url + params

                    self.trail.light(572, {
                        "action": "navigate_to_url",
                        "url": url
                    })

                    # Navigate to page
                    response = await page.goto(url, wait_until='domcontentloaded', timeout=30000)

                    # Check for rate limit (429)
                    if response and response.status == 429:
                        self.trail.light(577, {
                            "action": "rate_limit_429_detected",
                            "retry_count": retry_count,
                            "status": 429
                        })

                        if retry_count < self.MAX_RETRIES:
                            # Exponential backoff
                            backoff = self.BASE_BACKOFF * (2 ** retry_count) + random.uniform(0, 1)
                            self.trail.light(577, {
                                "action": "rate_limit_backoff",
                                "backoff_seconds": round(backoff, 2),
                                "retry": retry_count + 1
                            })

                            await asyncio.sleep(backoff)
                            await context.close()
                            await browser.close()

                            # Retry with exponential backoff
                            return await self.scrape_keyword(keyword, geo, timeframe, retry_count + 1)
                        else:
                            self.trail.fail(577, Exception(f"Max retries ({self.MAX_RETRIES}) exceeded for rate limit"))
                            return None

                    # Handle cookie consent
                    self.trail.light(573, {
                        "action": "check_cookie_consent"
                    })

                    try:
                        cookie_button = page.locator("button[mode='primary']").first
                        if await cookie_button.is_visible(timeout=3000):
                            await cookie_button.click()
                            await asyncio.sleep(random.uniform(0.5, 1.0))

                            self.trail.light(573, {
                                "action": "cookie_consent_accepted"
                            })
                    except Exception as e:
                        self.trail.light(573, {
                            "action": "cookie_consent_not_found",
                            "note": "May have been previously accepted"
                        })

                    # Wait for page content to load
                    self.trail.light(572, {
                        "action": "wait_for_networkidle"
                    })

                    await page.wait_for_load_state("networkidle", timeout=60000)

                    # Add random delay (mimic human)
                    human_delay = random.uniform(1.0, 2.0)
                    await asyncio.sleep(human_delay)

                    # Wait for export buttons
                    self.trail.light(574, {
                        "action": "wait_for_export_buttons"
                    })

                    await page.wait_for_selector(".widget-actions-item.export", state="visible", timeout=20000)

                    # Get all export buttons
                    export_buttons = await page.locator(".widget-actions-item.export").all()

                    self.trail.light(574, {
                        "action": "export_buttons_found",
                        "count": len(export_buttons)
                    })

                    # Prepare download directory
                    keyword_dir = self.cache_dir / keyword.replace(' ', '_').replace('/', '_')
                    keyword_dir.mkdir(parents=True, exist_ok=True)

                    downloaded_files = []

                    # Download each CSV
                    for i, button in enumerate(export_buttons):
                        try:
                            self.trail.light(575, {
                                "action": "download_csv_start",
                                "widget_index": i,
                                "total_widgets": len(export_buttons)
                            })

                            # Random delay before click
                            await asyncio.sleep(random.uniform(0.5, 1.5))

                            # Setup download expectation BEFORE clicking
                            async with page.expect_download(timeout=15000) as download_info:
                                await button.click()

                            download = await download_info.value

                            # Save with descriptive name
                            file_name = f"{keyword.replace(' ', '_')}_widget_{i}_{download.suggested_filename}"
                            file_path = keyword_dir / file_name

                            await download.save_as(str(file_path))
                            downloaded_files.append(str(file_path))

                            self.trail.light(576, {
                                "action": "csv_saved",
                                "widget_index": i,
                                "file_name": file_name,
                                "file_path": str(file_path)
                            })

                        except Exception as e:
                            self.trail.light(578, {
                                "action": "download_error",
                                "widget_index": i,
                                "error": str(e)[:200]
                            })

                    self.trail.light(575, {
                        "action": "scrape_keyword_complete",
                        "keyword": keyword,
                        "files_downloaded": len(downloaded_files)
                    })

                    return downloaded_files

                except Exception as e:
                    self.trail.fail(578, e)
                    raise

                finally:
                    # Cleanup
                    self.trail.light(579, {
                        "action": "cleanup_browser_context"
                    })

                    await context.close()
                    await browser.close()

        except Exception as e:
            self.trail.fail(578, e)
            return None

    async def scrape_batch(
        self,
        keywords: List[str],
        geo: str = "US",
        timeframe: str = "today 12-m"
    ) -> Dict[str, List[str]]:
        """
        Scrape multiple keywords sequentially with rate limiting

        Args:
            keywords: List of search terms
            geo: Geographic region
            timeframe: Time range

        Returns:
            Dict mapping keyword to list of downloaded CSV file paths
        """
        self.trail.light(570, {
            "action": "scrape_batch_start",
            "total_keywords": len(keywords),
            "geo": geo,
            "timeframe": timeframe
        })

        results = {}

        for i, keyword in enumerate(keywords, 1):
            self.trail.light(570, {
                "action": "scrape_batch_progress",
                "keyword": keyword,
                "progress": f"{i}/{len(keywords)}"
            })

            files = await self.scrape_keyword(keyword, geo, timeframe)
            results[keyword] = files if files else []

        self.trail.light(570, {
            "action": "scrape_batch_complete",
            "total_keywords": len(keywords),
            "successful": sum(1 for files in results.values() if files),
            "failed": sum(1 for files in results.values() if not files)
        })

        return results
