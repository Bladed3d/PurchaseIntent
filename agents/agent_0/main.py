"""
Agent 0: Topic Research Agent - Main Entry Point

Discovers and validates demand for product topics by analyzing:
- Google Trends (search volume patterns)
- Reddit (community discussions and pain points)
- YouTube (video engagement and content volume)

Usage:
    python agents/agent_0/main.py <topic1> <topic2> ... <topicN>
    python agents/agent_0/main.py "romance novels" "productivity apps" "meal prep"

LED Range: 500-599
Output: outputs/topic-selection.json, outputs/agent0-dashboard.html
"""

import sys
import os
import time
from typing import List

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from lib.breadcrumb_system import BreadcrumbTrail
from agents.agent_0.config import Agent0Config as Config
from agents.agent_0.api_clients import GoogleTrendsClient, RedditClient, YouTubeClient
from agents.agent_0.scoring import TopicScorer
from agents.agent_0.dashboard import DashboardGenerator


def main(topics: List[str]):
    """
    Main execution function for Agent 0

    Args:
        topics: List of topic strings to research

    Returns:
        Path to output JSON file
    """
    # Initialize LED breadcrumb trail
    trail = BreadcrumbTrail("Agent0_TopicResearch")

    trail.light(Config.LED_INIT, {
        "action": "agent_0_started",
        "topics_count": len(topics),
        "topics": topics
    })

    # Validate configuration
    try:
        Config.validate()
        trail.light(Config.LED_INIT + 1, {
            "action": "config_validated"
        })
    except ValueError as e:
        trail.fail(Config.LED_INIT + 1, e)
        print(f"\n[FAIL] Configuration error: {e}")
        return None

    # Initialize API clients
    trail.light(Config.LED_INIT + 2, {
        "action": "initializing_api_clients"
    })

    trends_client = GoogleTrendsClient(trail)
    reddit_client = RedditClient(trail)
    youtube_client = YouTubeClient(trail)
    scorer = TopicScorer(trail)
    dashboard_gen = DashboardGenerator(trail)

    # Research each topic
    topic_data = []

    for idx, topic in enumerate(topics, 1):
        print(f"\n{'='*60}")
        print(f"Researching topic {idx}/{len(topics)}: {topic}")
        print(f"{'='*60}")

        trail.light(Config.LED_INIT + 3, {
            "action": "researching_topic",
            "topic": topic,
            "index": idx
        })

        # Query Google Trends
        print("  [1/3] Querying Google Trends...")
        trends_data = trends_client.get_trend_data(topic)

        # Query Reddit
        print("  [2/3] Querying Reddit...")
        reddit_data = reddit_client.search_topic(topic)

        # Query YouTube
        print("  [3/3] Querying YouTube...")
        youtube_data = youtube_client.search_videos(topic)

        # Calculate scores
        print("  [*] Calculating composite score...")
        scores = scorer.calculate_composite_score(
            trends_data,
            reddit_data,
            youtube_data
        )

        # Store results
        topic_data.append({
            "topic": topic,
            "scores": scores,
            "trends_data": trends_data,
            "reddit_data": reddit_data,
            "youtube_data": youtube_data
        })

        print(f"  [OK] Composite Score: {scores['composite_score']:.2f} (Confidence: {scores['confidence']}%)")

    # Rank topics
    print(f"\n{'='*60}")
    print("Ranking topics...")
    print(f"{'='*60}")

    ranked_topics = scorer.rank_topics(topic_data)

    # Display results
    print("\nTop Topics:")
    for idx, topic in enumerate(ranked_topics[:5], 1):
        print(f"  {idx}. {topic['topic']} - Score: {topic['scores']['composite_score']:.2f}")

    # Generate outputs
    print(f"\n{'='*60}")
    print("Generating outputs...")
    print(f"{'='*60}")

    # Create output directory
    os.makedirs(Config.OUTPUT_DIR, exist_ok=True)

    # Generate HTML dashboard
    html_path = dashboard_gen.generate_html(ranked_topics, Config.OUTPUT_HTML)
    print(f"  [OK] HTML Dashboard: {html_path}")

    # Generate JSON output
    json_path = dashboard_gen.generate_json_output(ranked_topics, Config.OUTPUT_JSON)
    print(f"  [OK] JSON Output: {json_path}")

    # Open dashboard in browser
    print("\n  [*] Opening dashboard in browser...")
    dashboard_gen.open_dashboard(html_path)

    # Completion
    trail.light(Config.LED_OUTPUT_START + 2, {
        "action": "agent_0_complete",
        "topics_analyzed": len(topics),
        "top_topic": ranked_topics[0]['topic'] if ranked_topics else None,
        "output_json": json_path,
        "output_html": html_path
    })

    # Print summary
    summary = trail.get_verification_summary()
    print(f"\n{'='*60}")
    print("Agent 0 Execution Summary")
    print(f"{'='*60}")
    print(f"Total LEDs: {summary['total_leds']}")
    print(f"Failures: {summary['failures']}")
    print(f"Quality Score: {trail.get_quality_score()}%")
    print(f"Verification Passed: {summary['verification_passed']}")
    print(f"{'='*60}\n")

    return json_path


if __name__ == "__main__":
    # Parse command line arguments
    if len(sys.argv) < 2:
        print("Usage: python agents/agent_0/main.py <topic1> <topic2> ... <topicN>")
        print("\nExample:")
        print('  python agents/agent_0/main.py "romance novels" "productivity apps"')
        sys.exit(1)

    topics = sys.argv[1:]

    # Limit to MAX_TOPICS
    if len(topics) > Config.MAX_TOPICS:
        print(f"[!] Warning: Limiting to {Config.MAX_TOPICS} topics (configured max)")
        topics = topics[:Config.MAX_TOPICS]

    # Run Agent 0
    output_path = main(topics)

    if output_path:
        print(f"\n[OK] Agent 0 completed successfully!")
        print(f"[OK] Output: {output_path}")
        sys.exit(0)
    else:
        print(f"\n[FAIL] Agent 0 failed - check logs for details")
        sys.exit(1)
