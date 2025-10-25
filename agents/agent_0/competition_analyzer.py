"""
Agent 0 Competition Analysis
Analyzes market saturation and competitive landscape for topics

Goal: Find high-demand, low-competition opportunities (the "sweet spot")
"""

from typing import Dict, List
from lib.breadcrumb_system import BreadcrumbTrail
from .config import Agent0Config as Config


class CompetitionAnalyzer:
    """
    Analyzes competition level for topics

    Low competition signals:
    - "I can't find anything about X" (unmet need)
    - "Why doesn't X exist?" (market gap)
    - Few quality products in marketplaces
    - Amateur YouTube content with high views

    High competition signals:
    - "Here's my product for X" (existing solutions)
    - Many professional YouTube channels
    - Saturated Amazon/marketplace listings
    - Established brands dominating topic
    """

    def __init__(self, trail: BreadcrumbTrail):
        self.trail = trail

    def analyze_trends_competition(self, trends_data: Dict) -> float:
        """
        Analyze Google Trends for competition signals

        Low competition indicators:
        - Rising trend (new/emerging market)
        - Unstable interest (not yet saturated)
        - Regional concentration (not mainstream yet)

        High competition indicators:
        - Stable high interest (mature market)
        - Consistent plateau (saturated)
        - Declining trend (dying market)

        Returns: 0-100 (higher = more competitive)
        """
        trend_direction = trends_data.get('trend_direction', 'stable')
        average_interest = trends_data.get('average_interest', 0)
        data_points = trends_data.get('data_points', 0)

        if data_points < 10:
            # Not enough data - assume moderate competition
            return 50.0

        # Calculate trend stability (variance indicator)
        # Rising trend = low competition (emerging market)
        # Stable high = high competition (saturated)
        # Falling = high competition (dying market)

        if trend_direction == 'rising':
            base_competition = 20  # Low - emerging opportunity
        elif trend_direction == 'stable':
            # Stable + high interest = saturated
            # Stable + low interest = niche
            if average_interest > 60:
                base_competition = 70  # High - mature/saturated
            else:
                base_competition = 40  # Moderate - niche market
        else:  # falling
            base_competition = 80  # High - declining market

        # Adjust for overall interest level
        # Very high sustained interest often means saturation
        if average_interest > 80:
            base_competition += 10

        return min(base_competition, 100.0)

    def analyze_reddit_competition(self, reddit_data: Dict) -> float:
        """
        Analyze Reddit for existing solutions vs unmet needs

        Low competition signals:
        - Many "Can't find X" mentions
        - "Why doesn't X exist?" questions
        - Pain point posts with few solutions
        - High engagement on problem posts

        High competition signals:
        - "Here's my product/solution" posts
        - Multiple product recommendations
        - Established subreddit communities
        - Saturated with solution discussions

        Uses granular metrics to avoid quantization:
        - Engagement rate (avg_engagement per post)
        - Subreddit concentration index
        - Post volume density

        Returns: 0-100 (higher = more competitive)
        """
        total_posts = reddit_data.get('total_posts', 0)
        avg_engagement = reddit_data.get('avg_engagement', 0)
        top_subreddits = reddit_data.get('top_subreddits', [])

        if total_posts == 0:
            return 50.0  # Unknown - assume moderate

        # GRANULAR METRIC 1: Engagement Rate Per Post
        # This varies continuously even when total_posts is always ~50
        # High engagement/post = passionate community (could be low OR high competition)
        # We interpret high engagement as problem-focused (low competition)
        engagement_per_post = avg_engagement / max(total_posts, 1)

        if engagement_per_post > 200:
            # Very high engagement per post = passionate pain points = low competition
            engagement_score = 20
        elif engagement_per_post > 100:
            # High engagement per post = active discussions = moderate competition
            engagement_score = 35
        elif engagement_per_post > 50:
            # Moderate engagement per post = some solutions = moderate-high competition
            engagement_score = 55
        elif engagement_per_post > 20:
            # Low-moderate engagement = maturing market
            engagement_score = 70
        else:
            # Low engagement per post = either niche or saturated
            engagement_score = 60

        # GRANULAR METRIC 2: Subreddit Concentration Index
        # Spread across many subreddits = mainstream/competitive
        # Concentrated in few = niche opportunity
        subreddit_count = len(top_subreddits)
        if subreddit_count == 0:
            concentration_score = 50  # No data
        elif subreddit_count >= 5:
            # Spread across many communities = mainstream appeal = higher competition
            concentration_score = 75
        elif subreddit_count >= 3:
            # Moderate spread = growing topic
            concentration_score = 55
        elif subreddit_count >= 2:
            # Focused but not isolated = niche opportunity
            concentration_score = 35
        else:  # 1 subreddit
            # Highly concentrated = very niche = low competition
            concentration_score = 25

        # GRANULAR METRIC 3: Post Volume Density
        # Post count relative to engagement
        # Many posts + high engagement = active market (more competitive)
        # Many posts + low engagement = saturated (very competitive)
        if total_posts > 0 and avg_engagement > 0:
            density_ratio = total_posts / (avg_engagement / 100)  # Normalized
            if density_ratio > 5:
                # High density = saturated
                volume_score = 85
            elif density_ratio > 2:
                # Moderate density = competitive
                volume_score = 65
            elif density_ratio > 0.5:
                # Low density = healthy
                volume_score = 45
            else:
                # Very low density = potential gap
                volume_score = 30
        else:
            volume_score = 50

        # Weighted composite
        # Engagement: 40% (primary signal)
        # Concentration: 35% (market spread)
        # Volume: 25% (saturation check)
        base_competition = (
            engagement_score * 0.40 +
            concentration_score * 0.35 +
            volume_score * 0.25
        )

        return min(max(base_competition, 0), 100.0)

    def analyze_youtube_competition(self, youtube_data: Dict) -> float:
        """
        Analyze YouTube for content saturation and quality

        Low competition signals:
        - Few videos despite high views (gap!)
        - Amateur/low-production content
        - High views on simple videos (unmet need)
        - Few recent uploads

        High competition signals:
        - Many professional channels
        - High production value
        - Consistent upload schedule
        - Established creators dominating

        Uses granular metrics to avoid quantization:
        - Engagement rate (views per video)
        - Channel diversity index
        - View distribution variance

        Returns: 0-100 (higher = more competitive)
        """
        total_videos = youtube_data.get('total_videos', 0)
        avg_views = youtube_data.get('avg_views', 0)
        top_channels = youtube_data.get('top_channels', [])

        if total_videos == 0:
            # No videos = either gap or no interest
            # Combined with demand score will determine
            return 30.0  # Assume low competition (potential gap)

        # GRANULAR METRIC 1: Engagement Rate (views per video)
        # This varies continuously even when total_videos is always 20
        engagement_rate = avg_views / max(total_videos, 1)

        # Scale engagement rate to competition score
        # Low views/video = low competition (amateur content)
        # High views/video = high competition (professional quality)
        if engagement_rate > 1000000:  # 1M+ views per video
            engagement_score = 85  # Very professional/competitive
        elif engagement_rate > 500000:  # 500K+ views per video
            engagement_score = 70
        elif engagement_rate > 100000:  # 100K+ views per video
            engagement_score = 55
        elif engagement_rate > 50000:   # 50K+ views per video
            engagement_score = 40
        elif engagement_rate > 10000:   # 10K+ views per video
            engagement_score = 25
        else:  # < 10K views per video
            engagement_score = 15  # Low competition (amateur)

        # GRANULAR METRIC 2: Channel Diversity Index
        # More unique channels = more competitive
        channel_count = len(top_channels)
        if channel_count == 0:
            diversity_score = 20
        else:
            # Normalize: 1 channel = low competition, 5+ = high competition
            diversity_ratio = channel_count / max(total_videos, 1)
            diversity_score = min(diversity_ratio * 100, 100)

        # GRANULAR METRIC 3: Content Saturation Score
        # Video count normalized (but now just one component)
        if total_videos >= 100:
            saturation_score = 90
        elif total_videos >= 50:
            saturation_score = 70
        elif total_videos >= 20:
            saturation_score = 50
        elif total_videos >= 10:
            saturation_score = 30
        else:
            saturation_score = 15

        # Weighted composite (emphasize engagement over count)
        # Engagement: 50% (varies most, breaks quantization)
        # Diversity: 30% (varies based on channels)
        # Saturation: 20% (count-based, less variable)
        base_competition = (
            engagement_score * 0.50 +
            diversity_score * 0.30 +
            saturation_score * 0.20
        )

        # Opportunity gap detection
        # High views per video + few videos = opportunity gap
        if total_videos < 30 and engagement_rate > 500000:
            base_competition -= 15  # Significant opportunity

        return min(max(base_competition, 0), 100.0)

    def calculate_overall_competition(
        self,
        trends_data: Dict,
        reddit_data: Dict,
        youtube_data: Dict
    ) -> Dict:
        """
        Calculate overall competition score from all sources

        Returns dict with:
        - trends_competition: 0-100
        - reddit_competition: 0-100
        - youtube_competition: 0-100
        - overall_competition: 0-100 (weighted average)
        - competition_level: 'low', 'moderate', 'high', 'very_high'
        """
        self.trail.light(Config.LED_SCORING_START + 4, {
            "action": "analyze_competition"
        })

        trends_comp = self.analyze_trends_competition(trends_data)
        reddit_comp = self.analyze_reddit_competition(reddit_data)
        youtube_comp = self.analyze_youtube_competition(youtube_data)

        # Weighted average (equal weights for now)
        overall = (trends_comp + reddit_comp + youtube_comp) / 3.0

        # Categorize competition level
        if overall < 30:
            level = 'low'
            emoji = '🟢'
            description = 'LOW - OPPORTUNITY!'
        elif overall < 50:
            level = 'moderate'
            emoji = '🟡'
            description = 'MODERATE'
        elif overall < 70:
            level = 'high'
            emoji = '🟠'
            description = 'HIGH'
        else:
            level = 'very_high'
            emoji = '🔴'
            description = 'VERY HIGH - SATURATED'

        result = {
            "trends_competition": round(trends_comp, 2),
            "reddit_competition": round(reddit_comp, 2),
            "youtube_competition": round(youtube_comp, 2),
            "overall_competition": round(overall, 2),
            "competition_level": level,
            "competition_emoji": emoji,
            "competition_description": description
        }

        self.trail.light(Config.LED_SCORING_START + 5, {
            "action": "competition_analysis_complete",
            **result
        })

        return result

    def calculate_opportunity_score(
        self,
        demand_score: float,
        competition_score: float
    ) -> Dict:
        """
        Calculate opportunity score (demand vs competition)

        Formula: demand × (1 - competition/100)

        Examples:
        - Demand 85, Competition 25 = 85 × 0.75 = 63.75 🟢 (pursue!)
        - Demand 85, Competition 75 = 85 × 0.25 = 21.25 🔴 (avoid)
        - Demand 45, Competition 10 = 45 × 0.90 = 40.50 🔵 (risky niche)

        Returns dict with:
        - opportunity_score: 0-100
        - recommendation: 'high_priority', 'viable', 'risky', 'avoid'
        - recommendation_emoji: emoji indicator
        """
        # Calculate opportunity (demand adjusted by competition)
        opportunity = demand_score * (1 - competition_score / 100)

        # Categorize opportunity
        if opportunity >= 60:
            recommendation = 'high_priority'
            emoji = '🟢'
            description = 'HIGH PRIORITY - Strong demand, low competition'
            risk = 'LOW'
        elif opportunity >= 45:
            recommendation = 'viable'
            emoji = '🟡'
            description = 'VIABLE - Good opportunity with effort'
            risk = 'MODERATE'
        elif opportunity >= 30:
            recommendation = 'risky'
            emoji = '🔵'
            description = 'RISKY - Need strong differentiation'
            risk = 'HIGH'
        else:
            recommendation = 'avoid'
            emoji = '🔴'
            description = 'AVOID - Poor opportunity'
            risk = 'VERY HIGH'

        # Determine complexity level
        if demand_score >= 70 and competition_score <= 30:
            complexity = 'SIMPLE'
            complexity_desc = 'First-time ebook creator friendly'
        elif demand_score >= 50 and competition_score <= 50:
            complexity = 'MODERATE'
            complexity_desc = 'Standard ebook approach works'
        elif demand_score >= 50:
            complexity = 'COMPLEX'
            complexity_desc = 'Need unique angle or superior quality'
        else:
            complexity = 'VERY COMPLEX'
            complexity_desc = 'Market validation required'

        result = {
            "opportunity_score": round(opportunity, 2),
            "recommendation": recommendation,
            "recommendation_emoji": emoji,
            "recommendation_description": description,
            "risk_level": risk,
            "complexity": complexity,
            "complexity_description": complexity_desc,
            "demand_score": demand_score,
            "competition_score": competition_score
        }

        self.trail.light(Config.LED_SCORING_START + 6, {
            "action": "opportunity_calculated",
            **result
        })

        return result

    def calculate_audience_size(
        self,
        trends_data: Dict,
        reddit_data: Dict,
        youtube_data: Dict
    ) -> int:
        """
        Calculate total addressable market size (audience reach)

        This metric shows market scale, not just demand score.
        Used for bubble sizing in visualization.

        Formula:
        - Google Trends average interest × 100,000 (represents search volume proxy)
        - Reddit total engagement (posts × avg score)
        - YouTube total views

        Returns: Integer representing estimated audience size
        """
        # Google Trends: Average interest as search volume proxy
        trends_interest = trends_data.get('average_interest', 0)
        trends_audience = int(trends_interest * 100000)  # Scale factor

        # Reddit: Engagement metric (posts × average score)
        reddit_posts = reddit_data.get('total_posts', 0)
        reddit_engagement = reddit_data.get('avg_engagement', 0)
        reddit_audience = int(reddit_posts * reddit_engagement)

        # YouTube: Total views across all videos
        youtube_views = youtube_data.get('total_videos', 0) * youtube_data.get('avg_views', 0)
        youtube_audience = int(youtube_views)

        # Total addressable audience (sum of all channels)
        total_audience = trends_audience + reddit_audience + youtube_audience

        return max(total_audience, 1000)  # Minimum 1K for visibility

    def get_competitive_insights(
        self,
        trends_data: Dict,
        reddit_data: Dict,
        youtube_data: Dict,
        opportunity: Dict
    ) -> List[str]:
        """
        Generate actionable competitive insights

        Returns list of insight strings for dashboard
        """
        insights = []

        # Demand insights
        demand = opportunity['demand_score']
        if demand >= 80:
            insights.append("✅ Strong validated demand")
        elif demand >= 60:
            insights.append("✅ Good demand signals")
        elif demand >= 40:
            insights.append("⚠️ Moderate demand - validate carefully")
        else:
            insights.append("🔴 Weak demand signals")

        # Competition insights
        comp = opportunity['competition_score']
        if comp <= 30:
            insights.append("✅ Low competition - market gap opportunity")
        elif comp <= 50:
            insights.append("🟡 Moderate competition - differentiation needed")
        elif comp <= 70:
            insights.append("⚠️ High competition - strong positioning required")
        else:
            insights.append("🔴 Very competitive - avoid or find unique angle")

        # Trend insights
        trend_dir = trends_data.get('trend_direction', 'stable')
        if trend_dir == 'rising':
            insights.append("✅ Rising trend - early mover advantage")
        elif trend_dir == 'falling':
            insights.append("🔴 Declining trend - market may be dying")

        # Content gap insights
        videos = youtube_data.get('total_videos', 0)
        avg_views = youtube_data.get('avg_views', 0)
        if videos < 30 and avg_views > 100000:
            insights.append("✅ Content gap - high views, few videos!")

        # Reddit insights
        reddit_posts = reddit_data.get('total_posts', 0)
        reddit_engagement = reddit_data.get('avg_engagement', 0)
        if reddit_posts > 30 and reddit_engagement > 1000:
            insights.append("✅ Active community with pain points")

        return insights
