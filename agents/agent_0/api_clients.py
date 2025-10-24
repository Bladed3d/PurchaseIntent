"""
Agent 0 API Clients
Handles integration with Google Trends, Reddit, and YouTube APIs
"""

import time
from typing import Dict, List, Optional
from pytrends.request import TrendReq
import praw
from googleapiclient.discovery import build

from lib.breadcrumb_system import BreadcrumbTrail
from .config import Agent0Config as Config


class GoogleTrendsClient:
    """Google Trends API client using pytrends"""

    def __init__(self, trail: BreadcrumbTrail):
        self.trail = trail
        self.pytrends = TrendReq(hl='en-US', tz=360)

    def get_trend_data(self, keyword: str) -> Dict:
        """
        Query Google Trends for keyword interest over time

        Returns dict with:
        - average_interest: 0-100 score
        - peak_interest: highest interest point
        - trend_direction: 'rising', 'falling', 'stable'
        - data_points: number of data points returned
        """
        self.trail.light(Config.LED_GOOGLE_TRENDS_START, {
            "action": "query_google_trends",
            "keyword": keyword
        })

        try:
            # Build payload and query
            self.pytrends.build_payload([keyword], timeframe='today 12-m')

            # Respect rate limits
            time.sleep(Config.GOOGLE_TRENDS_DELAY)

            # Get interest over time
            data = self.pytrends.interest_over_time()

            if data.empty or keyword not in data.columns:
                self.trail.light(Config.LED_GOOGLE_TRENDS_START + 1, {
                    "action": "no_data",
                    "keyword": keyword
                })
                return {
                    "average_interest": 0,
                    "peak_interest": 0,
                    "trend_direction": "no_data",
                    "data_points": 0
                }

            # Calculate metrics
            interest_values = data[keyword].values
            average = float(interest_values.mean())
            peak = float(interest_values.max())

            # Determine trend direction (compare first half to second half)
            mid = len(interest_values) // 2
            first_half_avg = interest_values[:mid].mean()
            second_half_avg = interest_values[mid:].mean()

            if second_half_avg > first_half_avg * 1.1:
                trend_direction = "rising"
            elif second_half_avg < first_half_avg * 0.9:
                trend_direction = "falling"
            else:
                trend_direction = "stable"

            result = {
                "average_interest": round(average, 2),
                "peak_interest": round(peak, 2),
                "trend_direction": trend_direction,
                "data_points": len(interest_values)
            }

            self.trail.light(Config.LED_GOOGLE_TRENDS_START + 2, {
                "action": "trends_success",
                "keyword": keyword,
                **result
            })

            return result

        except Exception as e:
            self.trail.fail(Config.LED_GOOGLE_TRENDS_START + 2, e)
            return {
                "average_interest": 0,
                "peak_interest": 0,
                "trend_direction": "error",
                "data_points": 0,
                "error": str(e)
            }


class RedditClient:
    """Reddit API client using PRAW"""

    def __init__(self, trail: BreadcrumbTrail):
        self.trail = trail
        self.reddit = praw.Reddit(
            client_id=Config.REDDIT_CLIENT_ID,
            client_secret=Config.REDDIT_CLIENT_SECRET,
            user_agent=Config.REDDIT_USER_AGENT
        )

    def search_topic(self, keyword: str) -> Dict:
        """
        Search Reddit for keyword and analyze engagement

        Returns dict with:
        - total_posts: number of relevant posts found
        - total_engagement: sum of scores (upvotes - downvotes)
        - avg_engagement: average score per post
        - top_subreddits: list of most relevant subreddits
        """
        self.trail.light(Config.LED_REDDIT_START, {
            "action": "search_reddit",
            "keyword": keyword
        })

        try:
            # Search across all of Reddit
            posts = list(self.reddit.subreddit('all').search(
                keyword,
                limit=Config.MAX_REDDIT_POSTS,
                sort='relevance'
            ))

            # Respect rate limits
            time.sleep(Config.RATE_LIMIT_DELAY)

            if not posts:
                self.trail.light(Config.LED_REDDIT_START + 1, {
                    "action": "no_posts",
                    "keyword": keyword
                })
                return {
                    "total_posts": 0,
                    "total_engagement": 0,
                    "avg_engagement": 0,
                    "top_subreddits": []
                }

            # Calculate metrics
            total_engagement = sum(post.score for post in posts)
            avg_engagement = total_engagement / len(posts) if posts else 0

            # Find top subreddits
            subreddit_counts = {}
            for post in posts:
                sub = post.subreddit.display_name
                subreddit_counts[sub] = subreddit_counts.get(sub, 0) + 1

            top_subreddits = sorted(
                subreddit_counts.items(),
                key=lambda x: x[1],
                reverse=True
            )[:5]

            result = {
                "total_posts": len(posts),
                "total_engagement": total_engagement,
                "avg_engagement": round(avg_engagement, 2),
                "top_subreddits": [{"name": name, "count": count} for name, count in top_subreddits]
            }

            self.trail.light(Config.LED_REDDIT_START + 2, {
                "action": "reddit_success",
                "keyword": keyword,
                **result
            })

            return result

        except Exception as e:
            self.trail.fail(Config.LED_REDDIT_START + 2, e)
            return {
                "total_posts": 0,
                "total_engagement": 0,
                "avg_engagement": 0,
                "top_subreddits": [],
                "error": str(e)
            }


class YouTubeClient:
    """YouTube Data API v3 client"""

    def __init__(self, trail: BreadcrumbTrail):
        self.trail = trail
        self.youtube = build('youtube', 'v3', developerKey=Config.YOUTUBE_API_KEY)

    def search_videos(self, keyword: str) -> Dict:
        """
        Search YouTube for keyword and analyze video metrics

        Returns dict with:
        - total_videos: number of videos found
        - total_views: sum of view counts
        - avg_views: average views per video
        - top_channels: list of most relevant channels
        """
        self.trail.light(Config.LED_YOUTUBE_START, {
            "action": "search_youtube",
            "keyword": keyword
        })

        try:
            # Search for videos
            search_response = self.youtube.search().list(
                q=keyword,
                part='id,snippet',
                type='video',
                maxResults=Config.MAX_YOUTUBE_VIDEOS,
                order='relevance'
            ).execute()

            # Respect rate limits
            time.sleep(Config.RATE_LIMIT_DELAY)

            video_ids = [item['id']['videoId'] for item in search_response.get('items', [])]

            if not video_ids:
                self.trail.light(Config.LED_YOUTUBE_START + 1, {
                    "action": "no_videos",
                    "keyword": keyword
                })
                return {
                    "total_videos": 0,
                    "total_views": 0,
                    "avg_views": 0,
                    "top_channels": []
                }

            # Get video statistics
            videos_response = self.youtube.videos().list(
                id=','.join(video_ids),
                part='statistics,snippet'
            ).execute()

            # Calculate metrics
            videos = videos_response.get('items', [])
            total_views = sum(
                int(video['statistics'].get('viewCount', 0))
                for video in videos
            )
            avg_views = total_views / len(videos) if videos else 0

            # Find top channels
            channel_counts = {}
            for video in videos:
                channel = video['snippet']['channelTitle']
                channel_counts[channel] = channel_counts.get(channel, 0) + 1

            top_channels = sorted(
                channel_counts.items(),
                key=lambda x: x[1],
                reverse=True
            )[:5]

            result = {
                "total_videos": len(videos),
                "total_views": total_views,
                "avg_views": round(avg_views, 2),
                "top_channels": [{"name": name, "count": count} for name, count in top_channels]
            }

            self.trail.light(Config.LED_YOUTUBE_START + 2, {
                "action": "youtube_success",
                "keyword": keyword,
                **result
            })

            return result

        except Exception as e:
            self.trail.fail(Config.LED_YOUTUBE_START + 2, e)
            return {
                "total_videos": 0,
                "total_views": 0,
                "avg_views": 0,
                "top_channels": [],
                "error": str(e)
            }
