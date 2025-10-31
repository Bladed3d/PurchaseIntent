"""
Agent 1 Subreddit Overlap Analyzer
Discovers hidden audience segments using subreddit overlap analysis

CRITICAL RULES:
- FAIL LOUDLY: Require minimum overlaps
- Uses PRAW (free Reddit API)
"""

from typing import List, Dict, Any, Optional
from collections import Counter

from lib.breadcrumb_system import BreadcrumbTrail
from agents.agent_1.config import Agent1Config as Config
from agents.agent_1.api_clients import RedditClient


class SubredditOverlapAnalyzer:
    """Analyzes subreddit overlaps to discover hidden audience segments"""

    def __init__(self, trail: BreadcrumbTrail):
        self.trail = trail
        self.reddit_client = RedditClient(trail)

    def analyze_overlaps(
        self,
        base_subreddits: List[str],
        comparables: List[Dict[str, Any]],
        discussions: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Discover hidden segments via subreddit overlap analysis

        Args:
            base_subreddits: Starting subreddits (e.g., ['productivity', 'entrepreneur'])
            comparables: Comparable products from search
            discussions: Reddit discussions from search

        Returns:
            List of overlapping subreddits with multipliers and interpretations

        Raises:
            ValueError: If insufficient overlaps found
        """
        self.trail.light(Config.LED_OVERLAP_START, {
            "action": "overlap_analysis_started",
            "base_subreddits": base_subreddits,
            "discussions_count": len([d for d in discussions if d['platform'] == 'reddit'])
        })

        # Extract subreddits from discussions
        discussion_subreddits = self._extract_discussion_subreddits(discussions)

        # Combine with base subreddits
        all_base_subreddits = list(set(base_subreddits + discussion_subreddits))

        if not all_base_subreddits:
            raise ValueError(
                "No subreddits to analyze for overlap\n"
                "Need at least 1 base subreddit or Reddit discussions"
            )

        # Perform overlap analysis for first base subreddit (most relevant)
        primary_subreddit = all_base_subreddits[0]

        try:
            overlaps = self.reddit_client.get_subreddit_overlap(
                base_subreddit=primary_subreddit,
                max_users=Config.MAX_USERS_OVERLAP
            )

            if not overlaps:
                raise ValueError(
                    f"No overlaps found for r/{primary_subreddit}\n"
                    f"Try a different base subreddit"
                )

            # Enrich overlaps with segment insights
            enriched_overlaps = self._enrich_overlaps(overlaps, comparables)

            self.trail.light(Config.LED_OVERLAP_START + 1, {
                "action": "overlap_analysis_complete",
                "overlaps_found": len(enriched_overlaps),
                "primary_subreddit": primary_subreddit
            })

            return enriched_overlaps

        except Exception as e:
            self.trail.fail(Config.LED_ERROR_START + 6, e)
            raise ValueError(f"Overlap analysis failed: {str(e)}")

    def _extract_discussion_subreddits(
        self,
        discussions: List[Dict[str, Any]]
    ) -> List[str]:
        """Extract unique subreddits from Reddit discussions"""
        subreddits = []

        for discussion in discussions:
            if discussion['platform'] == 'reddit' and 'subreddit' in discussion:
                subreddit = discussion['subreddit'].replace('r/', '').lower()
                if subreddit not in subreddits:
                    subreddits.append(subreddit)

        return subreddits

    def _enrich_overlaps(
        self,
        overlaps: List[Dict[str, Any]],
        comparables: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Enrich overlap data with segment insights and product relevance

        Args:
            overlaps: Raw overlap data from Reddit API
            comparables: Comparable products to contextualize segments

        Returns:
            Enriched overlap data with segment insights
        """
        enriched = []

        for overlap in overlaps:
            # Determine segment type
            segment_type = self._classify_segment(overlap['subreddit'], overlap['multiplier'])

            # Check if segment is mentioned in comparable product titles
            mentioned_in_products = self._check_product_mentions(
                overlap['subreddit'],
                comparables
            )

            enriched.append({
                **overlap,
                "segment_type": segment_type,
                "product_validation": mentioned_in_products,
                "opportunity_level": self._rate_opportunity(
                    overlap['multiplier'],
                    mentioned_in_products
                )
            })

        return enriched

    def _classify_segment(self, subreddit: str, multiplier: float) -> str:
        """
        Classify segment as Primary, Hidden, or Niche based on multiplier

        High multiplier = strong overlap = primary or hidden segment
        """
        if multiplier >= 10.0:
            return "Primary"  # Core audience segment
        elif multiplier >= 5.0:
            return "Hidden"  # Underserved niche opportunity
        else:
            return "Niche"  # Minor segment

    def _check_product_mentions(
        self,
        subreddit: str,
        comparables: List[Dict[str, Any]]
    ) -> bool:
        """
        Check if segment keywords appear in comparable product titles

        Returns:
            True if segment is already validated by product market
        """
        # Extract key terms from subreddit name
        subreddit_clean = subreddit.replace('r/', '').lower()
        segment_keywords = subreddit_clean.split('_')

        # Check if keywords appear in product titles
        for product in comparables:
            title_lower = product['title'].lower()
            for keyword in segment_keywords:
                if len(keyword) > 3 and keyword in title_lower:
                    return True

        return False

    def _rate_opportunity(
        self,
        multiplier: float,
        mentioned_in_products: bool
    ) -> str:
        """
        Rate opportunity level for targeting this segment

        HIGH: Strong overlap + NOT mentioned in products = underserved
        MEDIUM: Strong overlap + mentioned = competitive
        LOW: Weak overlap
        """
        if multiplier >= 8.0:
            if not mentioned_in_products:
                return "HIGH"  # Hidden underserved niche
            else:
                return "MEDIUM"  # Validated but competitive
        elif multiplier >= 5.0:
            return "MEDIUM"
        else:
            return "LOW"


class SegmentInsightsGenerator:
    """Generates actionable insights from subreddit overlap analysis"""

    @staticmethod
    def generate_insights(
        overlaps: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Generate actionable segment insights

        Returns:
            Dictionary with segment summary and recommendations
        """
        # Count segments by type
        segment_types = Counter([o['segment_type'] for o in overlaps])

        # Identify high-opportunity segments
        high_opportunities = [
            o for o in overlaps
            if o['opportunity_level'] == 'HIGH'
        ]

        # Calculate average multiplier
        avg_multiplier = sum([o['multiplier'] for o in overlaps]) / len(overlaps)

        return {
            "total_segments": len(overlaps),
            "segment_breakdown": {
                "primary": segment_types.get('Primary', 0),
                "hidden": segment_types.get('Hidden', 0),
                "niche": segment_types.get('Niche', 0)
            },
            "high_opportunity_segments": len(high_opportunities),
            "average_overlap_multiplier": round(avg_multiplier, 2),
            "top_opportunities": [
                {
                    "subreddit": o['subreddit'],
                    "multiplier": o['multiplier'],
                    "interpretation": o['interpretation'],
                    "opportunity_level": o['opportunity_level']
                }
                for o in high_opportunities[:3]
            ],
            "recommendations": SegmentInsightsGenerator._generate_recommendations(
                high_opportunities,
                overlaps
            )
        }

    @staticmethod
    def _generate_recommendations(
        high_opportunities: List[Dict[str, Any]],
        all_overlaps: List[Dict[str, Any]]
    ) -> List[str]:
        """Generate strategic recommendations based on segments"""
        recommendations = []

        if len(high_opportunities) >= 2:
            recommendations.append(
                f"Found {len(high_opportunities)} underserved niche segments - "
                "consider multi-segment targeting strategy"
            )

        if any(o['multiplier'] >= 12.0 for o in all_overlaps):
            recommendations.append(
                "Strong primary segment identified - prioritize in marketing and positioning"
            )

        validated_segments = [o for o in all_overlaps if o['product_validation']]
        if validated_segments:
            recommendations.append(
                f"{len(validated_segments)} segments already validated by competitor products - "
                "study competitor positioning"
            )

        unvalidated_segments = [o for o in all_overlaps if not o['product_validation']]
        if unvalidated_segments:
            recommendations.append(
                f"{len(unvalidated_segments)} segments NOT mentioned in competitor products - "
                "potential blue ocean opportunity"
            )

        return recommendations if recommendations else ["Conduct deeper segment analysis"]
