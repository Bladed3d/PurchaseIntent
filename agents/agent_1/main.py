"""
Agent 1: Product Researcher
Finds 5-10 comparable products and discovers hidden audience segments
LED Range: 1500-1599 | Output: outputs/{timestamp}-agent1-output.json
"""
import sys
import os
import argparse
from datetime import datetime

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from lib.breadcrumb_system import BreadcrumbTrail
from agents.agent_1.config import Agent1Config as Config
from agents.agent_1.search import MultiSourceSearch, SubredditDetector
from agents.agent_1.comparables import ComparablesRanker
from agents.agent_1.subreddit_overlap import SubredditOverlapAnalyzer, SegmentInsightsGenerator
from agents.agent_1.checkpoint import CheckpointManager


def main(product_description: str, product_category: str = "general",
         enable_youtube: bool = True, enable_goodreads: bool = False,
         auto_approve: bool = False):
    """Main execution for Agent 1 - Product Researcher"""
    trail = BreadcrumbTrail("Agent1_ProductResearch")

    trail.light(Config.LED_INIT, {"action": "agent_1_started", "product": product_description})

    try:
        Config.validate()
    except ValueError as e:
        trail.fail(Config.LED_ERROR_START + 7, e)
        print(f"\n[FAIL] {e}")
        return None

    print(f"\n{'='*80}\nAGENT 1: PRODUCT RESEARCHER\n{'='*80}")
    print(f"Product: {product_description} | Category: {product_category}")
    print(f"YouTube: {'ON' if enable_youtube else 'OFF'} | Goodreads: {'ON' if enable_goodreads else 'OFF'}\n")

    try:
        # Step 1: Multi-source search
        print("[1/5] Searching multiple sources for comparable products...")
        search = MultiSourceSearch(trail)
        search_results = search.search_all_sources(
            product_description=product_description,
            product_category=product_category,
            enable_youtube=enable_youtube,
            enable_goodreads=enable_goodreads
        )
        print(f"  Amazon: {len(search_results['amazon'])} products")
        print(f"  Reddit: {len(search_results['reddit'])} discussions")
        print(f"  YouTube: {len(search_results['youtube'])} videos")
        print(f"  Goodreads: {len(search_results['goodreads'])} books")
        print()

        # Step 2: Rank comparables
        print("[2/5] Ranking comparable products by relevance...")
        ranker = ComparablesRanker(trail)
        comparables = ranker.rank_comparables(search_results, product_description)
        discussions = ranker.aggregate_discussion_sources(search_results)
        print(f"  Selected: {len(comparables)} top comparables")
        print(f"  Aggregated: {len(discussions)} discussion sources")
        print()

        # Step 3: Subreddit overlap & insights
        print("[3/5] Analyzing subreddit overlaps...")
        base_subreddits = SubredditDetector.detect_subreddits(product_description, product_category)
        overlap_analyzer = SubredditOverlapAnalyzer(trail)
        overlaps = overlap_analyzer.analyze_overlaps(base_subreddits, comparables, discussions)
        print(f"  Found: {len(overlaps)} communities\n")

        print("[4/5] Generating segment insights...")
        segment_insights = SegmentInsightsGenerator.generate_insights(overlaps)
        print(f"  Segments: {segment_insights['total_segments']} | High-opp: {segment_insights['high_opportunity_segments']}\n")

        # Step 5: Checkpoint & save
        print("[5/5] Checkpoint...")
        checkpoint = CheckpointManager(trail)
        report = checkpoint.generate_checkpoint_report(comparables, discussions, overlaps, segment_insights)

        try:
            checkpoint.prompt_user_approval(report, auto_approve=auto_approve)
        except ValueError as e:
            trail.fail(Config.LED_ERROR_START + 8, e)
            print("\n[RETRY] Aborted by user")
            return None

        timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')
        output_path = os.path.join(os.path.dirname(__file__), Config.OUTPUT_DIR, f"{timestamp}-agent1-output.json")
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        checkpoint.save_checkpoint_data(output_path, product_description, product_category,
                                       comparables, discussions, overlaps, segment_insights)

        trail.light(Config.LED_OUTPUT_START + 1, {"action": "agent_1_complete", "output": output_path})

        print(f"\n{'='*80}\nAGENT 1 COMPLETE\n{'='*80}")
        print(f"Output: {output_path}\nReady for Agent 2\n")
        return output_path

    except Exception as e:
        trail.fail(Config.LED_ERROR_START + 9, e)
        print(f"\n[FAIL] Agent 1 error: {str(e)}")
        return None


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Agent 1: Product Researcher")
    parser.add_argument("product_description", help="Product description")
    parser.add_argument("--category", default="general",
                       choices=["book", "software", "saas", "app", "course", "training", "general"])
    parser.add_argument("--no-youtube", action="store_true", help="Disable YouTube (saves quota)")
    parser.add_argument("--enable-goodreads", action="store_true", help="Enable Goodreads (books)")
    parser.add_argument("--auto-approve", action="store_true", help="Auto-approve checkpoint (for testing)")
    args = parser.parse_args()

    main(args.product_description, args.category, not args.no_youtube, args.enable_goodreads, args.auto_approve)
