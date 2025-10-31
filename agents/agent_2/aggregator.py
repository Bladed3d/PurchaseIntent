"""
Demographics Aggregator - Cluster and aggregate demographic profiles

LED Range: 2560-2569
"""

from typing import List, Dict, Any
from collections import Counter
from dataclasses import dataclass, asdict


@dataclass
class DemographicCluster:
    """Aggregated demographic cluster"""
    cluster_id: str
    size: int
    age_range: str
    age_distribution: Dict[str, float]
    gender_distribution: Dict[str, float]
    top_occupations: List[Dict[str, Any]]
    top_pain_points: List[Dict[str, Any]]
    top_interests: List[str]
    life_stage: str


class DemographicsAggregator:
    """Aggregate and cluster demographic profiles"""

    def __init__(self, trail):
        """
        Initialize aggregator

        Args:
            trail: BreadcrumbTrail for LED tracking
        """
        self.trail = trail

    def aggregate_profiles(self, profiles: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Aggregate individual profiles into overall demographics

        Args:
            profiles: List of DemographicProfile dicts

        Returns:
            Dict with aggregated demographics

        Raises:
            ValueError: If profiles is empty
        """
        if not profiles:
            raise ValueError("Cannot aggregate empty profile list")

        self.trail.light(2560, {
            "action": "aggregating_demographics",
            "total_profiles": len(profiles)
        })

        # Calculate age distribution
        age_counts = Counter([p['age_range'] for p in profiles if p['age_range'] != 'unknown'])
        total_age = sum(age_counts.values())

        if total_age == 0:
            raise ValueError("No valid age data found in profiles - cannot calculate age distribution")

        age_distribution = {
            age: round(count / total_age * 100, 1)
            for age, count in age_counts.items()
        }

        # Calculate gender distribution
        gender_counts = Counter([p['gender'] for p in profiles])
        total_gender = sum(gender_counts.values())
        gender_distribution = {
            gender: round(count / total_gender * 100, 1)
            for gender, count in gender_counts.items()
        }

        # Calculate occupation frequencies
        occupation_counts = Counter([
            p['occupation'] for p in profiles if p['occupation'] != 'unknown'
        ])
        total_occupations = sum(occupation_counts.values())

        if total_occupations == 0:
            raise ValueError("No valid occupation data found in profiles")

        top_occupations = [
            {
                "occupation": occ,
                "frequency": round(count / total_occupations * 100, 1),
                "count": count
            }
            for occ, count in occupation_counts.most_common(10)
        ]

        # Calculate pain point frequencies
        pain_point_counts = Counter()
        for profile in profiles:
            for pain in profile['pain_points']:
                pain_point_counts[pain] += 1

        top_pain_points = [
            {
                "pain": pain,
                "mentions": count,
                "percentage": round(count / len(profiles) * 100, 1)
            }
            for pain, count in pain_point_counts.most_common(10)
        ]

        # Calculate interest frequencies
        interest_counts = Counter()
        for profile in profiles:
            for interest in profile['interests']:
                interest_counts[interest] += 1

        top_interests = [interest for interest, _ in interest_counts.most_common(10)]

        # Determine most common age range and life stage
        most_common_age = age_counts.most_common(1)[0][0] if age_counts else "unknown"
        life_stage_counts = Counter([p['life_stage'] for p in profiles])
        most_common_life_stage = life_stage_counts.most_common(1)[0][0] if life_stage_counts else "unknown"

        aggregated = {
            "age_range": most_common_age,
            "age_distribution": age_distribution,
            "gender_distribution": gender_distribution,
            "top_occupations": top_occupations,
            "top_pain_points": top_pain_points,
            "top_interests": top_interests,
            "life_stage": most_common_life_stage
        }

        self.trail.light(2561, {
            "action": "aggregation_complete",
            "age_range": most_common_age,
            "top_occupation": top_occupations[0]['occupation'] if top_occupations else None
        })

        return aggregated

    def cluster_profiles(self, profiles: List[Dict[str, Any]], num_clusters: int = 4) -> List[DemographicCluster]:
        """
        Cluster profiles into distinct customer segments

        Uses simple rule-based clustering (no ML dependencies needed for MVP)

        Args:
            profiles: List of DemographicProfile dicts
            num_clusters: Target number of clusters (default: 4)

        Returns:
            List of DemographicCluster objects

        Raises:
            ValueError: If profiles is empty
        """
        if not profiles:
            raise ValueError("Cannot cluster empty profile list")

        self.trail.light(2562, {
            "action": "clustering_profiles",
            "num_profiles": len(profiles),
            "target_clusters": num_clusters
        })

        # Simple clustering by occupation + age combination
        clusters_dict = {}

        for profile in profiles:
            # Create cluster key from occupation and age
            occupation = profile['occupation']
            age = profile['age_range']
            cluster_key = f"{occupation}_{age}"

            if cluster_key not in clusters_dict:
                clusters_dict[cluster_key] = []

            clusters_dict[cluster_key].append(profile)

        # Convert to DemographicCluster objects
        clusters = []
        for cluster_id, cluster_profiles in clusters_dict.items():
            cluster = self._create_cluster(cluster_id, cluster_profiles)
            clusters.append(cluster)

        # Sort by size (largest first)
        clusters.sort(key=lambda c: c.size, reverse=True)

        # Take top N clusters
        clusters = clusters[:num_clusters]

        self.trail.light(2563, {
            "action": "clustering_complete",
            "clusters_created": len(clusters),
            "cluster_sizes": [c.size for c in clusters]
        })

        if len(clusters) == 0:
            raise ValueError("Failed to create any demographic clusters")

        return clusters

    def _create_cluster(self, cluster_id: str, cluster_profiles: List[Dict[str, Any]]) -> DemographicCluster:
        """Create DemographicCluster from list of profiles"""

        # Aggregate cluster demographics
        age_counts = Counter([p['age_range'] for p in cluster_profiles if p['age_range'] != 'unknown'])
        total_age = sum(age_counts.values())
        age_distribution = {
            age: round(count / total_age * 100, 1)
            for age, count in age_counts.items()
        } if total_age > 0 else {}

        gender_counts = Counter([p['gender'] for p in cluster_profiles])
        total_gender = sum(gender_counts.values())
        gender_distribution = {
            gender: round(count / total_gender * 100, 1)
            for gender, count in gender_counts.items()
        }

        occupation_counts = Counter([p['occupation'] for p in cluster_profiles])
        top_occupations = [
            {
                "occupation": occ,
                "frequency": round(count / len(cluster_profiles) * 100, 1),
                "count": count
            }
            for occ, count in occupation_counts.most_common(5)
        ]

        pain_point_counts = Counter()
        for profile in cluster_profiles:
            for pain in profile['pain_points']:
                pain_point_counts[pain] += 1

        top_pain_points = [
            {
                "pain": pain,
                "mentions": count,
                "percentage": round(count / len(cluster_profiles) * 100, 1)
            }
            for pain, count in pain_point_counts.most_common(5)
        ]

        interest_counts = Counter()
        for profile in cluster_profiles:
            for interest in profile['interests']:
                interest_counts[interest] += 1

        top_interests = [interest for interest, _ in interest_counts.most_common(5)]

        # Determine dominant characteristics
        most_common_age = age_counts.most_common(1)[0][0] if age_counts else "unknown"
        life_stage_counts = Counter([p['life_stage'] for p in cluster_profiles])
        most_common_life_stage = life_stage_counts.most_common(1)[0][0] if life_stage_counts else "unknown"

        return DemographicCluster(
            cluster_id=cluster_id,
            size=len(cluster_profiles),
            age_range=most_common_age,
            age_distribution=age_distribution,
            gender_distribution=gender_distribution,
            top_occupations=top_occupations,
            top_pain_points=top_pain_points,
            top_interests=top_interests,
            life_stage=most_common_life_stage
        )

    def clusters_to_dict(self, clusters: List[DemographicCluster]) -> List[Dict[str, Any]]:
        """Convert clusters to dictionary format for JSON serialization"""
        return [asdict(cluster) for cluster in clusters]
