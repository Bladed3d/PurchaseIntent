"""
Source Tier Definitions for Intelligent Pipeline Routing

Tier 1: Unlimited sources (use always, parallel processing)
Tier 2: Rate-limited sources (use strategically when needed)

LED Range: N/A (configuration only)
"""

from typing import Dict, Any, List
from dataclasses import dataclass


@dataclass
class DataSource:
    """Definition of a data source"""
    name: str
    tier: int  # 1 = unlimited, 2 = rate-limited
    cost_per_request: float  # $0.00 for free sources
    daily_quota: int  # Max requests per day (999999 = unlimited)
    rate_limit: str  # Human-readable rate limit description
    priority: int  # Higher = use first when choosing between sources
    enabled: bool = True  # Can be disabled if unavailable


class SourceTiers:
    """Data source tier definitions for intelligent routing"""

    # Tier 1: Unlimited sources (always use these)
    TIER_1_SOURCES = {
        "reddit": DataSource(
            name="reddit",
            tier=1,
            cost_per_request=0.0,
            daily_quota=3600,  # PRAW API: effectively unlimited
            rate_limit="3600 requests/hour",
            priority=100,
            enabled=True
        ),
        "ai_web_search": DataSource(
            name="ai_web_search",
            tier=1,
            cost_per_request=0.0,
            daily_quota=999999,  # Task tool: unlimited
            rate_limit="Unlimited (Task tool)",
            priority=95,
            enabled=True
        ),
        "goodreads": DataSource(
            name="goodreads",
            tier=1,
            cost_per_request=0.0,
            daily_quota=999999,  # Playwright web scraping: no quota
            rate_limit="Unlimited (web scraping)",
            priority=90,
            enabled=True
        ),
        "ebay": DataSource(
            name="ebay",
            tier=1,
            cost_per_request=0.0,
            daily_quota=999999,  # Web scraping: no quota
            rate_limit="Unlimited (web scraping)",
            priority=85,
            enabled=False  # Not yet implemented
        )
    }

    # Tier 2: Rate-limited sources (use strategically)
    TIER_2_SOURCES = {
        "amazon": DataSource(
            name="amazon",
            tier=2,
            cost_per_request=0.01,  # Amazon PA API: $0.01-0.50 per request
            daily_quota=8640,  # 1 request/sec = 86,400/day, but budget limited
            rate_limit="1 request/second (tight budget)",
            priority=100,
            enabled=True
        ),
        "youtube": DataSource(
            name="youtube",
            tier=2,
            cost_per_request=0.0,  # Free but quota-limited
            daily_quota=10000,  # YouTube Data API: 10K units/day
            rate_limit="10K quota units/day (~10 topics)",
            priority=90,
            enabled=True
        )
    }

    @classmethod
    def get_tier_1_sources(cls) -> List[DataSource]:
        """Get all enabled Tier 1 (unlimited) sources"""
        return [source for source in cls.TIER_1_SOURCES.values() if source.enabled]

    @classmethod
    def get_tier_2_sources(cls) -> List[DataSource]:
        """Get all enabled Tier 2 (rate-limited) sources"""
        return [source for source in cls.TIER_2_SOURCES.values() if source.enabled]

    @classmethod
    def get_all_sources(cls) -> List[DataSource]:
        """Get all enabled sources across all tiers"""
        return cls.get_tier_1_sources() + cls.get_tier_2_sources()

    @classmethod
    def get_source_by_name(cls, name: str) -> DataSource:
        """
        Get source definition by name

        Args:
            name: Source name (e.g., "reddit", "amazon")

        Returns:
            DataSource object

        Raises:
            KeyError: If source not found
        """
        all_sources = {**cls.TIER_1_SOURCES, **cls.TIER_2_SOURCES}
        if name not in all_sources:
            raise KeyError(f"Unknown source: {name}. Available: {list(all_sources.keys())}")
        return all_sources[name]

    @classmethod
    def is_tier_1(cls, source_name: str) -> bool:
        """Check if source is Tier 1 (unlimited)"""
        return source_name in cls.TIER_1_SOURCES

    @classmethod
    def is_tier_2(cls, source_name: str) -> bool:
        """Check if source is Tier 2 (rate-limited)"""
        return source_name in cls.TIER_2_SOURCES

    @classmethod
    def get_total_daily_cost(cls, sources_used: List[str], requests_per_source: int = 1) -> float:
        """
        Calculate total daily cost for using specific sources

        Args:
            sources_used: List of source names to use
            requests_per_source: Number of requests per source

        Returns:
            Total cost in USD
        """
        total_cost = 0.0
        for source_name in sources_used:
            try:
                source = cls.get_source_by_name(source_name)
                total_cost += source.cost_per_request * requests_per_source
            except KeyError:
                continue
        return total_cost
