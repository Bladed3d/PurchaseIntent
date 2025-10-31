"""
Agent 0: Topic Research Agent - Main Entry Point

Discovers and validates demand for product topics by analyzing:
- Google Trends (search volume patterns and trend direction)
- Reddit (community discussions, pain points, and purchase intent signals)

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
from agents.agent_0.drill_down_loader import DrillDownTrail
from agents.agent_0.purchase_intent_analyzer import PurchaseIntentAnalyzer


def main(topics: List[str], method: str = "pytrends", parent_topic: str = None, use_split_view: bool = False):
    """
    Main execution function for Agent 0

    Args:
        topics: List of topic strings to research
        method: Data collection method ("pytrends", "playwright", or "websearch")
        parent_topic: Optional parent topic for drill-down mode (None for root level)
        use_split_view: Use split-view dashboard with tree navigation

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

    # OBSOLETE: Rate limit check commented out since we now use AI Agent research
    # AI agents have no rate limits, and this check was blocking execution unnecessarily
    # Uncomment if we ever switch back to Google Trends API
    #
    # # Check batch safety
    # batch_check = queue_manager.can_process_batch(topics)
    # if not batch_check['safe']:
    #     print(f"\n[!] WARNING: {batch_check['reason']}")
    #     print("Recommendations:")
    #     for rec in batch_check['recommendations']:
    #         print(f"  - {rec}")
    #
    #     if batch_check['wait_seconds'] is not None and batch_check['wait_seconds'] > 0:
    #         print(f"\n[*] Waiting {round(batch_check['wait_seconds'], 1)} seconds before proceeding...")
    #         time.sleep(batch_check['wait_seconds'])
    #     else:
    #         proceed = input("\nProceed anyway? (y/n): ")
    #         if proceed.lower() != 'y':
    #             print("Aborted by user.")
    #             return None

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
    purchase_intent_analyzer = PurchaseIntentAnalyzer(trail)
    scorer = TopicScorer(trail)
    dashboard_gen = DashboardGenerator(trail)

    # Initialize YouTube client if enabled
    youtube_client = None
    if Config.ENABLE_YOUTUBE:
        try:
            youtube_client = YouTubeClient(trail)
            trail.light(Config.LED_INIT + 2, {
                "action": "youtube_client_initialized"
            })
        except Exception as e:
            trail.fail(Config.LED_INIT + 2, e)
            print(f"\n[!] WARNING: YouTube client initialization failed: {e}")
            print("    Continuing with Reddit + Google Trends only\n")
            Config.ENABLE_YOUTUBE = False

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

        # Get trend data (skip if DRILLDOWN_MODE)
        step = 1
        total_steps = 2 + (1 if Config.ENABLE_YOUTUBE else 0) + (0 if Config.DRILLDOWN_MODE else 1)

        trends_data = None
        if not Config.DRILLDOWN_MODE:
            if topic in agent_results:
                print(f"  [{step}/{total_steps}] Using AI agent research data (demand: {agent_results[topic]['demand_score']}, confidence: {agent_results[topic]['confidence']}%)...")
                # Convert agent results to trends format
                trends_data = {
                    "average_interest": agent_results[topic]['demand_score'],
                    "peak_interest": agent_results[topic]['demand_score'],
                    "trend_direction": "stable",
                    "data_points": agent_results[topic]['signals']['mention_count'],
                    "source": "agent"
                }
            else:
                print(f"  [{step}/{total_steps}] Using batched Google Trends data...")
                trends_data = trends_batch_results.get(topic, {
                    "average_interest": 0,
                    "peak_interest": 0,
                    "trend_direction": "no_data",
                    "data_points": 0,
                    "source": "google_trends"
                })
            step += 1
        else:
            print(f"  [DRILL-DOWN MODE] Skipping Google Trends (saves quota)")

        # Query Reddit (with purchase intent data)
        print(f"  [{step}/{total_steps}] Querying Reddit...")
        reddit_data = reddit_client.search_topic(topic, fetch_purchase_intent=True)
        step += 1

        # Query YouTube if enabled
        youtube_data = None
        if Config.ENABLE_YOUTUBE and youtube_client:
            print(f"  [{step}/{total_steps}] Querying YouTube...")
            youtube_data = youtube_client.search_videos(topic, fetch_purchase_intent=False)
            step += 1

        # Analyze purchase intent from Reddit posts
        print(f"  [{step}/{total_steps}] Analyzing purchase intent...")
        purchase_intent_data = {}
        if reddit_data.get('posts'):
            purchase_intent_data = purchase_intent_analyzer.analyze_purchase_intent(
                topic,
                reddit_data['posts']
            )

            # Log purchase intent findings
            if purchase_intent_data['purchase_signals']:
                print(f"  [OK] Purchase Intent: {purchase_intent_data['purchase_intent_score']:.1f}/100")
                print(f"  [OK] Willingness to Pay: {purchase_intent_data['willingness_to_pay_score']:.1f}/100")
                for signal in purchase_intent_data['purchase_signals'][:3]:  # Show top 3
                    # Remove emoji for Windows console compatibility
                    safe_signal = signal.encode('ascii', 'ignore').decode('ascii')
                    print(f"       {safe_signal}")

        # Calculate scores
        print("  [*] Calculating composite score...")
        scores = scorer.calculate_composite_score(
            trends_data,
            reddit_data,
            youtube_data  # Pass YouTube data (None if not enabled)
        )

        # Store results (include description if available from agent results)
        topic_entry = {
            "topic": topic,
            "scores": scores,
            "trends_data": trends_data,
            "reddit_data": reddit_data,
            "youtube_data": youtube_data,  # Include YouTube data
            "purchase_intent": purchase_intent_data  # NEW: purchase intent analysis
        }

        # Add description from agent results if available
        if topic in agent_results and 'description' in agent_results[topic]:
            topic_entry['description'] = agent_results[topic]['description']

        topic_data.append(topic_entry)

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

    # Initialize drill-down trail
    drill_trail = DrillDownTrail(trail)

    # Add this research session to trail
    drill_trail.add_research_session(parent_topic, ranked_topics, Config.OUTPUT_JSON)

    # Get tree data for dashboard
    tree_data = drill_trail.get_tree_for_dashboard()

    # Generate appropriate dashboard based on mode
    if use_split_view or tree_data.get("root_nodes"):
        # Use split-view if explicitly requested OR if we have drill-down history
        trail.light(Config.LED_DRILL_DOWN_START + 13, {
            "action": "generating_split_view_dashboard"
        })
        html_path = dashboard_gen.generate_split_view_html(ranked_topics, tree_data, Config.OUTPUT_HTML, queue_manager=queue_manager)
        print(f"  [OK] Split-View Dashboard: {html_path}")
    else:
        # Use standard dashboard for first-time research
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
        print("\nMode Flags:")
        print("  --drill-down-mode  - Reddit-only (fast exploration, 60% confidence, saves quotas)")
        print("  --enable-youtube   - Enable YouTube API (final validation, 100% confidence, uses quota)")
        print("\nExamples:")
        print('  # Drill-down exploration (Reddit-only, unlimited)')
        print('  python agents/agent_0/main.py --drill-down-mode "romance novels"')
        print('')
        print('  # Final validation (all sources including YouTube)')
        print('  python agents/agent_0/main.py --enable-youtube "walking meditation for anxiety"')
        print('')
        print('  # Regular mode (Reddit + Google Trends)')
        print('  python agents/agent_0/main.py "romance novels" "productivity apps"')
        print('')
        print('  # Drill-down with subtopics')
        print('  python agents/agent_0/main.py --drill-down "romance novels"')
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

    # Check for drill-down mode flag (Reddit-only, fast exploration)
    if "--drill-down-mode" in sys.argv:
        Config.DRILLDOWN_MODE = True
        sys.argv.remove("--drill-down-mode")
        print("[*] DRILL-DOWN MODE: Using Reddit-only for fast exploration")
        print("    - Google Trends: DISABLED (saves quota)")
        print("    - YouTube: DISABLED (saves quota)")
        print("    - Confidence: 60% (acceptable for exploration)")
        print("    - Use regular mode (without flag) for final validation\n")

    # Check for YouTube enable flag (for final validation)
    if "--enable-youtube" in sys.argv:
        Config.ENABLE_YOUTUBE = True
        sys.argv.remove("--enable-youtube")
        print("[*] YOUTUBE ENABLED: Using full 3-source validation")
        print("    - YouTube API: ENABLED (uses quota: ~500-1,000 units per topic)")
        print("    - Free tier: 10,000 units/day (can handle 10-20 topics)")
        print("    - Confidence: 100% (all sources)")
        print("    - Recommended: Use for final 1-3 topic validation only\n")

    # Validate YouTube configuration if enabled
    if Config.ENABLE_YOUTUBE:
        if not Config.YOUTUBE_API_KEY:
            print("[!] ERROR: --enable-youtube requires YOUTUBE_API_KEY in .env file")
            print("    Add: YOUTUBE_API_KEY=your_key_here")
            print("    Get key from: https://console.cloud.google.com/")
            sys.exit(1)

    # Check for drill-down mode
    parent_topic = None
    use_split_view = False

    if "--drill-down" in sys.argv:
        idx = sys.argv.index("--drill-down")
        if idx + 1 >= len(sys.argv):
            print("[!] Error: --drill-down requires a topic argument")
            print('Example: python agents/agent_0/main.py --drill-down "romance novels"')
            sys.exit(1)

        parent_topic = sys.argv[idx + 1]
        use_split_view = True  # Always use split-view for drill-down

        # Load existing trail to show breadcrumb path
        temp_trail = BreadcrumbTrail("Agent0_DrillDown_Check")
        drill_trail_checker = DrillDownTrail(temp_trail)

        breadcrumb_path = drill_trail_checker.get_breadcrumb_path(parent_topic)

        print(f"\n{'='*60}")
        print(f"DRILL-DOWN MODE")
        print(f"{'='*60}")

        if breadcrumb_path:
            print(f"[*] Current Path: {' -> '.join(breadcrumb_path)}")
            print(f"[*] Drilling into: {parent_topic}")
        else:
            print(f"[!] Parent topic '{parent_topic}' not found in research history")
            print(f"[*] Will treat as new root-level research")
            parent_topic = None

        print(f"{'='*60}\n")

        print(f"[*] Step 1: Generate 10 Subtopics")
        print(f"[*] Ask Claude (in your chat session) to generate subtopics:\n")

        # Generate prompt for user to give to Claude
        prompt = f'''Generate 10 specific, in-demand subtopics for "{parent_topic or sys.argv[idx + 1]}" suitable for ebooks.

Use web research to find trending angles for 2025. Focus on specific, actionable niches that follow Brian Moran's "Rule of One" - avoid broad terms.

Research each subtopic and save results to cache/agent_results/ with these filenames:
- {{parent_topic_snake_case}}_{{subtopic}}.json

Return when all 10 are researched and cached.

Examples of good subtopics:
- "billionaire romance novels"
- "guided meditation for sleep"
- "meal prep for busy professionals"

IMPORTANT: Make each subtopic specific enough to be searchable and distinct from others.'''

        print(f"+{'-'*58}+")
        for line in prompt.split('\n'):
            print(f"| {line:<56} |")
        print(f"+{'-'*58}+\n")

        print(f"[*] After Claude completes research, provide the subtopic names below")
        print(f"[*] (one per line, press Enter twice when done):\n")

        # Get subtopics from user
        topics = []
        print(f"Enter subtopics (press Enter twice to finish):")
        while True:
            line = input(f"  {len(topics)+1}. ").strip()
            if not line:
                if topics:
                    break
                else:
                    continue
            topics.append(line)

        if not topics:
            print(f"\n[!] No subtopics provided. Exiting.")
            sys.exit(1)

        print(f"\n[OK] Received {len(topics)} subtopics")
        print(f"[*] Starting research verification...\n")

    else:
        # Normal mode - check for --parent flag
        parent_topic = None

        if "--parent" in sys.argv:
            idx = sys.argv.index("--parent")
            if idx + 1 >= len(sys.argv):
                print("[!] Error: --parent requires a topic name")
                print('Example: python agents/agent_0/main.py --parent "meditation" "body scan" "chakra"')
                sys.exit(1)

            parent_topic = sys.argv[idx + 1]
            use_split_view = True  # Use split-view when specifying parent

            # Remove --parent and its value from argv
            sys.argv.pop(idx)  # Remove --parent
            sys.argv.pop(idx)  # Remove parent value

            print(f"\n{'='*60}")
            print(f"Adding subtopics under parent: {parent_topic}")
            print(f"{'='*60}\n")

        topics = sys.argv[1:]

    # Limit to MAX_TOPICS
    if len(topics) > Config.MAX_TOPICS:
        print(f"[!] Warning: Limiting to {Config.MAX_TOPICS} topics (configured max)")
        topics = topics[:Config.MAX_TOPICS]

    # Run Agent 0
    output_path = main(topics, method=method, parent_topic=parent_topic, use_split_view=use_split_view)

    if output_path:
        print(f"\n[OK] Agent 0 completed successfully!")
        print(f"[OK] Output: {output_path}")
        print(f"[OK] Method used: {method}")
        if use_split_view:
            print(f"[OK] Split-view dashboard generated with drill-down tree")
        sys.exit(0)
    else:
        print(f"\n[FAIL] Agent 0 failed - check logs for details")
        sys.exit(1)
