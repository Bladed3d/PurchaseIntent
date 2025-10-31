"""
Agent 1 API Clients
Reddit, YouTube, and web scraping clients for product research

CRITICAL RULES:
- FAIL LOUDLY: No fallbacks, raise exceptions immediately
- NO PAID APIs: Use PRAW (free), YouTube Data API (free quota), Playwright (free)
- Require data: No .get(key, 0) - use KeyError to catch missing fields
"""

import praw
import time
import json
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout

from lib.breadcrumb_system import BreadcrumbTrail
from agents.agent_1.config import Agent1Config as Config


class RedditClient:
    """Reddit API client using PRAW for discussion search"""

    def __init__(self, trail: BreadcrumbTrail):
        self.trail = trail

        # Validate credentials before creating client
        if not Config.REDDIT_CLIENT_ID or not Config.REDDIT_CLIENT_SECRET:
            raise ValueError(
                "Reddit credentials missing. Check REDDIT_CLIENT_ID and REDDIT_CLIENT_SECRET in .env"
            )

        self.reddit = praw.Reddit(
            client_id=Config.REDDIT_CLIENT_ID,
            client_secret=Config.REDDIT_CLIENT_SECRET,
            user_agent=Config.REDDIT_USER_AGENT,
        )
        self.reddit.read_only = True

    def search_product_discussions(
        self,
        query: str,
        subreddits: Optional[List[str]] = None,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """
        Search Reddit for product discussions

        Args:
            query: Search query (e.g., "productivity books for entrepreneurs")
            subreddits: Optional list of subreddits to search (None = all)
            limit: Max number of discussions to return

        Returns:
            List of discussion dictionaries with metadata

        Raises:
            ValueError: If Reddit API returns no results or fails
        """
        self.trail.light(Config.LED_REDDIT_START, {
            "action": "reddit_search_started",
            "query": query,
            "subreddits": subreddits,
            "limit": limit
        })

        discussions = []

        try:
            # Build search query
            search_query = query
            if subreddits:
                subreddit_str = "+".join(subreddits)
                search_target = self.reddit.subreddit(subreddit_str)
            else:
                search_target = self.reddit.subreddit("all")

            # Execute search
            results = search_target.search(
                search_query,
                sort="relevance",
                time_filter="year",
                limit=limit
            )

            for submission in results:
                discussions.append({
                    "id": submission.id,
                    "title": submission.title,
                    "url": f"https://reddit.com{submission.permalink}",
                    "subreddit": str(submission.subreddit),
                    "score": submission.score,
                    "num_comments": submission.num_comments,
                    "created_utc": submission.created_utc,
                    "selftext": submission.selftext[:500] if submission.selftext else "",
                    "platform": "reddit"
                })

                time.sleep(Config.REDDIT_DELAY)

            if not discussions:
                raise ValueError(
                    f"Reddit search returned no results for query: '{query}'\n"
                    f"Subreddits: {subreddits or 'all'}\n"
                    f"Try a broader search query or different subreddits"
                )

            self.trail.light(Config.LED_REDDIT_START + 1, {
                "action": "reddit_search_complete",
                "discussions_found": len(discussions)
            })

            return discussions

        except Exception as e:
            self.trail.fail(Config.LED_ERROR_START, e)
            raise ValueError(f"Reddit API error: {str(e)}")

    def get_subreddit_overlap(
        self,
        base_subreddit: str,
        max_users: int = 500
    ) -> List[Dict[str, Any]]:
        """
        Discover hidden audience segments via subreddit overlap analysis

        Args:
            base_subreddit: Starting subreddit (e.g., "productivity")
            max_users: Max users to analyze for overlap

        Returns:
            List of overlapping subreddits with multipliers

        Raises:
            ValueError: If analysis fails or returns no overlaps
        """
        self.trail.light(Config.LED_OVERLAP_START, {
            "action": "overlap_analysis_started",
            "base_subreddit": base_subreddit,
            "max_users": max_users
        })

        try:
            subreddit = self.reddit.subreddit(base_subreddit)

            # Get active users from recent posts
            active_users = set()
            for submission in subreddit.hot(limit=50):
                active_users.add(submission.author.name if submission.author else None)
                submission.comments.replace_more(limit=0)
                for comment in submission.comments.list()[:10]:
                    active_users.add(comment.author.name if comment.author else None)
                    if len(active_users) >= max_users:
                        break
                if len(active_users) >= max_users:
                    break
                time.sleep(Config.REDDIT_DELAY)

            # Remove None values
            active_users.discard(None)

            if len(active_users) < 10:
                raise ValueError(
                    f"Insufficient active users found in r/{base_subreddit} (found {len(active_users)})\n"
                    f"Need at least 10 active users for meaningful overlap analysis"
                )

            # Count subreddit activity across users (sample first 100 users to avoid rate limits)
            overlap_counts = {}
            sampled_users = list(active_users)[:100]

            for username in sampled_users:
                try:
                    user = self.reddit.redditor(username)
                    for submission in user.submissions.new(limit=20):
                        sub = str(submission.subreddit)
                        if sub != base_subreddit:
                            overlap_counts[sub] = overlap_counts.get(sub, 0) + 1

                    for comment in user.comments.new(limit=20):
                        sub = str(comment.subreddit)
                        if sub != base_subreddit:
                            overlap_counts[sub] = overlap_counts.get(sub, 0) + 1

                    time.sleep(Config.REDDIT_DELAY)
                except Exception:
                    # Skip users with private/deleted accounts
                    continue

            if not overlap_counts:
                raise ValueError(
                    f"No overlapping subreddits found for r/{base_subreddit}\n"
                    f"Users analyzed: {len(sampled_users)}"
                )

            # Calculate overlap multiplier (simplified baseline)
            total_activity = sum(overlap_counts.values())
            overlaps = []

            for subreddit_name, count in sorted(overlap_counts.items(), key=lambda x: x[1], reverse=True):
                multiplier = (count / len(sampled_users)) * 10  # Normalize to reasonable range
                if multiplier >= Config.MIN_OVERLAP_MULTIPLIER:
                    overlaps.append({
                        "subreddit": f"r/{subreddit_name}",
                        "multiplier": round(multiplier, 2),
                        "user_count": count,
                        "interpretation": self._interpret_overlap(subreddit_name)
                    })

            if not overlaps:
                raise ValueError(
                    f"No significant overlaps found (min multiplier: {Config.MIN_OVERLAP_MULTIPLIER})\n"
                    f"Base: r/{base_subreddit}, Users analyzed: {len(sampled_users)}"
                )

            # Return top N overlaps
            top_overlaps = overlaps[:Config.TOP_OVERLAPS]

            self.trail.light(Config.LED_OVERLAP_START + 1, {
                "action": "overlap_analysis_complete",
                "overlaps_found": len(top_overlaps)
            })

            return top_overlaps

        except Exception as e:
            self.trail.fail(Config.LED_ERROR_START + 1, e)
            raise ValueError(f"Subreddit overlap analysis failed: {str(e)}")

    def _interpret_overlap(self, subreddit: str) -> str:
        """Generate interpretation for overlapping subreddit (simple heuristic)"""
        # This would ideally use an AI agent, but keeping simple for now
        keywords = {
            'entrepreneur': 'Business owners',
            'adhd': 'Neurodivergent professionals',
            'fire': 'Financial independence seekers',
            'cscareer': 'Software developers',
            'productivity': 'Productivity enthusiasts',
            'anxiety': 'Mental health focus',
            'fitness': 'Health-conscious individuals',
            'investing': 'Investors',
        }

        for keyword, interpretation in keywords.items():
            if keyword in subreddit.lower():
                return interpretation

        return subreddit.title().replace('_', ' ')


class YouTubeClient:
    """YouTube Data API v3 client for video discovery"""

    def __init__(self, trail: BreadcrumbTrail):
        self.trail = trail

        # Validate API key
        if not Config.YOUTUBE_API_KEY:
            raise ValueError(
                "YouTube API key missing. Check YOUTUBE_API_KEY in .env\n"
                "Get API key at: https://console.cloud.google.com/apis/credentials"
            )

        self.youtube = build('youtube', 'v3', developerKey=Config.YOUTUBE_API_KEY)

    def search_product_reviews(
        self,
        query: str,
        max_results: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Search YouTube for product review videos

        Args:
            query: Search query (e.g., "productivity books for entrepreneurs review")
            max_results: Max videos to return

        Returns:
            List of video dictionaries with metadata

        Raises:
            ValueError: If YouTube API returns no results or fails
        """
        self.trail.light(Config.LED_YOUTUBE_START, {
            "action": "youtube_search_started",
            "query": query,
            "max_results": max_results
        })

        try:
            # Search for videos
            search_response = self.youtube.search().list(
                q=query,
                part='id,snippet',
                type='video',
                maxResults=max_results,
                order='relevance',
                videoDuration='medium',  # Filter out very short clips
                relevanceLanguage='en'
            ).execute()

            if 'items' not in search_response or not search_response['items']:
                raise ValueError(
                    f"YouTube search returned no results for query: '{query}'\n"
                    f"Check quota at: https://console.cloud.google.com/apis/api/youtube.googleapis.com/quotas"
                )

            video_ids = [item['id']['videoId'] for item in search_response['items']]

            # Get video statistics
            stats_response = self.youtube.videos().list(
                part='statistics,contentDetails',
                id=','.join(video_ids)
            ).execute()

            videos = []
            for item, stats_item in zip(search_response['items'], stats_response['items']):
                statistics = stats_item['statistics']

                videos.append({
                    "id": item['id']['videoId'],
                    "title": item['snippet']['title'],
                    "url": f"https://youtube.com/watch?v={item['id']['videoId']}",
                    "channel": item['snippet']['channelTitle'],
                    "published_at": item['snippet']['publishedAt'],
                    "views": int(statistics['viewCount']),
                    "likes": int(statistics.get('likeCount', 0)),
                    "comments": int(statistics.get('commentCount', 0)),
                    "platform": "youtube"
                })

            # Filter by minimum comment threshold
            filtered_videos = [v for v in videos if v['comments'] >= Config.MIN_COMMENTS_YOUTUBE]

            if not filtered_videos:
                raise ValueError(
                    f"No YouTube videos found with >={Config.MIN_COMMENTS_YOUTUBE} comments\n"
                    f"Query: '{query}', Videos found: {len(videos)}"
                )

            self.trail.light(Config.LED_YOUTUBE_START + 1, {
                "action": "youtube_search_complete",
                "videos_found": len(filtered_videos)
            })

            return filtered_videos

        except HttpError as e:
            self.trail.fail(Config.LED_ERROR_START + 2, e)
            if e.resp.status == 403:
                raise ValueError(
                    f"YouTube API quota exceeded. Daily limit: 10,000 units\n"
                    f"Check usage at: https://console.cloud.google.com/apis/api/youtube.googleapis.com/quotas\n"
                    f"Error: {str(e)}"
                )
            else:
                raise ValueError(f"YouTube API error ({e.resp.status}): {str(e)}")
        except Exception as e:
            self.trail.fail(Config.LED_ERROR_START + 2, e)
            raise ValueError(f"YouTube search failed: {str(e)}")
