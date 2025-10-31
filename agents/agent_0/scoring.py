"""
Agent 0 Topic Scoring Algorithm
Combines signals from Google Trends and Reddit into composite demand score
Now includes competition analysis for opportunity scoring
"""

from typing import Dict, List
from datetime import datetime
from lib.breadcrumb_system import BreadcrumbTrail
from .config import Agent0Config as Config
from .competition_analyzer import CompetitionAnalyzer


class TopicScorer:
    """Calculates composite demand scores and opportunity scores for topics"""

    def __init__(self, trail: BreadcrumbTrail):
        self.trail = trail
        self.competition_analyzer = CompetitionAnalyzer(trail)

    def calculate_recency_score(
        self,
        trends_data: Dict,
        reddit_data: Dict
    ) -> Dict:
        """
        Calculate recency/urgency score based on content freshness

        Recency Score Components:
        - Recent activity weight (60%): Posts in last 30-90 days
        - Trend momentum (30%): Rising vs falling from Google Trends
        - Content freshness (10%): Average age of content

        Returns dict with:
        - recency_score: 0-100 overall recency/urgency
        - recent_activity_pct: % of content in last 90 days
        - trend_momentum: Rising/stable/falling
        - avg_content_age_days: Average age of content
        """
        now = datetime.now().timestamp()
        days_30 = 30 * 24 * 60 * 60
        days_90 = 90 * 24 * 60 * 60

        recent_30_count = 0
        recent_90_count = 0
        total_content = 0
        total_age_days = 0

        # Analyze Reddit timestamps
        reddit_timestamps = reddit_data.get('timestamps', [])
        for ts in reddit_timestamps:
            age = now - ts
            total_content += 1
            total_age_days += (age / (24 * 60 * 60))

            if age <= days_30:
                recent_30_count += 1
                recent_90_count += 1
            elif age <= days_90:
                recent_90_count += 1

        # Calculate components
        if total_content == 0:
            return {
                'recency_score': 0,
                'recent_activity_pct': 0,
                'trend_momentum': 'no_data',
                'avg_content_age_days': 0,
                'recent_30_days': 0,
                'recent_90_days': 0,
                'total_content': 0
            }

        # 1. Recent activity (60%): Percentage of content in last 90 days
        recent_90_pct = (recent_90_count / total_content) * 100
        recent_activity_score = min(recent_90_pct, 100) * 0.60

        # 2. Trend momentum (30%): From Google Trends
        trend_direction = trends_data.get('trend_direction', 'stable')
        if trend_direction == 'rising':
            trend_momentum_score = 100 * 0.30
        elif trend_direction == 'falling':
            trend_momentum_score = 30 * 0.30  # Penalty for falling
        else:  # stable or no_data
            trend_momentum_score = 60 * 0.30

        # 3. Content freshness (10%): Inverse of average age
        avg_age_days = total_age_days / total_content
        # Convert to freshness score: 0 days = 100, 365 days = 0
        freshness_score = max(0, (1 - (avg_age_days / 365)) * 100) * 0.10

        # Combined recency score
        recency_score = recent_activity_score + trend_momentum_score + freshness_score

        return {
            'recency_score': round(recency_score, 2),
            'recent_activity_pct': round(recent_90_pct, 1),
            'trend_momentum': trend_direction,
            'avg_content_age_days': round(avg_age_days, 1),
            'recent_30_days': recent_30_count,
            'recent_90_days': recent_90_count,
            'total_content': total_content
        }

    def calculate_data_richness(
        self,
        trends_data: Dict,
        reddit_data: Dict
    ) -> Dict:
        """
        Calculate data richness score based on volume and quality of data sources

        Returns dict with:
        - richness_score: 0-100 overall data quality
        - richness_stars: 1-5 star rating
        - source_breakdown: Details per source
        """
        scores = []
        breakdown = {}

        # Google Trends richness (0-100)
        trends_points = trends_data.get('data_points', 0)
        trends_interest = trends_data.get('average_interest', 0)

        if trends_points > 0:
            # More data points (52 weeks = full year) + higher interest = richer
            trends_richness = min(
                (trends_points / 52) * 50 +  # Data point coverage
                (trends_interest / 100) * 50,  # Interest level
                100
            )
            scores.append(trends_richness)
            breakdown['trends'] = {
                'richness': round(trends_richness, 1),
                'data_points': trends_points,
                'average_interest': trends_interest
            }

        # Reddit richness (0-100)
        reddit_posts = reddit_data.get('total_posts', 0)
        reddit_engagement = reddit_data.get('avg_engagement', 0)

        if reddit_posts > 0:
            # More posts + higher engagement = richer
            reddit_richness = min(
                (reddit_posts / 100) * 30 +  # Post volume (100 posts = good sample)
                (reddit_engagement / 5000) * 70,  # Engagement quality
                100
            )
            scores.append(reddit_richness)
            breakdown['reddit'] = {
                'richness': round(reddit_richness, 1),
                'total_posts': reddit_posts,
                'avg_engagement': reddit_engagement
            }

        # Overall richness = average of available sources
        overall_richness = sum(scores) / len(scores) if scores else 0

        # Convert to star rating (1-5)
        if overall_richness >= 90:
            stars = 5
        elif overall_richness >= 70:
            stars = 4
        elif overall_richness >= 50:
            stars = 3
        elif overall_richness >= 30:
            stars = 2
        else:
            stars = 1

        return {
            'richness_score': round(overall_richness, 2),
            'richness_stars': stars,
            'sources_count': len(scores),
            'breakdown': breakdown
        }

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
        - Number of videos (more content = more interest)
        - View counts (high views = strong demand signals)
        - Channel diversity (spread across creators)
        """
        if not youtube_data:
            return 0.0

        total_videos = youtube_data.get('total_videos', 0)
        avg_views = youtube_data.get('avg_views', 0)
        top_channels = youtube_data.get('top_channels', [])

        if total_videos == 0:
            return 0.0

        # Video volume score (logarithmic scale)
        # 5 videos = 20, 10 videos = 35, 20+ videos = 60
        if total_videos >= 20:
            volume_score = 60
        elif total_videos >= 10:
            volume_score = 35
        elif total_videos >= 5:
            volume_score = 20
        else:
            volume_score = total_videos * 4

        # View count score (logarithmic scale, capped)
        # 10k avg views = 20, 100k = 40, 1M+ = 60
        if avg_views >= 1000000:
            views_score = 60
        elif avg_views >= 100000:
            views_score = 40
        elif avg_views >= 10000:
            views_score = 20
        elif avg_views > 0:
            views_score = min((avg_views / 1000) * 2, 20)
        else:
            views_score = 0

        # Channel diversity bonus (more creators = broader interest)
        diversity_bonus = min(len(top_channels) * 4, 20)

        total = volume_score + views_score + diversity_bonus
        return min(total, 100.0)

    def calculate_composite_score(
        self,
        trends_data: Dict,
        reddit_data: Dict,
        youtube_data: Dict = None
    ) -> Dict:
        """
        Calculate weighted composite demand score with competition analysis

        Supports 3 modes:
        - DRILLDOWN_MODE: Reddit-only (60% confidence, fast exploration)
        - 2-source: Reddit + Google Trends (100% confidence if both have data)
        - 3-source: Reddit + Google Trends + YouTube (100% confidence if all have data)

        Returns dict with:
        - composite_score: 0-100 overall demand score
        - trends_score: normalized Google Trends score
        - reddit_score: normalized Reddit score
        - youtube_score: normalized YouTube score (if enabled)
        - confidence: 0-100 confidence in score accuracy
        - competition: dict with competition metrics
        - opportunity: dict with opportunity score and recommendation
        - insights: list of competitive insights
        """
        self.trail.light(Config.LED_SCORING_START, {
            "action": "calculate_scores"
        })

        # Normalize each source (DEMAND scoring)
        trends_score = self.normalize_trends_score(trends_data) if trends_data else 0
        reddit_score = self.normalize_reddit_score(reddit_data)
        youtube_score = self.normalize_youtube_score(youtube_data) if youtube_data else 0

        # Count sources with data
        sources_with_data = sum([
            1 if trends_data and trends_data.get('data_points', 0) > 0 else 0,
            1 if reddit_data.get('total_posts', 0) > 0 else 0,
            1 if youtube_data and youtube_data.get('total_videos', 0) > 0 else 0
        ])

        # Adjust weights dynamically based on available sources
        if Config.ENABLE_YOUTUBE and youtube_data:
            # 3-source mode: 33/33/33 split
            weight_trends = 0.33
            weight_reddit = 0.33
            weight_youtube = 0.34  # Slight extra to sum to 1.0
            composite = (
                trends_score * weight_trends +
                reddit_score * weight_reddit +
                youtube_score * weight_youtube
            )
        elif Config.DRILLDOWN_MODE or not trends_data:
            # Drill-down mode: Reddit-only
            composite = reddit_score
        else:
            # 2-source mode: 50/50 split (Trends + Reddit)
            composite = (
                trends_score * Config.WEIGHT_GOOGLE_TRENDS +
                reddit_score * Config.WEIGHT_REDDIT
            )

        # Calculate confidence based on mode and data availability
        if Config.DRILLDOWN_MODE:
            # Drill-down mode: 60% confidence (acceptable for exploration)
            confidence = 60 if sources_with_data > 0 else 0
        elif Config.ENABLE_YOUTUBE:
            # 3-source mode: Confidence based on source count
            confidence = {3: 100, 2: 75, 1: 50, 0: 0}[sources_with_data]
        else:
            # 2-source mode: Confidence based on source count
            confidence = {2: 100, 1: 60, 0: 0}[sources_with_data]

        # Analyze COMPETITION
        competition = self.competition_analyzer.calculate_overall_competition(
            trends_data,
            reddit_data
        )

        # Calculate OPPORTUNITY score (demand vs competition)
        opportunity = self.competition_analyzer.calculate_opportunity_score(
            composite,  # demand_score
            competition['overall_competition']  # competition_score
        )

        # Get competitive insights
        insights = self.competition_analyzer.get_competitive_insights(
            trends_data,
            reddit_data,
            opportunity
        )

        # Calculate audience size (for bubble sizing in visualization)
        audience_size = self.competition_analyzer.calculate_audience_size(
            trends_data,
            reddit_data
        )

        # Calculate data richness (for confidence and visualization)
        richness = self.calculate_data_richness(
            trends_data,
            reddit_data
        )

        # Calculate recency/urgency (NEW)
        recency = self.calculate_recency_score(
            trends_data,
            reddit_data
        )

        # Classify zone based on demand and competition
        zone = self._classify_zone(composite, competition['overall_competition'])

        result = {
            # Demand metrics (original)
            "composite_score": round(composite, 2),
            "trends_score": round(trends_score, 2),
            "reddit_score": round(reddit_score, 2),
            "youtube_score": round(youtube_score, 2) if youtube_data else None,
            "confidence": confidence,
            "sources_with_data": sources_with_data,

            # Competition metrics (NEW)
            "competition": competition,

            # Opportunity metrics (NEW)
            "opportunity": opportunity,

            # Insights (NEW)
            "insights": insights,

            # Visualization metrics (NEW)
            "audience_size": audience_size,
            "zone": zone,

            # Data richness metrics (NEW)
            "richness": richness,

            # Recency metrics (NEW)
            "recency": recency
        }

        self.trail.light(Config.LED_SCORING_START + 1, {
            "action": "scoring_complete",
            "demand": round(composite, 2),
            "competition": round(competition['overall_competition'], 2),
            "opportunity": round(opportunity['opportunity_score'], 2)
        })

        return result

    def _classify_zone(self, demand_score: float, competition_score: float) -> str:
        """
        Classify topic into quadrant zone based on demand and competition

        Zones:
        - gold_mine: High demand (>50), Low competition (<50)
        - viable: High demand (>50), High competition (>50)
        - risky_niche: Low demand (<50), Low competition (<50)
        - avoid: Low demand (<50), High competition (>50)

        Returns: Zone identifier string
        """
        high_demand = demand_score >= 50
        low_competition = competition_score < 50

        if high_demand and low_competition:
            return 'gold_mine'
        elif high_demand and not low_competition:
            return 'viable'
        elif not high_demand and low_competition:
            return 'risky_niche'
        else:
            return 'avoid'

    def rank_topics(self, topic_data: List[Dict]) -> List[Dict]:
        """
        Rank topics by opportunity score (demand vs competition)

        Input: List of dicts with 'topic' and 'scores' keys
        Output: Sorted list (highest opportunity first)
        """
        self.trail.light(Config.LED_SCORING_START + 7, {
            "action": "rank_topics",
            "total_topics": len(topic_data)
        })

        # Sort by opportunity score (primary), then confidence (secondary)
        ranked = sorted(
            topic_data,
            key=lambda x: (
                x['scores']['opportunity']['opportunity_score'],
                x['scores']['confidence']
            ),
            reverse=True
        )

        self.trail.light(Config.LED_SCORING_START + 8, {
            "action": "ranking_complete",
            "top_topic": ranked[0]['topic'] if ranked else None,
            "top_opportunity": ranked[0]['scores']['opportunity']['opportunity_score'] if ranked else 0,
            "top_demand": ranked[0]['scores']['composite_score'] if ranked else 0,
            "top_competition": ranked[0]['scores']['competition']['overall_competition'] if ranked else 0
        })

        return ranked
