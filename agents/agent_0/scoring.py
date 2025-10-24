"""
Agent 0 Topic Scoring Algorithm
Combines signals from Google Trends, Reddit, and YouTube into composite demand score
"""

from typing import Dict, List
from lib.breadcrumb_system import BreadcrumbTrail
from .config import Agent0Config as Config


class TopicScorer:
    """Calculates composite demand scores for topics"""

    def __init__(self, trail: BreadcrumbTrail):
        self.trail = trail

    def normalize_trends_score(self, trends_data: Dict) -> float:
        """
        Normalize Google Trends data to 0-100 score

        Considers:
        - Average interest level
        - Trend direction (rising is better)
        - Data quality (more data points = more confidence)
        """
        avg_interest = trends_data.get('average_interest', 0)
        trend_direction = trends_data.get('trend_direction', 'stable')
        data_points = trends_data.get('data_points', 0)

        # Base score from average interest
        score = avg_interest

        # Bonus for rising trends (+20%)
        if trend_direction == 'rising':
            score *= 1.2
        # Penalty for falling trends (-20%)
        elif trend_direction == 'falling':
            score *= 0.8

        # Quality adjustment based on data points
        if data_points < 10:
            score *= 0.7  # Low confidence
        elif data_points >= 30:
            score *= 1.1  # High confidence

        # Cap at 100
        return min(score, 100.0)

    def normalize_reddit_score(self, reddit_data: Dict) -> float:
        """
        Normalize Reddit data to 0-100 score

        Considers:
        - Number of posts (more discussion = more interest)
        - Engagement level (high scores = passionate community)
        - Subreddit diversity (spread across communities)
        """
        total_posts = reddit_data.get('total_posts', 0)
        avg_engagement = reddit_data.get('avg_engagement', 0)
        top_subreddits = reddit_data.get('top_subreddits', [])

        if total_posts == 0:
            return 0.0

        # Post volume score (logarithmic scale)
        # 10 posts = 30, 50 posts = 50, 100+ posts = 70
        if total_posts >= 100:
            volume_score = 70
        elif total_posts >= 50:
            volume_score = 50
        elif total_posts >= 10:
            volume_score = 30
        else:
            volume_score = total_posts * 3

        # Engagement score (linear scale, capped)
        # Average score >100 = very high engagement
        engagement_score = min(avg_engagement / 2, 50)

        # Diversity bonus (more subreddits = broader appeal)
        diversity_bonus = min(len(top_subreddits) * 3, 15)

        total = volume_score + engagement_score + diversity_bonus
        return min(total, 100.0)

    def normalize_youtube_score(self, youtube_data: Dict) -> float:
        """
        Normalize YouTube data to 0-100 score

        Considers:
        - Number of videos (content volume)
        - Total/average views (audience size)
        - Channel diversity (not dominated by single creator)
        """
        total_videos = youtube_data.get('total_videos', 0)
        avg_views = youtube_data.get('avg_views', 0)
        top_channels = youtube_data.get('top_channels', [])

        if total_videos == 0:
            return 0.0

        # Video volume score
        if total_videos >= 20:
            volume_score = 40
        elif total_videos >= 10:
            volume_score = 30
        else:
            volume_score = total_videos * 2

        # View count score (logarithmic scale)
        # 10K avg = 30, 100K avg = 50, 1M+ avg = 70
        if avg_views >= 1000000:
            view_score = 70
        elif avg_views >= 100000:
            view_score = 50
        elif avg_views >= 10000:
            view_score = 30
        else:
            view_score = min(avg_views / 500, 20)

        # Channel diversity bonus
        diversity_bonus = min(len(top_channels) * 2, 10)

        total = volume_score + view_score + diversity_bonus
        return min(total, 100.0)

    def calculate_composite_score(
        self,
        trends_data: Dict,
        reddit_data: Dict,
        youtube_data: Dict
    ) -> Dict:
        """
        Calculate weighted composite demand score

        Returns dict with:
        - composite_score: 0-100 overall demand score
        - trends_score: normalized Google Trends score
        - reddit_score: normalized Reddit score
        - youtube_score: normalized YouTube score
        - confidence: 0-100 confidence in score accuracy
        """
        self.trail.light(Config.LED_SCORING_START, {
            "action": "calculate_scores"
        })

        # Normalize each source
        trends_score = self.normalize_trends_score(trends_data)
        reddit_score = self.normalize_reddit_score(reddit_data)
        youtube_score = self.normalize_youtube_score(youtube_data)

        # Weighted composite
        composite = (
            trends_score * Config.WEIGHT_GOOGLE_TRENDS +
            reddit_score * Config.WEIGHT_REDDIT +
            youtube_score * Config.WEIGHT_YOUTUBE
        )

        # Calculate confidence based on data availability
        sources_with_data = sum([
            1 if trends_data.get('data_points', 0) > 0 else 0,
            1 if reddit_data.get('total_posts', 0) > 0 else 0,
            1 if youtube_data.get('total_videos', 0) > 0 else 0
        ])

        # Confidence: 3 sources = 100%, 2 sources = 70%, 1 source = 40%
        confidence = {3: 100, 2: 70, 1: 40, 0: 0}[sources_with_data]

        result = {
            "composite_score": round(composite, 2),
            "trends_score": round(trends_score, 2),
            "reddit_score": round(reddit_score, 2),
            "youtube_score": round(youtube_score, 2),
            "confidence": confidence,
            "sources_with_data": sources_with_data
        }

        self.trail.light(Config.LED_SCORING_START + 1, {
            "action": "scoring_complete",
            **result
        })

        return result

    def rank_topics(self, topic_data: List[Dict]) -> List[Dict]:
        """
        Rank topics by composite score

        Input: List of dicts with 'topic' and 'scores' keys
        Output: Sorted list (highest score first)
        """
        self.trail.light(Config.LED_SCORING_START + 2, {
            "action": "rank_topics",
            "total_topics": len(topic_data)
        })

        # Sort by composite score, then by confidence
        ranked = sorted(
            topic_data,
            key=lambda x: (
                x['scores']['composite_score'],
                x['scores']['confidence']
            ),
            reverse=True
        )

        self.trail.light(Config.LED_SCORING_START + 3, {
            "action": "ranking_complete",
            "top_topic": ranked[0]['topic'] if ranked else None,
            "top_score": ranked[0]['scores']['composite_score'] if ranked else 0
        })

        return ranked
