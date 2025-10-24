"""
Example usage of the LED Breadcrumb System for Purchase Intent agents

This demonstrates the patterns agents should follow for instrumentation.
"""

from breadcrumb_system import BreadcrumbTrail, VerificationResult


def example_agent_0_workflow():
    """Example: Agent 0 - Topic Research Agent workflow with LED instrumentation"""

    # Initialize trail for this agent
    trail = BreadcrumbTrail("Agent0_TopicResearch")

    # 1. Start operation
    trail.light(500, {"action": "Agent 0 started", "mode": "topic_research"})

    # 2. Validate input
    topic = "romance novels"
    if not topic:
        trail.fail(501, Exception("No topic provided"))
        return

    trail.light(501, {"action": "Input validated", "topic": topic})

    # 3. Query Google Trends
    try:
        trail.light(502, {"action": "Starting Google Trends query", "keyword": topic})

        # Simulate API call
        trends_data = {"interest_over_time": [65, 70, 72, 68, 71]}

        # Verify we got data
        verification = VerificationResult(
            expect=True,
            actual=len(trends_data.get("interest_over_time", [])) > 0,
            validator=lambda x: x is True
        )

        if not trail.light_with_verification(503, trends_data, verification):
            print("Google Trends returned no data")
            return

    except Exception as e:
        trail.fail(503, e)
        return

    # 4. Query Reddit
    trail.light(510, {"action": "Starting Reddit PRAW query", "subreddit": "books"})

    try:
        reddit_posts = [
            {"title": "Best romance novels of 2024", "score": 342},
            {"title": "Looking for romance book recommendations", "score": 156}
        ]

        trail.light(511, {
            "action": "Reddit query complete",
            "posts_found": len(reddit_posts),
            "total_engagement": sum(p["score"] for p in reddit_posts)
        })

    except Exception as e:
        trail.fail(511, e)
        # Continue with degraded data (graceful degradation)
        reddit_posts = []

    # 5. Query YouTube
    trail.light(520, {"action": "Starting YouTube Data API query"})

    youtube_videos = [
        {"title": "Top 10 Romance Books", "views": 45000},
        {"title": "Romance Novel Recommendations", "views": 23000}
    ]

    trail.light(521, {
        "action": "YouTube query complete",
        "videos_found": len(youtube_videos),
        "total_views": sum(v["views"] for v in youtube_videos)
    })

    # 6. Checkpoint: Verify we have enough data
    def has_sufficient_data():
        return (
            len(trends_data.get("interest_over_time", [])) > 0 and
            (len(reddit_posts) > 0 or len(youtube_videos) > 0)
        )

    if not trail.checkpoint(
        530,
        "Sufficient data collected",
        has_sufficient_data,
        {
            "trends": bool(trends_data),
            "reddit": len(reddit_posts),
            "youtube": len(youtube_videos)
        }
    ):
        print("Insufficient data - cannot proceed")
        return

    # 7. Score topics
    trail.light(540, {"action": "Calculating topic scores"})

    scored_topics = [
        {"topic": "romance novels", "score": 87.5, "sources": 3},
        {"topic": "BookTok romance", "score": 92.3, "sources": 3}
    ]

    trail.light(541, {
        "action": "Scoring complete",
        "topics_scored": len(scored_topics),
        "top_topic": scored_topics[0]["topic"]
    })

    # 8. Generate HTML dashboard
    trail.light(550, {"action": "Generating HTML dashboard"})

    html_path = "outputs/agent0-dashboard.html"
    # Simulate HTML generation
    trail.light(551, {
        "action": "Dashboard generated",
        "path": html_path,
        "topics_displayed": len(scored_topics)
    })

    # 9. Write output JSON
    trail.light(560, {"action": "Writing topic-selection.json"})

    output = {
        "selected_topic": scored_topics[0]["topic"],
        "confidence": scored_topics[0]["score"],
        "sources": ["Google Trends", "Reddit", "YouTube"]
    }

    trail.light(561, {
        "action": "Agent 0 complete",
        "output_file": "outputs/topic-selection.json",
        "selected": output["selected_topic"]
    })

    # Print summary
    summary = trail.get_verification_summary()
    print(f"\n{'='*60}")
    print(f"Agent 0 Verification Summary:")
    print(f"  Total LEDs: {summary['total_leds']}")
    print(f"  Failures: {summary['failures']}")
    print(f"  Quality Score: {BreadcrumbTrail.get_quality_score()}%")
    print(f"  Verification Passed: {summary['verification_passed']}")
    print(f"{'='*60}\n")


def example_check_led_range():
    """Example: How Claude can autonomously check LED ranges for debugging"""

    print("\n=== Autonomous Debugging Example ===\n")

    # Check if Agent 0 completed successfully
    agent0_check = BreadcrumbTrail.check_range(500, 599)

    print(f"Agent 0 Range Check (500-599):")
    print(f"  Passed: {agent0_check['passed']}")
    print(f"  Missing LEDs: {agent0_check['missing']}")
    print(f"  Failed LEDs: {agent0_check['failed']}")

    # Get all failures
    failures = BreadcrumbTrail.get_failures()
    if failures:
        print(f"\nFailures detected: {len(failures)}")
        for failure in failures:
            print(f"  [FAIL] LED {failure.id} ({failure.component}): {failure.error}")
    else:
        print("\n[OK] No failures detected")

    # Get specific range (e.g., just Google Trends operations)
    trends_leds = BreadcrumbTrail.get_range(502, 503)
    print(f"\nGoogle Trends Operations (502-503): {len(trends_leds)} LEDs")
    for led in trends_leds:
        status = "[OK]" if led.success else "[FAIL]"
        print(f"  {status} LED {led.id}: {led.name}")


if __name__ == "__main__":
    # Run the example workflow
    print("Running Agent 0 example workflow...\n")
    example_agent_0_workflow()

    # Demonstrate autonomous debugging
    example_check_led_range()

    print("\n[LOG] Check logs/breadcrumbs.jsonl for JSON Lines log output")
    print("      Claude can grep this file to debug issues autonomously\n")
