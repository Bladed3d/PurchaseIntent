"""
Confidence Calculator - Calculate confidence scores with triangulation

Formula: Confidence = (Source Agreement × 40%) + (Sample Size × 30%) + (Benchmark Match × 30%)

LED Range: 2570-2579
"""

from typing import Dict, Any, List
import statistics


class ConfidenceCalculator:
    """Calculate confidence scores for demographic data"""

    def __init__(self, trail, config):
        """
        Initialize confidence calculator

        Args:
            trail: BreadcrumbTrail for LED tracking
            config: Agent2Config for weights and thresholds
        """
        self.trail = trail
        self.config = config

    def calculate_confidence(
        self,
        source_demographics: Dict[str, Dict[str, Any]],
        overall_demographics: Dict[str, Any],
        sample_size: int,
        benchmark_data: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Calculate confidence score using triangulation

        Args:
            source_demographics: Dict of demographics by source (amazon, reddit, youtube)
            overall_demographics: Aggregated demographics across all sources
            sample_size: Total number of data points analyzed
            benchmark_data: Optional benchmark data from Pew Research/Statista

        Returns:
            Dict with confidence scores and breakdown

        Raises:
            ValueError: If source_demographics is empty or invalid
        """
        if not source_demographics:
            raise ValueError("Cannot calculate confidence with empty source demographics")

        self.trail.light(2570, {
            "action": "calculating_confidence",
            "num_sources": len(source_demographics),
            "sample_size": sample_size
        })

        # Calculate source agreement score
        # SPECIAL CASE: Single source = cannot triangulate, source_agreement = 0.0
        if len(source_demographics) == 1:
            self.trail.light(2546, {
                "warning": "single_source_no_triangulation",
                "message": "Only 1 data source - source agreement score set to 0.0 (cannot triangulate)",
                "source": list(source_demographics.keys())[0]
            })
            source_agreement = 0.0
            print(f"[!] WARNING: Single data source - no triangulation possible")
            print(f"    Source agreement score: 0.0 (40% weight penalty)")
            print(f"    This will significantly reduce overall confidence")
        else:
            source_agreement = self._calculate_source_agreement(source_demographics)

        # Calculate sample size score
        sample_size_score = self._calculate_sample_size_score(sample_size)

        # Calculate benchmark match score (if benchmark data provided)
        benchmark_match = 0.0
        if benchmark_data:
            benchmark_match = self._calculate_benchmark_match(overall_demographics, benchmark_data)
        else:
            # No benchmark data - reduce weight accordingly
            print("[!] WARNING: No benchmark data provided - confidence calculation will be less reliable")

        # Calculate weighted confidence score
        confidence_score = (
            source_agreement * self.config.WEIGHT_SOURCE_AGREEMENT +
            sample_size_score * self.config.WEIGHT_SAMPLE_SIZE +
            benchmark_match * self.config.WEIGHT_BENCHMARK_MATCH
        )

        # Round to 2 decimal places
        confidence_score = round(confidence_score, 4)

        self.trail.light(2571, {
            "action": "confidence_calculated",
            "confidence_score": confidence_score,
            "source_agreement": source_agreement,
            "sample_size_score": sample_size_score,
            "benchmark_match": benchmark_match
        })

        return {
            "confidence_score": confidence_score,
            "confidence_percentage": round(confidence_score * 100, 1),
            "breakdown": {
                "source_agreement": round(source_agreement, 4),
                "sample_size_score": round(sample_size_score, 4),
                "benchmark_match": round(benchmark_match, 4)
            },
            "weights": {
                "source_agreement": self.config.WEIGHT_SOURCE_AGREEMENT,
                "sample_size": self.config.WEIGHT_SAMPLE_SIZE,
                "benchmark_match": self.config.WEIGHT_BENCHMARK_MATCH
            },
            "meets_threshold": confidence_score >= self.config.CONFIDENCE_THRESHOLD
        }

    def _calculate_source_agreement(self, source_demographics: Dict[str, Dict[str, Any]]) -> float:
        """
        Calculate agreement score across sources

        Compares age distributions and occupation distributions

        Returns:
            Score between 0.0 and 1.0
        """
        sources = list(source_demographics.keys())

        # Extract age ranges from each source
        age_ranges = []
        for source in sources:
            demographics = source_demographics[source]
            age_dist = demographics.get('age_distribution', {})
            if age_dist:
                # Get dominant age range (highest percentage)
                dominant_age = max(age_dist.items(), key=lambda x: x[1])[0] if age_dist else None
                if dominant_age:
                    age_ranges.append(dominant_age)

        # Calculate age agreement (all sources agree on same age range?)
        age_agreement = len(set(age_ranges)) == 1 if age_ranges else 0

        # Extract top occupations from each source
        top_occupations = []
        for source in sources:
            demographics = source_demographics[source]
            occupations = demographics.get('top_occupations', [])
            if occupations:
                top_occ = occupations[0]['occupation'] if occupations else None
                if top_occ:
                    top_occupations.append(top_occ)

        # Calculate occupation agreement
        occupation_agreement = len(set(top_occupations)) == 1 if top_occupations else 0

        # Extract gender distributions
        gender_percentages = []
        for source in sources:
            demographics = source_demographics[source]
            gender_dist = demographics.get('gender_distribution', {})
            male_pct = gender_dist.get('male', 0)
            gender_percentages.append(male_pct)

        # Calculate gender variance (lower variance = higher agreement)
        gender_variance = 0
        if len(gender_percentages) >= 2:
            try:
                variance = statistics.stdev(gender_percentages)
                # Convert variance to agreement score (0-1 scale)
                # Variance of 0 = perfect agreement (1.0)
                # Variance of 20+ = poor agreement (0.0)
                gender_variance = max(0, 1.0 - (variance / 20.0))
            except statistics.StatisticsError:
                gender_variance = 0

        # Weighted average of agreements
        total_score = (
            (1.0 if age_agreement else 0.0) * 0.4 +
            (1.0 if occupation_agreement else 0.0) * 0.4 +
            gender_variance * 0.2
        )

        return total_score

    def _calculate_sample_size_score(self, sample_size: int) -> float:
        """
        Calculate sample size adequacy score

        Based on research report: 300+ samples = 1.0, scales linearly below that

        Args:
            sample_size: Number of data points analyzed

        Returns:
            Score between 0.0 and 1.0
        """
        if sample_size >= self.config.MIN_DATA_POINTS_REQUIRED:
            return 1.0

        # Linear scaling below minimum
        return min(sample_size / self.config.MIN_DATA_POINTS_REQUIRED, 1.0)

    def _calculate_benchmark_match(
        self,
        demographics: Dict[str, Any],
        benchmark: Dict[str, Any]
    ) -> float:
        """
        Calculate match score against industry benchmark

        Compares age and gender distributions

        Args:
            demographics: Our extracted demographics
            benchmark: Benchmark data (e.g., from Pew Research)

        Returns:
            Score between 0.0 and 1.0
        """
        # Extract our age distribution
        our_age_dist = demographics.get('age_distribution', {})
        benchmark_age = benchmark.get('age_range', None)

        # Check if our dominant age matches benchmark
        age_match = 0.0
        if our_age_dist and benchmark_age:
            dominant_age = max(our_age_dist.items(), key=lambda x: x[1])[0]
            # Simple string matching
            if benchmark_age.lower() in dominant_age.lower() or dominant_age.lower() in benchmark_age.lower():
                age_match = 1.0

        # Extract our gender distribution
        our_gender_dist = demographics.get('gender_distribution', {})
        our_male_pct = our_gender_dist.get('male', 0)

        benchmark_male_pct = benchmark.get('gender_male_percentage', None)

        # Calculate gender match (within 10% tolerance)
        gender_match = 0.0
        if benchmark_male_pct is not None:
            deviation = abs(our_male_pct - benchmark_male_pct)
            if deviation <= 10:
                gender_match = 1.0 - (deviation / 10.0)

        # Average of age and gender matches
        return (age_match + gender_match) / 2.0

    def get_low_confidence_reasons(
        self,
        confidence_result: Dict[str, Any],
        source_demographics: Dict[str, Dict[str, Any]],
        sample_size: int
    ) -> List[str]:
        """
        Generate list of reasons why confidence is low

        Args:
            confidence_result: Result from calculate_confidence()
            source_demographics: Dict of demographics by source
            sample_size: Total sample size

        Returns:
            List of human-readable reason strings
        """
        reasons = []

        breakdown = confidence_result['breakdown']

        # Check source agreement
        if breakdown['source_agreement'] < 0.7:
            reasons.append(
                f"Low source agreement ({breakdown['source_agreement']:.1%}). "
                f"Sources disagree on demographics - need more data or validation."
            )

        # Check sample size
        if breakdown['sample_size_score'] < 1.0:
            reasons.append(
                f"Small sample size ({sample_size} data points). "
                f"Minimum recommended: {self.config.MIN_DATA_POINTS_REQUIRED}."
            )

        # Check benchmark match
        if breakdown['benchmark_match'] < self.config.MIN_BENCHMARK_MATCH:
            reasons.append(
                f"Poor benchmark match ({breakdown['benchmark_match']:.1%}). "
                f"Demographics don't align with industry benchmarks."
            )

        # Check number of sources
        if len(source_demographics) < 3:
            reasons.append(
                f"Only {len(source_demographics)} data sources available. "
                f"Recommended: 3+ sources for higher confidence."
            )

        return reasons
