"""
Agent 2: Demographics Analyst - Main Entry Point

Extracts demographic profiles from product reviews and discussions.
Validates via triangulation across multiple sources.

Usage:
    python agents/agent_2/main.py --input <agent1_output.json>
    python agents/agent_2/main.py --test-data <test_data.json>

LED Range: 2500-2599
Output: agents/agent_2/outputs/<timestamp>-demographics.json
"""

import sys
import os
import json
from datetime import datetime
from pathlib import Path

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from lib.breadcrumb_system import BreadcrumbTrail
from agents.agent_2.config import Agent2Config as Config
from agents.agent_2.scraper import DataScraper
from agents.agent_2.demographics_extractor import DemographicsExtractor
from agents.agent_2.aggregator import DemographicsAggregator
from agents.agent_2.confidence_calculator import ConfidenceCalculator
from agents.agent_2.checkpoint import CheckpointGate
from agents.agent_2.source_tiers import SourceTiers


def main(input_path: str = None, test_data_path: str = None, auto_approve: bool = False):
    """
    Main execution function for Agent 2

    Args:
        input_path: Path to Agent 1 output JSON
        test_data_path: Path to test data JSON (for development)
        auto_approve: Auto-approve checkpoint gate (for testing)

    Returns:
        Path to output JSON file
    """
    # Initialize LED breadcrumb trail
    trail = BreadcrumbTrail("Agent2_DemographicsAnalyst")

    trail.light(Config.LED_INIT, {
        "action": "agent_2_started",
        "input_path": input_path or test_data_path
    })

    print(f"\n{'='*60}")
    print("Agent 2: Demographics Analyst")
    print(f"{'='*60}\n")

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

    # Initialize components
    scraper = DataScraper(trail, Config)
    extractor = DemographicsExtractor(trail)
    aggregator = DemographicsAggregator(trail)
    confidence_calc = ConfidenceCalculator(trail, Config)
    checkpoint = CheckpointGate(trail, Config)

    # Load data
    print(f"[1/6] Loading review/comment data...")
    try:
        if test_data_path:
            all_data = scraper.load_from_test_data(test_data_path)
        elif input_path:
            all_data = scraper.load_from_agent1(input_path)
        else:
            raise ValueError("Must provide either --input or --test-data argument")

    except (FileNotFoundError, ValueError) as e:
        trail.fail(Config.LED_SCRAPING_START, e)
        print(f"\n[FAIL] Data loading error: {e}")
        return None

    # Check minimum data requirement
    if all_data['total_data_points'] < Config.MIN_DATA_POINTS_REQUIRED:
        print(f"\n[!] WARNING: Only {all_data['total_data_points']} data points available")
        print(f"    Minimum recommended: {Config.MIN_DATA_POINTS_REQUIRED}")
        print(f"    This will likely result in low confidence scores\n")

    # Prepare source datasets
    source_datasets = scraper.prepare_source_datasets(all_data)

    # Extract demographics from each source
    print(f"\n[2/6] Extracting demographics from each source...")

    source_demographics = {}
    all_profiles = []

    for source_name, reviews in source_datasets.items():
        if not reviews:
            print(f"  [SKIP] {source_name}: No data available")
            continue

        print(f"  [*] Processing {source_name}: {len(reviews)} reviews/comments")

        try:
            profiles = extractor.extract_from_batch(reviews)
            all_profiles.extend(profiles)

            # Aggregate for this source
            profiles_dict = extractor.profiles_to_dict(profiles)
            source_agg = aggregator.aggregate_profiles(profiles_dict)

            source_demographics[source_name] = {
                "sample_size": len(reviews),
                **source_agg
            }

            print(f"  [OK] {source_name}: {len(profiles)} profiles extracted")

        except (ValueError, KeyError) as e:
            trail.fail(Config.LED_EXTRACTION_START, e)
            print(f"  [FAIL] {source_name} extraction failed: {e}")
            # Continue with other sources

    # Intelligent pipeline: Analyze Tier 1 source coverage
    trail.light(2545, {
        "action": "tier_1_analysis",
        "sources_found": list(source_demographics.keys()),
        "total_sources": len(source_demographics)
    })

    print(f"\n[*] Tier 1 Pipeline Analysis:")
    print(f"    Sources with data: {len(source_demographics)}")
    print(f"    Sources: {', '.join(source_demographics.keys())}")

    # Check if we have NO sources at all (FAIL LOUDLY)
    if len(source_demographics) == 0:
        error = ValueError(
            "NO DATA SOURCES AVAILABLE. No demographic data found across any source.\n"
            "This topic likely has insufficient demand or market presence.\n"
            "Recommendation: Choose a different topic with stronger market signals."
        )
        trail.fail(Config.LED_EXTRACTION_START + 1, error)
        print(f"\n[FAIL] {error}")
        return None

    # Aggregate overall demographics
    print(f"\n[3/6] Aggregating overall demographics...")

    try:
        all_profiles_dict = extractor.profiles_to_dict(all_profiles)
        overall_demographics = aggregator.aggregate_profiles(all_profiles_dict)

        print(f"  [OK] Overall demographics aggregated from {len(all_profiles)} profiles")
        print(f"       Age: {overall_demographics['age_range']}")
        print(f"       Top Occupation: {overall_demographics['top_occupations'][0]['occupation']}")

    except (ValueError, KeyError) as e:
        trail.fail(Config.LED_EXTRACTION_START + 2, e)
        print(f"\n[FAIL] Aggregation error: {e}")
        return None

    # Cluster demographics
    print(f"\n[4/6] Clustering demographics into customer segments...")

    try:
        clusters = aggregator.cluster_profiles(all_profiles_dict, Config.NUM_DEMOGRAPHIC_CLUSTERS)
        clusters_dict = aggregator.clusters_to_dict(clusters)

        print(f"  [OK] Created {len(clusters)} demographic clusters:")
        for cluster in clusters:
            print(f"       - {cluster.cluster_id}: {cluster.size} profiles ({cluster.age_range})")

    except ValueError as e:
        trail.fail(Config.LED_CLUSTERING_START, e)
        print(f"\n[FAIL] Clustering error: {e}")
        return None

    # Calculate confidence
    print(f"\n[5/6] Calculating confidence score...")

    try:
        # TODO: Web search for benchmark data (future enhancement)
        benchmark_data = None

        confidence_result = confidence_calc.calculate_confidence(
            source_demographics,
            overall_demographics,
            all_data['total_data_points'],
            benchmark_data
        )

        print(f"  [OK] Confidence Score: {confidence_result['confidence_percentage']:.1f}%")
        print(f"       Source Agreement: {confidence_result['breakdown']['source_agreement']:.1%}")
        print(f"       Sample Size Score: {confidence_result['breakdown']['sample_size_score']:.1%}")
        print(f"       Benchmark Match: {confidence_result['breakdown']['benchmark_match']:.1%}")

    except ValueError as e:
        trail.fail(Config.LED_VALIDATION_START, e)
        print(f"\n[FAIL] Confidence calculation error: {e}")
        return None

    # Checkpoint gate
    print(f"\n[6/6] Evaluating confidence checkpoint...")

    try:
        low_confidence_reasons = confidence_calc.get_low_confidence_reasons(
            confidence_result,
            source_demographics,
            all_data['total_data_points']
        )

        # Auto-approve if flag is set (for testing)
        if auto_approve and confidence_result['confidence_score'] < Config.CONFIDENCE_THRESHOLD:
            print(f"\n[!] AUTO-APPROVE MODE: Bypassing checkpoint gate")
            print(f"    Confidence: {confidence_result['confidence_percentage']:.1f}% (threshold: {Config.CONFIDENCE_THRESHOLD:.0%})")
            checkpoint_result = {
                "checkpoint_passed": False,
                "user_approval": "auto_approved",
                "confidence_score": confidence_result['confidence_score']
            }
        else:
            checkpoint_result = checkpoint.evaluate_checkpoint(
                confidence_result,
                overall_demographics,
                source_demographics,
                all_data['total_data_points'],
                low_confidence_reasons
            )

    except ValueError as e:
        # User declined to continue
        trail.fail(Config.LED_CHECKPOINT_START, e)
        print(f"\n[ABORTED] {e}")
        return None

    # Generate output
    print(f"\n{'='*60}")
    print("Generating output...")
    print(f"{'='*60}")

    # Create output directory
    os.makedirs(Config.OUTPUT_DIR, exist_ok=True)

    # Generate output filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_filename = f"{timestamp}-demographics.json"
    output_path = os.path.join(Config.OUTPUT_DIR, output_filename)

    # Build output data
    output_data = {
        "agent": "demographics_analyst",
        "status": "complete",
        "timestamp": datetime.now().isoformat(),
        "demographics_overall": overall_demographics,
        "demographic_clusters": clusters_dict,
        "validation": {
            "confidence_score": confidence_result['confidence_score'],
            "confidence_percentage": confidence_result['confidence_percentage'],
            "breakdown": confidence_result['breakdown'],
            "meets_threshold": confidence_result['meets_threshold'],
            "checkpoint_result": checkpoint_result
        },
        "data_sources": source_demographics,
        "metadata": {
            "total_profiles": len(all_profiles),
            "total_data_points": all_data['total_data_points'],
            "num_sources": len(source_demographics),
            "num_clusters": len(clusters),
            "input_file": input_path or test_data_path
        }
    }

    # Save JSON output
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=2)

        trail.light(Config.LED_COMPLETE, {
            "action": "agent_2_complete",
            "output_path": output_path,
            "confidence_score": confidence_result['confidence_score']
        })

        print(f"  [OK] Demographics JSON: {output_path}")

    except Exception as e:
        trail.fail(Config.LED_COMPLETE, e)
        print(f"\n[FAIL] Output generation error: {e}")
        return None

    # Print summary
    summary = trail.get_verification_summary()

    print(f"\n{'='*60}")
    print("Agent 2 Execution Summary")
    print(f"{'='*60}")
    print(f"Status: {'SUCCESS' if checkpoint_result['checkpoint_passed'] or checkpoint_result['user_approval'] == 'approved' else 'FAILED'}")
    print(f"Confidence: {confidence_result['confidence_percentage']:.1f}%")
    print(f"Profiles Extracted: {len(all_profiles)}")
    print(f"Clusters Created: {len(clusters)}")
    print(f"Data Sources: {len(source_demographics)}")
    print(f"Total LEDs: {summary['total_leds']}")
    print(f"Failures: {summary['failures']}")
    print(f"Quality Score: {trail.get_quality_score()}%")
    print(f"Output: {output_path}")
    print(f"{'='*60}\n")

    return output_path


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Agent 2: Demographics Analyst")
    parser.add_argument(
        "--input",
        type=str,
        help="Path to Agent 1 output JSON file"
    )
    parser.add_argument(
        "--test-data",
        type=str,
        help="Path to test data JSON file (for development/testing)"
    )
    parser.add_argument(
        "--auto-approve",
        action="store_true",
        help="Auto-approve checkpoint gate (for testing with low confidence)"
    )

    args = parser.parse_args()

    if not args.input and not args.test_data:
        print("Error: Must provide either --input or --test-data argument")
        print("\nUsage:")
        print("  python agents/agent_2/main.py --input agents/agent_1/outputs/comparables.json")
        print("  python agents/agent_2/main.py --test-data tests/fixtures/agent2_test_data.json")
        sys.exit(1)

    # Run Agent 2
    output_path = main(input_path=args.input, test_data_path=args.test_data, auto_approve=args.auto_approve)

    if output_path:
        print(f"\n[OK] Agent 2 completed successfully!")
        print(f"[OK] Output: {output_path}")
        sys.exit(0)
    else:
        print(f"\n[FAIL] Agent 2 failed - check logs for details")
        sys.exit(1)
