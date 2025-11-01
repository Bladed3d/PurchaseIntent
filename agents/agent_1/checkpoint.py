"""
Agent 1 Checkpoint System
User approval gate before proceeding to Agent 2

CRITICAL RULES:
- FAIL LOUDLY: User must explicitly approve
- Clear presentation of findings
"""

import json
from typing import Dict, Any, List
from datetime import datetime

from lib.breadcrumb_system import BreadcrumbTrail
from agents.agent_1.config import Agent1Config as Config


class CheckpointManager:
    """Manages user approval checkpoint between Agent 1 and Agent 2"""

    def __init__(self, trail: BreadcrumbTrail):
        self.trail = trail

    def generate_checkpoint_report(
        self,
        comparables: List[Dict[str, Any]],
        discussions: List[Dict[str, Any]],
        overlaps: List[Dict[str, Any]],
        segment_insights: Dict[str, Any]
    ) -> str:
        """
        Generate human-readable checkpoint report for user approval

        Args:
            comparables: Top comparable products
            discussions: Discussion sources
            overlaps: Subreddit overlap analysis
            segment_insights: Segment insights summary

        Returns:
            Formatted markdown report string
        """
        self.trail.light(Config.LED_CHECKPOINT_START, {
            "action": "checkpoint_report_generated",
            "comparables_count": len(comparables),
            "discussions_count": len(discussions),
            "overlaps_count": len(overlaps)
        })

        report_lines = [
            "=" * 80,
            "AGENT 1: PRODUCT RESEARCH COMPLETE",
            "=" * 80,
            "",
            f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            ""
        ]

        # Section 1: Comparables Found
        report_lines.extend([
            "## COMPARABLE PRODUCTS",
            f"Found: {len(comparables)} products",
            ""
        ])

        for i, product in enumerate(comparables[:7], 1):
            platform_emoji = {
                'amazon': '',
                'goodreads': '',
                'youtube': ''
            }.get(product['platform'], '')

            report_lines.append(f"{i}. {platform_emoji} {product['title']}")
            report_lines.append(f"   Platform: {product['platform'].title()}")

            if product['platform'] == 'amazon':
                report_lines.append(
                    f"   Price: {product['price']} | "
                    f"Reviews: {product['review_count']:,} | "
                    f"Rating: {product['rating']:.1f}/5.0"
                )
            elif product['platform'] == 'goodreads':
                report_lines.append(
                    f"   Author: {product.get('author', 'Unknown')} | "
                    f"Reviews: {product['review_count']:,} | "
                    f"Rating: {product['rating']:.1f}/5.0"
                )
            elif product['platform'] == 'youtube':
                report_lines.append(
                    f"   Views: {product['views']:,} | "
                    f"Comments: {product['comments']:,}"
                )

            report_lines.append(f"   Relevance Score: {product['relevance_score']:.2f}")
            report_lines.append("")

        if len(comparables) > 7:
            report_lines.append(f"   ... and {len(comparables) - 7} more")
            report_lines.append("")

        # Section 2: Discussion Sources
        total_comments = sum([d['comments'] for d in discussions])
        report_lines.extend([
            "## DISCUSSION SOURCES",
            f"Found: {len(discussions)} discussions with {total_comments:,} total comments",
            ""
        ])

        reddit_discussions = [d for d in discussions if d['platform'] == 'reddit']
        youtube_discussions = [d for d in discussions if d['platform'] == 'youtube']

        if reddit_discussions:
            report_lines.append(f"Reddit: {len(reddit_discussions)} threads ({sum([d['comments'] for d in reddit_discussions]):,} comments)")
        if youtube_discussions:
            report_lines.append(f"YouTube: {len(youtube_discussions)} videos ({sum([d['comments'] for d in youtube_discussions]):,} comments)")

        report_lines.append("")

        # Section 3: Hidden Segments
        report_lines.extend([
            "## HIDDEN AUDIENCE SEGMENTS (Subreddit Overlap)",
            ""
        ])

        if overlaps:
            high_opp = [o for o in overlaps if o['opportunity_level'] == 'HIGH']
            medium_opp = [o for o in overlaps if o['opportunity_level'] == 'MEDIUM']

            if high_opp:
                report_lines.append(f" HIGH OPPORTUNITY SEGMENTS ({len(high_opp)} found):")
                for overlap in high_opp:
                    report_lines.append(
                        f"   - {overlap['subreddit']} ({overlap['multiplier']:.1f}x overlap) - "
                        f"{overlap['interpretation']}"
                    )
                report_lines.append("")

            if medium_opp:
                report_lines.append(f" MEDIUM OPPORTUNITY SEGMENTS ({len(medium_opp)} found):")
                for overlap in medium_opp[:5]:
                    report_lines.append(
                        f"   - {overlap['subreddit']} ({overlap['multiplier']:.1f}x overlap) - "
                        f"{overlap['interpretation']}"
                    )
                report_lines.append("")

            # Segment insights
            if segment_insights:
                report_lines.append("INSIGHTS:")
                for rec in segment_insights.get('recommendations', []):
                    report_lines.append(f"   - {rec}")
                report_lines.append("")
        else:
            report_lines.append("(No subreddit overlap analysis performed)")
            report_lines.append("")

        # Section 4: Data Quality Check
        report_lines.extend([
            "## DATA QUALITY CHECK",
            ""
        ])

        total_review_count = sum([
            p.get('review_count', p.get('comments', 0))
            for p in comparables
        ])
        total_data_points = total_review_count + total_comments

        report_lines.append(f" Total reviews/comments available: {total_data_points:,}")
        report_lines.append(f" Minimum required: {Config.MIN_TOTAL_COMMENTS:,}")

        if total_data_points >= Config.MIN_TOTAL_COMMENTS:
            report_lines.append(" Status: PASS - Sufficient data for Agent 2 analysis")
        else:
            report_lines.append(f" Status: WARNING - Below minimum threshold (need {Config.MIN_TOTAL_COMMENTS - total_data_points:,} more)")

        report_lines.append("")

        # Section 5: Next Steps
        report_lines.extend([
            "## NEXT STEPS",
            "",
            "Agent 2 will analyze customer demographics from these sources.",
            "Agent 2 will extract age, location, occupation, pain points, and psychographics.",
            "",
            "=" * 80,
            "USER CHECKPOINT: Do these comparables look correct?",
            "=" * 80,
            "",
            "Options:",
            "  [A] Approve - Proceed to Agent 2",
            "  [M] Modify - Add or remove comparables",
            "  [R] Retry - Run Agent 1 again with different search",
            ""
        ])

        return "\n".join(report_lines)

    def prompt_user_approval(self, report: str, auto_approve: bool = False) -> str:
        """
        Display report and prompt user for approval

        Args:
            report: Checkpoint report to display
            auto_approve: If True, automatically approve without prompting

        Returns:
            User's choice: 'approve', 'modify', or 'retry'

        Raises:
            ValueError: If user rejects and wants to retry
        """
        print(report)

        if auto_approve:
            print("\n[AUTO-APPROVE] Automatically approving checkpoint...")
            self.trail.light(Config.LED_CHECKPOINT_START + 1, {
                "action": "auto_approved_checkpoint"
            })
            return 'approve'

        while True:
            choice = input("Your choice [A/M/R]: ").strip().upper()

            if choice == 'A':
                self.trail.light(Config.LED_CHECKPOINT_START + 1, {
                    "action": "user_approved_checkpoint"
                })
                return 'approve'

            elif choice == 'M':
                print("\n[!] Manual modification not implemented in this version.")
                print("    Please use 'R' to retry with different search parameters.")
                continue

            elif choice == 'R':
                self.trail.light(Config.LED_CHECKPOINT_START + 2, {
                    "action": "user_rejected_checkpoint"
                })
                raise ValueError("User requested retry - Agent 1 aborted")

            else:
                print(f"Invalid choice: '{choice}'. Please enter A, M, or R.")

    def save_checkpoint_data(
        self,
        output_path: str,
        product_description: str,
        product_category: str,
        comparables: List[Dict[str, Any]],
        discussions: List[Dict[str, Any]],
        overlaps: List[Dict[str, Any]],
        segment_insights: Dict[str, Any]
    ) -> None:
        """
        Save checkpoint data to JSON file for Agent 2 handoff

        Args:
            output_path: Path to save JSON file
            product_description: User's product description
            product_category: Product category
            comparables: Top comparable products
            discussions: Discussion sources
            overlaps: Subreddit overlap data
            segment_insights: Segment insights summary
        """
        checkpoint_data = {
            "agent": "product_researcher",
            "version": "1.0",
            "status": "complete",
            "timestamp": datetime.now().isoformat(),
            "product_input": {
                "description": product_description,
                "category": product_category
            },
            "comparables": comparables,
            "discussion_urls": discussions,
            "subreddit_overlaps": overlaps,
            "segment_insights": segment_insights,
            "data_sources_collected": {
                "amazon_products": len([p for p in comparables if p['platform'] == 'amazon']),
                "goodreads_books": len([p for p in comparables if p['platform'] == 'goodreads']),
                "youtube_videos": len([p for p in comparables if p['platform'] == 'youtube']),
                "reddit_discussions": len([d for d in discussions if d['platform'] == 'reddit']),
                "youtube_discussions": len([d for d in discussions if d['platform'] == 'youtube']),
                "total_reviews": sum([p.get('review_count', 0) for p in comparables]),
                "total_comments": sum([d['comments'] for d in discussions])
            },
            "confidence": self._calculate_confidence(comparables, discussions),
            "user_checkpoint": "approved"
        }

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(checkpoint_data, f, indent=2, ensure_ascii=False)

        self.trail.light(Config.LED_OUTPUT_START, {
            "action": "checkpoint_data_saved",
            "file": output_path
        })

    def _calculate_confidence(
        self,
        comparables: List[Dict[str, Any]],
        discussions: List[Dict[str, Any]]
    ) -> float:
        """
        Calculate confidence score based on data quality

        Factors:
        - Number of comparables (5+ = high)
        - Total reviews/comments (300+ = high)
        - Average relevance score (0.7+ = high)
        """
        num_comparables = len(comparables)
        total_comments = sum([d['comments'] for d in discussions])
        total_reviews = sum([p.get('review_count', 0) for p in comparables])
        avg_relevance = sum([p['relevance_score'] for p in comparables]) / len(comparables)

        # Scoring
        score = 0.0

        # Factor 1: Number of comparables (0.0 - 0.3)
        if num_comparables >= 5:
            score += 0.3
        else:
            score += 0.3 * (num_comparables / 5)

        # Factor 2: Data volume (0.0 - 0.4)
        total_data = total_comments + total_reviews
        if total_data >= 500:
            score += 0.4
        else:
            score += 0.4 * (total_data / 500)

        # Factor 3: Relevance (0.0 - 0.3)
        score += 0.3 * avg_relevance

        return round(min(1.0, score), 2)
