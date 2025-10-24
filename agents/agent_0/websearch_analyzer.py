"""
Agent 0 Web Search Analyzer
Analyzes web search results to extract trend signals

LED Breadcrumb Range: 610-619 (Web Search Analysis)
- 610: Analyzer initialization
- 611: Article analysis start
- 612: Subtopic extraction
- 613: Engagement signal detection
- 614: Source reliability scoring
- 615: Composite score calculation
- 616: DataFrame conversion
- 617: Validation complete
- 618: Error handling
- 619: Analysis complete
"""

import re
from typing import List, Dict, Optional
from datetime import datetime
import pandas as pd

from lib.breadcrumb_system import BreadcrumbTrail


class WebSearchAnalyzer:
    """
    Analyzes web search results to generate trend signals

    Process:
    1. Parse search results (articles, mentions)
    2. Extract signals (frequency, recency, source quality)
    3. Calculate demand score (0-100)
    4. Convert to PyTrends-compatible format
    """

    # Trusted sources for trend data (weighted by reliability)
    TRUSTED_SOURCES = {
        'forbes.com': 1.0,
        'healthline.com': 1.0,
        'statista.com': 1.0,
        'reddit.com': 0.9,
        'medium.com': 0.8,
        'nytimes.com': 1.0,
        'wsj.com': 1.0,
        'bloomberg.com': 1.0,
        'techcrunch.com': 0.9,
        'wired.com': 0.9,
    }

    # Engagement indicators (words that suggest high demand)
    ENGAGEMENT_INDICATORS = [
        'trending', 'viral', 'popular', 'top', 'best',
        'in-demand', 'hot', 'rising', 'surge', 'boom',
        'growing', 'increase', 'demand', 'sales', 'revenue'
    ]

    # Recency weights (more recent = higher weight)
    RECENCY_WEIGHTS = {
        2025: 1.0,
        2024: 0.8,
        2023: 0.5,
        2022: 0.3,
    }

    def __init__(self, trail: BreadcrumbTrail):
        """
        Initialize web search analyzer

        Args:
            trail: LED breadcrumb trail for debugging
        """
        self.trail = trail

        self.trail.light(610, {
            "action": "analyzer_init"
        })

    def analyze_keyword(self, keyword: str, search_results: List[Dict]) -> Dict:
        """
        Analyze web search results for a keyword to generate trend signals

        Args:
            keyword: The search keyword
            search_results: List of search result dicts with 'title', 'url', 'snippet'

        Returns:
            Dict with demand_score, confidence, signals
        """
        self.trail.light(611, {
            "action": "analyze_start",
            "keyword": keyword,
            "result_count": len(search_results)
        })

        if not search_results:
            return {
                'demand_score': 0.0,
                'confidence': 0.0,
                'signals': {
                    'mention_count': 0,
                    'source_quality': 0.0,
                    'recency_score': 0.0,
                    'engagement_score': 0.0
                }
            }

        # Extract signals
        mention_count = len(search_results)
        source_quality = self._calculate_source_quality(search_results)
        recency_score = self._calculate_recency_score(search_results)
        engagement_score = self._calculate_engagement_score(keyword, search_results)

        self.trail.light(612, {
            "action": "signals_extracted",
            "mention_count": mention_count,
            "source_quality": round(source_quality, 2),
            "recency_score": round(recency_score, 2)
        })

        # Calculate composite demand score
        demand_score = self._calculate_demand_score(
            mention_count=mention_count,
            source_quality=source_quality,
            recency_score=recency_score,
            engagement_score=engagement_score
        )

        # Calculate confidence based on data quality
        confidence = self._calculate_confidence(
            mention_count=mention_count,
            source_quality=source_quality
        )

        self.trail.light(615, {
            "action": "score_calculated",
            "keyword": keyword,
            "demand_score": round(demand_score, 2),
            "confidence": round(confidence, 2)
        })

        self.trail.light(619, {
            "action": "analysis_complete",
            "keyword": keyword
        })

        return {
            'demand_score': demand_score,
            'confidence': confidence,
            'signals': {
                'mention_count': mention_count,
                'source_quality': source_quality,
                'recency_score': recency_score,
                'engagement_score': engagement_score
            }
        }

    def _calculate_source_quality(self, search_results: List[Dict]) -> float:
        """
        Calculate average source quality score (0-1)

        Args:
            search_results: List of search result dicts

        Returns:
            Average source quality (0.0-1.0)
        """
        if not search_results:
            return 0.0

        total_quality = 0.0
        for result in search_results:
            url = result.get('url', '').lower()

            # Check against trusted sources
            quality = 0.5  # Default for unknown sources
            for domain, weight in self.TRUSTED_SOURCES.items():
                if domain in url:
                    quality = weight
                    break

            total_quality += quality

        avg_quality = total_quality / len(search_results)

        self.trail.light(614, {
            "action": "source_quality_scored",
            "avg_quality": round(avg_quality, 2),
            "result_count": len(search_results)
        })

        return avg_quality

    def _calculate_recency_score(self, search_results: List[Dict]) -> float:
        """
        Calculate recency score based on year mentions (0-1)

        Args:
            search_results: List of search result dicts

        Returns:
            Recency score (0.0-1.0)
        """
        current_year = datetime.now().year
        year_mentions = []

        for result in search_results:
            text = f"{result.get('title', '')} {result.get('snippet', '')}".lower()

            # Extract year mentions
            for year in range(2022, current_year + 1):
                if str(year) in text:
                    year_mentions.append(year)

        if not year_mentions:
            # No year mentions, assume moderate recency
            return 0.6

        # Calculate weighted average
        total_weight = 0.0
        total_count = len(year_mentions)

        for year in year_mentions:
            weight = self.RECENCY_WEIGHTS.get(year, 0.1)
            total_weight += weight

        recency_score = total_weight / total_count

        return min(recency_score, 1.0)

    def _calculate_engagement_score(self, keyword: str, search_results: List[Dict]) -> float:
        """
        Calculate engagement score based on indicator words (0-1)

        Args:
            keyword: The search keyword
            search_results: List of search result dicts

        Returns:
            Engagement score (0.0-1.0)
        """
        total_indicators = 0

        for result in search_results:
            text = f"{result.get('title', '')} {result.get('snippet', '')}".lower()

            # Count engagement indicators
            for indicator in self.ENGAGEMENT_INDICATORS:
                if indicator in text:
                    total_indicators += 1

        # Normalize (cap at 20 indicators for score of 1.0)
        engagement_score = min(total_indicators / 20.0, 1.0)

        self.trail.light(613, {
            "action": "engagement_detected",
            "keyword": keyword,
            "indicator_count": total_indicators,
            "score": round(engagement_score, 2)
        })

        return engagement_score

    def _calculate_demand_score(
        self,
        mention_count: int,
        source_quality: float,
        recency_score: float,
        engagement_score: float
    ) -> float:
        """
        Calculate composite demand score (0-100)

        Formula (from Grok's recommendation):
        Demand = (mention_frequency * 0.4) + (source_quality * 0.3) +
                 (recency * 0.2) + (engagement * 0.1)

        Args:
            mention_count: Number of search results
            source_quality: Average source quality (0-1)
            recency_score: Recency score (0-1)
            engagement_score: Engagement indicator score (0-1)

        Returns:
            Demand score (0-100)
        """
        # Normalize mention count (10+ mentions = 1.0)
        mention_score = min(mention_count / 10.0, 1.0)

        # Weighted composite
        demand = (
            mention_score * 0.4 +
            source_quality * 0.3 +
            recency_score * 0.2 +
            engagement_score * 0.1
        )

        # Scale to 0-100
        demand_score = demand * 100.0

        return round(demand_score, 2)

    def _calculate_confidence(self, mention_count: int, source_quality: float) -> float:
        """
        Calculate confidence in the demand score (0-100)

        Higher confidence when:
        - More mentions (more data)
        - Higher source quality (trusted sources)

        Args:
            mention_count: Number of search results
            source_quality: Average source quality (0-1)

        Returns:
            Confidence score (0-100)
        """
        # Mention confidence (10+ mentions = full confidence)
        mention_confidence = min(mention_count / 10.0, 1.0)

        # Combined confidence
        confidence = (mention_confidence * 0.6) + (source_quality * 0.4)

        return round(confidence * 100.0, 2)

    def convert_to_pytrends_format(self, keyword: str, analysis: Dict) -> pd.DataFrame:
        """
        Convert analysis results to PyTrends-compatible DataFrame format

        Args:
            keyword: The keyword
            analysis: Analysis dict from analyze_keyword()

        Returns:
            DataFrame with PyTrends-compatible format
        """
        self.trail.light(616, {
            "action": "convert_to_dataframe",
            "keyword": keyword
        })

        # Create a simple DataFrame (web search doesn't have time series data)
        # We'll use a single row with the demand score
        df = pd.DataFrame({
            keyword: [analysis['demand_score']]
        })

        self.trail.light(617, {
            "action": "conversion_complete",
            "keyword": keyword
        })

        return df
