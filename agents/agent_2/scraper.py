"""
Data Scraper - Load review/comment data from Agent 1 or direct sources

LED Range: 2510-2539
"""

import json
import os
from typing import Dict, Any, List
from pathlib import Path


class DataScraper:
    """Load and prepare review/comment data for demographic extraction"""

    def __init__(self, trail, config):
        """
        Initialize data scraper

        Args:
            trail: BreadcrumbTrail for LED tracking
            config: Agent2Config for limits
        """
        self.trail = trail
        self.config = config

    def load_from_agent1(self, agent1_output_path: str) -> Dict[str, Any]:
        """
        Load data from Agent 1 output file

        Args:
            agent1_output_path: Path to Agent 1's JSON output

        Returns:
            Dict with reviews/comments organized by source

        Raises:
            FileNotFoundError: If Agent 1 output doesn't exist
            ValueError: If Agent 1 output is invalid
        """
        if not os.path.exists(agent1_output_path):
            raise FileNotFoundError(
                f"Agent 1 output not found: {agent1_output_path}\n"
                f"Please run Agent 1 first to collect product data, or provide test data."
            )

        self.trail.light(2510, {
            "action": "loading_agent1_data",
            "path": agent1_output_path
        })

        try:
            with open(agent1_output_path, 'r', encoding='utf-8') as f:
                agent1_data = json.load(f)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in Agent 1 output: {e}")

        # Validate Agent 1 data structure
        if 'comparables' not in agent1_data:
            raise ValueError("Agent 1 output missing 'comparables' field")

        # Extract reviews/comments from Agent 1 data
        amazon_reviews = self._extract_amazon_reviews(agent1_data)
        reddit_comments = self._extract_reddit_comments(agent1_data)
        youtube_comments = self._extract_youtube_comments(agent1_data)

        total_data_points = len(amazon_reviews) + len(reddit_comments) + len(youtube_comments)

        self.trail.light(2511, {
            "action": "agent1_data_loaded",
            "amazon_reviews": len(amazon_reviews),
            "reddit_comments": len(reddit_comments),
            "youtube_comments": len(youtube_comments),
            "total_data_points": total_data_points
        })

        print(f"[OK] Loaded {total_data_points} data points from Agent 1")
        print(f"     Amazon: {len(amazon_reviews)} reviews")
        print(f"     Reddit: {len(reddit_comments)} comments")
        print(f"     YouTube: {len(youtube_comments)} comments")

        if total_data_points < self.config.MIN_DATA_POINTS_REQUIRED:
            print(f"[!] WARNING: Only {total_data_points} data points (minimum: {self.config.MIN_DATA_POINTS_REQUIRED})")
            print(f"    This may result in low confidence scores")

        return {
            "amazon": amazon_reviews,
            "reddit": reddit_comments,
            "youtube": youtube_comments,
            "total_data_points": total_data_points
        }

    def load_from_test_data(self, test_data_path: str) -> Dict[str, Any]:
        """
        Load data from test data file for development/testing

        Args:
            test_data_path: Path to test data JSON file

        Returns:
            Dict with reviews/comments organized by source

        Raises:
            FileNotFoundError: If test data doesn't exist
            ValueError: If test data is invalid
        """
        if not os.path.exists(test_data_path):
            raise FileNotFoundError(
                f"Test data not found: {test_data_path}\n"
                f"Create test data in the format: {{'amazon': [], 'reddit': [], 'youtube': []}}"
            )

        self.trail.light(2512, {
            "action": "loading_test_data",
            "path": test_data_path
        })

        try:
            with open(test_data_path, 'r', encoding='utf-8') as f:
                test_data = json.load(f)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in test data: {e}")

        # Validate test data structure
        amazon_reviews = test_data.get('amazon', [])
        reddit_comments = test_data.get('reddit', [])
        youtube_comments = test_data.get('youtube', [])

        total_data_points = len(amazon_reviews) + len(reddit_comments) + len(youtube_comments)

        if total_data_points == 0:
            raise ValueError("Test data contains no reviews/comments")

        self.trail.light(2513, {
            "action": "test_data_loaded",
            "amazon_reviews": len(amazon_reviews),
            "reddit_comments": len(reddit_comments),
            "youtube_comments": len(youtube_comments),
            "total_data_points": total_data_points
        })

        print(f"[OK] Loaded {total_data_points} data points from test data")

        return {
            "amazon": amazon_reviews,
            "reddit": reddit_comments,
            "youtube": youtube_comments,
            "total_data_points": total_data_points
        }

    def _extract_amazon_reviews(self, agent1_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract Amazon reviews from Agent 1 data"""
        reviews = []
        comparables = agent1_data.get('comparables', [])

        for comparable in comparables:
            # Agent 1 stores reviews in comparable['reviews']
            comparable_reviews = comparable.get('reviews', [])

            for review in comparable_reviews[:self.config.MAX_AMAZON_REVIEWS_PER_PRODUCT]:
                reviews.append({
                    "id": f"amazon_{len(reviews)}",
                    "text": review.get('text', review.get('review_text', '')),
                    "source": "amazon",
                    "product": comparable.get('title', 'unknown')
                })

        return reviews

    def _extract_reddit_comments(self, agent1_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract Reddit comments from Agent 1 data"""
        comments = []

        # Agent 1 stores Reddit discussions in discussion_urls
        discussions = agent1_data.get('discussion_urls', [])

        for discussion in discussions:
            discussion_comments = discussion.get('comments', [])

            for comment in discussion_comments[:self.config.MAX_REDDIT_COMMENTS_PER_THREAD]:
                comments.append({
                    "id": f"reddit_{len(comments)}",
                    "text": comment.get('text', comment.get('body', '')),
                    "source": "reddit",
                    "thread": discussion.get('url', 'unknown')
                })

        return comments

    def _extract_youtube_comments(self, agent1_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract YouTube comments from Agent 1 data"""
        comments = []

        # Agent 1 stores YouTube videos in video_urls or similar
        videos = agent1_data.get('video_urls', [])

        for video in videos:
            video_comments = video.get('comments', [])

            for comment in video_comments[:self.config.MAX_YOUTUBE_COMMENTS_PER_VIDEO]:
                comments.append({
                    "id": f"youtube_{len(comments)}",
                    "text": comment.get('text', comment.get('textDisplay', '')),
                    "source": "youtube",
                    "video": video.get('url', 'unknown')
                })

        return comments

    def prepare_source_datasets(self, all_data: Dict[str, Any]) -> Dict[str, List[Dict[str, Any]]]:
        """
        Prepare separate datasets for each source

        Args:
            all_data: Dict with amazon, reddit, youtube lists

        Returns:
            Dict with source name -> list of reviews/comments
        """
        return {
            "amazon": all_data.get('amazon', []),
            "reddit": all_data.get('reddit', []),
            "youtube": all_data.get('youtube', [])
        }
