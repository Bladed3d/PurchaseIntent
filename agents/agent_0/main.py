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
from agents.agent_0.api_clients_playwright import GoogleTrendsPlaywrightClient
from agents.agent_0.api_clients_websearch import GoogleTrendsWebSearchClient
from agents.agent_0.agent_results_loader import AgentResultsLoader
from agents.agent_0.scoring import TopicScorer
from agents.agent_0.dashboard import DashboardGenerator
from agents.agent_0.queue_manager import QueueManager


def main(topics: List[str], method: str = "pytrends"):
    """
    Main execution function for Agent 0

    Args:
        topics: List of topic strings to research
        method: Data collection method ("pytrends", "playwright", or "websearch")

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

    # Initialize queue manager for rate limit tracking
    queue_manager = QueueManager(trail)

    # Check batch safety
    batch_check = queue_manager.can_process_batch(topics)
    if not batch_check['safe']:
        print(f"\n[!] WARNING: {batch_check['reason']}")
        print("Recommendations:")
        for rec in batch_check['recommendations']:
            print(f"  - {rec}")

        if batch_check['wait_seconds'] is not None and batch_check['wait_seconds'] > 0:
            print(f"\n[*] Waiting {round(batch_check['wait_seconds'], 1)} seconds before proceeding...")
            time.sleep(batch_check['wait_seconds'])
        else:
            proceed = input("\nProceed anyway? (y/n): ")
            if proceed.lower() != 'y':
                print("Aborted by user.")
                return None

    # Show batch estimate
    estimate = queue_manager.estimate_batch_time(topics)
    print(f"\n[*] Batch Estimate:")
    print(f"  Total topics: {estimate['total_topics']}")
    print(f"  Cached: {estimate['cached_topics']} | New queries: {estimate['new_queries']}")
    print(f"  Estimated time: ~{estimate['estimated_minutes']} min ({estimate['estimated_seconds']}s)")

    # Initialize API clients
    trail.light(Config.LED_INIT + 2, {
        "action": "initializing_api_clients",
        "method": method
    })

    # Choose Google Trends client based on method
    if method == "playwright":
        print(f"[*] Using Playwright browser automation (improved rate limit handling)")
        trends_client = GoogleTrendsPlaywrightClient(trail, queue_manager=queue_manager)
    elif method == "websearch":
        print(f"[*] Using Web Search for trend signals (unlimited queries, no rate limits)")
        print(f"[!] Note: Requires 'googlesearch-python' package")
        print(f"[!] Install with: pip install googlesearch-python")
        trends_client = GoogleTrendsWebSearchClient(trail)
    else:
        print(f"[*] Using PyTrends library (standard method)")
        trends_client = GoogleTrendsClient(trail, queue_manager=queue_manager)

    # Initialize agent results loader (checks for AI research results)
    agent_loader = AgentResultsLoader(trail)

    reddit_client = RedditClient(trail)
    youtube_client = YouTubeClient(trail)
    scorer = TopicScorer(trail)
    dashboard_gen = DashboardGenerator(trail)

    # Check for AI agent results first, then batch query Google Trends
    print(f"\n{'='*60}")
    print(f"Checking for AI agent research results...")
    print(f"{'='*60}")

    # Load agent results for all topics
    agent_results = {}
    topics_needing_trends = []

    for topic in topics:
        agent_data = agent_loader.load_results(topic)
        if agent_data:
            age_hours = agent_loader.get_result_age_hours(topic)
            print(f"  [OK] Found agent results for '{topic}' (age: {age_hours:.1f}h)")
            agent_results[topic] = agent_data
        else:
            print(f"  [ ] No agent results for '{topic}' - will use {method} method")
            topics_needing_trends.append(topic)

    # Query Google Trends only for topics without agent results
    trends_batch_results = {}
    if topics_needing_trends:
        print(f"\n{'='*60}")
        print(f"Querying Google Trends (batched - {len(topics_needing_trends)} topics)...")
        print(f"{'='*60}")
        trends_batch_results = trends_client.get_batch_trend_data(topics_needing_trends)
    else:
        print(f"\n[*] All topics have agent results - skipping Google Trends")

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

        # Get trend data (agent results preferred, Google Trends fallback)
        if topic in agent_results:
            print(f"  [1/3] Using AI agent research data (demand: {agent_results[topic]['demand_score']}, confidence: {agent_results[topic]['confidence']}%)...")
            # Convert agent results to trends format
            trends_data = {
                "average_interest": agent_results[topic]['demand_score'],
                "peak_interest": agent_results[topic]['demand_score'],
                "trend_direction": "stable",
                "data_points": agent_results[topic]['signals']['mention_count'],
                "source": "agent"
            }
        else:
            print("  [1/3] Using batched Google Trends data...")
            trends_data = trends_batch_results.get(topic, {
                "average_interest": 0,
                "peak_interest": 0,
                "trend_direction": "no_data",
                "data_points": 0,
                "source": "google_trends"
            })

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

    # Generate HTML dashboard (with queue manager for rate limit indicator)
    html_path = dashboard_gen.generate_html(ranked_topics, Config.OUTPUT_HTML, queue_manager=queue_manager)
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
    api_stats = queue_manager.get_calls_last_hour()

    print(f"\n{'='*60}")
    print("Agent 0 Execution Summary")
    print(f"{'='*60}")
    print(f"Total LEDs: {summary['total_leds']}")
    print(f"Failures: {summary['failures']}")
    print(f"Quality Score: {trail.get_quality_score()}%")
    print(f"Verification Passed: {summary['verification_passed']}")
    print(f"\n[*] API Usage (Last Hour):")
    print(f"  Total queries: {api_stats['total_calls']}")
    print(f"  Actual API calls: {api_stats['actual_api_calls']}")
    print(f"  Cache hits: {api_stats['cache_hits']} ({api_stats['cache_hit_rate']}%)")
    print(f"  Rate limit status: {api_stats['actual_api_calls']}/{queue_manager.MAX_CALLS_PER_HOUR} calls")
    print(f"{'='*60}\n")

    return json_path


if __name__ == "__main__":
    # Parse command line arguments
    if len(sys.argv) < 2:
        print("Usage: python agents/agent_0/main.py <topic1> <topic2> ... <topicN>")
        print("   or: python agents/agent_0/main.py --drill-down <primary_topic>")
        print("   or: python agents/agent_0/main.py --method <method> <topic1> <topic2>")
        print("\nMethods:")
        print("  pytrends   - Standard Google Trends API (default, rate limited)")
        print("  playwright - Browser automation (needs proxies, rate limited)")
        print("  websearch  - Web search trend signals (unlimited, no rate limits)")
        print("\nExamples:")
        print('  python agents/agent_0/main.py "romance novels" "productivity apps"')
        print('  python agents/agent_0/main.py --drill-down "romance novels"')
        print('  python agents/agent_0/main.py --method websearch "romance novels"')
        print('  python agents/agent_0/main.py --method playwright "romance novels"')
        sys.exit(1)

    # Check for method flag
    method = "pytrends"  # default
    if "--method" in sys.argv:
        idx = sys.argv.index("--method")
        if idx + 1 >= len(sys.argv):
            print("[!] Error: --method requires an argument (pytrends or playwright)")
            sys.exit(1)
        method = sys.argv[idx + 1]
        if method not in ["pytrends", "playwright", "websearch"]:
            print(f"[!] Error: Invalid method '{method}'. Use 'pytrends', 'playwright', or 'websearch'")
            sys.exit(1)
        # Remove method args from sys.argv for further processing
        sys.argv.pop(idx)  # Remove --method
        sys.argv.pop(idx)  # Remove method value

    # Check for drill-down mode
    if "--drill-down" in sys.argv:
        idx = sys.argv.index("--drill-down")
        if idx + 1 >= len(sys.argv):
            print("[!] Error: --drill-down requires a topic argument")
            print('Example: python agents/agent_0/main.py --drill-down "romance novels"')
            sys.exit(1)

        primary_topic = sys.argv[idx + 1]

        print(f"\n{'='*60}")
        print(f"DRILL-DOWN MODE: {primary_topic}")
        print(f"{'='*60}")
        print(f"Generating top 10 in-demand subtopics using AI web research...")
        print(f"This follows Grok's methodology: web search + social signals + composite scoring")
        print(f"{'='*60}\n")

        # Generate subtopics using Claude AI
        from agents.agent_0.drill_down import DrillDownGenerator

        trail = BreadcrumbTrail("Agent0_DrillDown")
        drill_down_gen = DrillDownGenerator(trail)

        subtopics = drill_down_gen.generate_subtopics(primary_topic, method="auto")

        if not subtopics:
            print(f"\n[!] Failed to generate subtopics for '{primary_topic}'")
            print(f"[!] Please ensure ANTHROPIC_API_KEY is set in your .env file")
            print(f"[!] Or add patterns for this topic in drill_down.py")
            sys.exit(1)

        print(f"\n{'='*60}")
        print(f"Generated {len(subtopics)} Subtopics:")
        print(f"{'='*60}")
        for i, subtopic in enumerate(subtopics, 1):
            print(f"  {i}. {subtopic}")
        print(f"{'='*60}\n")

        # Now research all subtopics using normal Agent 0 flow
        print(f"[*] Starting research on all {len(subtopics)} subtopics...")
        print(f"[*] This will take approximately {len(subtopics) * 14 / 60:.1f} minutes\n")

        topics = subtopics
    else:
        # Normal mode
        topics = sys.argv[1:]

    # Limit to MAX_TOPICS
    if len(topics) > Config.MAX_TOPICS:
        print(f"[!] Warning: Limiting to {Config.MAX_TOPICS} topics (configured max)")
        topics = topics[:Config.MAX_TOPICS]

    # Run Agent 0
    output_path = main(topics, method=method)

    if output_path:
        print(f"\n[OK] Agent 0 completed successfully!")
        print(f"[OK] Output: {output_path}")
        print(f"[OK] Method used: {method}")
        sys.exit(0)
    else:
        print(f"\n[FAIL] Agent 0 failed - check logs for details")
        sys.exit(1)
