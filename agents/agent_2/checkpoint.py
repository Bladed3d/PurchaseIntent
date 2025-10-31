"""
Checkpoint Gate - Enforce confidence threshold before continuing

LED Range: 2575-2579
"""

from typing import Dict, Any, List


class CheckpointGate:
    """Checkpoint gate for confidence validation"""

    def __init__(self, trail, config):
        """
        Initialize checkpoint gate

        Args:
            trail: BreadcrumbTrail for LED tracking
            config: Agent2Config for thresholds
        """
        self.trail = trail
        self.config = config

    def evaluate_checkpoint(
        self,
        confidence_result: Dict[str, Any],
        demographics: Dict[str, Any],
        source_demographics: Dict[str, Dict[str, Any]],
        sample_size: int,
        low_confidence_reasons: List[str]
    ) -> Dict[str, Any]:
        """
        Evaluate checkpoint - pass or require user approval

        Args:
            confidence_result: Result from ConfidenceCalculator
            demographics: Overall demographics
            source_demographics: Demographics by source
            sample_size: Total data points
            low_confidence_reasons: List of reasons for low confidence

        Returns:
            Dict with checkpoint result and user decision

        Raises:
            ValueError: If user declines to continue with low confidence
        """
        confidence_score = confidence_result['confidence_score']
        threshold = self.config.CONFIDENCE_THRESHOLD

        self.trail.light(2575, {
            "action": "evaluating_checkpoint",
            "confidence_score": confidence_score,
            "threshold": threshold,
            "meets_threshold": confidence_score >= threshold
        })

        if confidence_score >= threshold:
            # Checkpoint PASSED
            self.trail.light(2576, {
                "action": "checkpoint_passed",
                "confidence_score": confidence_score
            })

            print(f"\n{'='*60}")
            print("CHECKPOINT PASSED")
            print(f"{'='*60}")
            print(f"Confidence Score: {confidence_score:.1%} (threshold: {threshold:.0%})")
            print(f"Sample Size: {sample_size} data points")
            print(f"Sources: {len(source_demographics)}")
            print(f"{'='*60}\n")

            return {
                "checkpoint_passed": True,
                "user_approval": "automatic",
                "confidence_score": confidence_score
            }

        else:
            # Checkpoint FAILED - require user approval
            self.trail.light(2577, {
                "action": "checkpoint_failed",
                "confidence_score": confidence_score,
                "threshold": threshold
            })

            print(f"\n{'='*60}")
            print("CHECKPOINT FAILED")
            print(f"{'='*60}")
            print(f"Confidence Score: {confidence_score:.1%} (threshold: {threshold:.0%})")
            print(f"\nReasons for low confidence:")

            for reason in low_confidence_reasons:
                print(f"  - {reason}")

            print(f"\nDemographics Summary:")
            print(f"  Age Range: {demographics.get('age_range', 'unknown')}")
            print(f"  Top Occupation: {demographics['top_occupations'][0]['occupation'] if demographics.get('top_occupations') else 'unknown'}")
            print(f"  Sample Size: {sample_size}")
            print(f"  Sources: {', '.join(source_demographics.keys())}")

            print(f"\n{'='*60}")
            print("OPTIONS:")
            print("  'yes'     - Continue anyway (accept risk of low confidence)")
            print("  'no'      - Abort and collect more data")
            print("  'details' - Show detailed demographics breakdown")
            print(f"{'='*60}\n")

            while True:
                user_input = input("Continue with low-confidence demographics? (yes/no/details): ").strip().lower()

                if user_input == 'yes':
                    # User approved - continue
                    self.trail.light(2578, {
                        "action": "checkpoint_user_approved",
                        "confidence_score": confidence_score
                    })

                    print(f"\n[OK] User approved - continuing with {confidence_score:.1%} confidence\n")

                    return {
                        "checkpoint_passed": False,
                        "user_approval": "approved",
                        "confidence_score": confidence_score
                    }

                elif user_input == 'no':
                    # User declined - abort
                    self.trail.fail(2579, ValueError("User declined to continue with low-confidence demographics"))

                    print(f"\n[ABORT] User declined to continue")
                    print(f"[!] Recommendation: Collect more data from additional sources")
                    print(f"[!] Try these options:")
                    print(f"    - Scrape more reviews/comments (increase sample size)")
                    print(f"    - Add YouTube comments if not already included")
                    print(f"    - Find benchmark data to validate against\n")

                    raise ValueError(
                        f"User declined to continue with low-confidence demographics "
                        f"(confidence: {confidence_score:.1%}, threshold: {threshold:.0%}). "
                        f"Reasons: {'; '.join(low_confidence_reasons)}"
                    )

                elif user_input == 'details':
                    # Show detailed breakdown
                    self._print_detailed_demographics(demographics, source_demographics, confidence_result)
                    print(f"\n{'='*60}\n")

                else:
                    print(f"[!] Invalid input: '{user_input}'. Please enter 'yes', 'no', or 'details'")

    def _print_detailed_demographics(
        self,
        demographics: Dict[str, Any],
        source_demographics: Dict[str, Dict[str, Any]],
        confidence_result: Dict[str, Any]
    ):
        """Print detailed demographics breakdown"""
        print(f"\n{'='*60}")
        print("DETAILED DEMOGRAPHICS BREAKDOWN")
        print(f"{'='*60}")

        # Overall demographics
        print(f"\nOVERALL DEMOGRAPHICS:")
        print(f"  Age Distribution:")
        for age, pct in demographics.get('age_distribution', {}).items():
            print(f"    {age}: {pct}%")

        print(f"\n  Gender Distribution:")
        for gender, pct in demographics.get('gender_distribution', {}).items():
            print(f"    {gender}: {pct}%")

        print(f"\n  Top Occupations:")
        for occ in demographics.get('top_occupations', [])[:5]:
            print(f"    {occ['occupation']}: {occ['frequency']}% ({occ['count']} mentions)")

        print(f"\n  Top Pain Points:")
        for pain in demographics.get('top_pain_points', [])[:5]:
            print(f"    {pain['pain']}: {pain['mentions']} mentions ({pain['percentage']}%)")

        # Source-by-source breakdown
        print(f"\n{'='*60}")
        print("SOURCE-BY-SOURCE COMPARISON:")
        print(f"{'='*60}")

        for source, source_demo in source_demographics.items():
            print(f"\n{source.upper()}:")
            print(f"  Sample Size: {source_demo.get('sample_size', 'unknown')}")

            age_dist = source_demo.get('age_distribution', {})
            if age_dist:
                dominant_age = max(age_dist.items(), key=lambda x: x[1])[0]
                print(f"  Dominant Age: {dominant_age} ({age_dist[dominant_age]}%)")

            gender_dist = source_demo.get('gender_distribution', {})
            if gender_dist:
                print(f"  Gender: {gender_dist.get('male', 0):.0f}% male, {gender_dist.get('female', 0):.0f}% female")

            top_occs = source_demo.get('top_occupations', [])
            if top_occs:
                print(f"  Top Occupation: {top_occs[0]['occupation']} ({top_occs[0]['frequency']}%)")

        # Confidence breakdown
        print(f"\n{'='*60}")
        print("CONFIDENCE SCORE BREAKDOWN:")
        print(f"{'='*60}")

        breakdown = confidence_result['breakdown']
        weights = confidence_result['weights']

        print(f"\n  Source Agreement: {breakdown['source_agreement']:.1%} (weight: {weights['source_agreement']:.0%})")
        print(f"  Sample Size Score: {breakdown['sample_size_score']:.1%} (weight: {weights['sample_size']:.0%})")
        print(f"  Benchmark Match: {breakdown['benchmark_match']:.1%} (weight: {weights['benchmark_match']:.0%})")
        print(f"\n  TOTAL CONFIDENCE: {confidence_result['confidence_score']:.1%}")
