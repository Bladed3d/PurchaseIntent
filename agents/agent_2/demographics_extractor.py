"""
Demographics Extractor - Extract demographic profiles from reviews/comments

Uses direct extraction logic (NO paid Anthropic API).
Prepared for Task tool integration when available.

LED Range: 2540-2559
"""

import json
import re
from typing import List, Dict, Any
from dataclasses import dataclass, asdict


@dataclass
class DemographicProfile:
    """Individual demographic profile extracted from review/comment"""
    review_id: str
    age_range: str
    age_confidence: int  # 0-10
    gender: str  # "male", "female", "unknown"
    gender_confidence: int
    occupation: str
    occupation_confidence: int
    life_stage: str
    pain_points: List[str]
    interests: List[str]
    source_text: str  # Original review/comment for reference


class DemographicsExtractor:
    """Extract demographic data from text using pattern matching"""

    # Age indicators
    AGE_PATTERNS = {
        "gen_z": [r"\b(18|19|20|21|22|23|24)\b", r"gen z", r"zoomer", r"college student", r"just graduated"],
        "millennial": [r"\b(25|26|27|28|29|30|31|32|33|34|35|36|37|38|39|40)\b", r"millennial", r"started my business"],
        "gen_x": [r"\b(41|42|43|44|45|46|47|48|49|50|51|52|53|54|55)\b", r"gen x", r"mid-career"],
        "boomer": [r"\b(56|57|58|59|60|61|62|63|64|65|66|67|68|69|70)\b", r"boomer", r"retire", r"retirement"]
    }

    # Gender indicators (only use if explicitly stated)
    GENDER_PATTERNS = {
        "male": [r"\bi'm a (man|guy|dude|male)\b", r"as a (man|guy|dude|male)", r"\bhe/him\b"],
        "female": [r"\bi'm a (woman|girl|lady|female)\b", r"as a (woman|lady|female)", r"\bshe/her\b"]
    }

    # Occupation indicators
    OCCUPATION_PATTERNS = {
        "entrepreneur": [r"founder", r"startup", r"my business", r"entrepreneur", r"own company", r"started my"],
        "software_developer": [r"developer", r"programmer", r"software engineer", r"coder", r"tech role"],
        "manager": [r"manager", r"director", r"executive", r"team lead", r"supervisor"],
        "freelancer": [r"freelance", r"consultant", r"self-employed", r"independent"],
        "student": [r"student", r"college", r"university", r"studying"],
        "teacher": [r"teacher", r"educator", r"professor", r"instructor"]
    }

    # Pain point indicators
    PAIN_POINT_PATTERNS = {
        "time_management": [r"time management", r"not enough time", r"too busy", r"manage my time"],
        "delegation": [r"delegat(e|ion)", r"hiring", r"building a team", r"can't do everything"],
        "work_life_balance": [r"work.?life balance", r"burnout", r"overworked", r"no time for family"],
        "focus": [r"focus", r"distract(ed|ion)", r"concentrate", r"adhd", r"attention"],
        "procrastination": [r"procrastinat", r"putting off", r"avoid(ing)?", r"delay(ing)?"],
        "scaling": [r"scal(e|ing)", r"grow(th|ing)", r"expand(ing)?", r"next level"]
    }

    # Interest indicators
    INTEREST_PATTERNS = {
        "productivity": [r"productivity", r"efficient", r"optimize", r"systemize"],
        "business_growth": [r"business growth", r"revenue", r"profit", r"scale"],
        "self_improvement": [r"self.?improve", r"personal development", r"better myself"],
        "career_advancement": [r"career", r"promotion", r"advancement", r"next job"],
        "passive_income": [r"passive income", r"automat(e|ion)", r"recurring revenue"]
    }

    def __init__(self, trail):
        """
        Initialize demographics extractor

        Args:
            trail: BreadcrumbTrail for LED tracking
        """
        self.trail = trail

    def extract_from_batch(self, reviews: List[Dict[str, Any]]) -> List[DemographicProfile]:
        """
        Extract demographics from a batch of reviews/comments

        Args:
            reviews: List of review dicts with 'text' and 'id' fields

        Returns:
            List of DemographicProfile objects

        Raises:
            ValueError: If reviews is empty or missing required fields
        """
        if not reviews:
            raise ValueError("Cannot extract demographics from empty review list")

        # Validate reviews have required fields
        for review in reviews:
            if 'text' not in review:
                raise KeyError(f"Review {review.get('id', 'unknown')} missing 'text' field")
            if 'id' not in review:
                raise KeyError("Review missing 'id' field")

        self.trail.light(2540, {
            "action": "extracting_demographics",
            "batch_size": len(reviews)
        })

        profiles = []
        for review in reviews:
            profile = self._extract_single_profile(review)
            if profile:
                profiles.append(profile)

        self.trail.light(2541, {
            "action": "extraction_complete",
            "profiles_extracted": len(profiles)
        })

        if len(profiles) == 0:
            raise ValueError(f"Failed to extract any demographic profiles from {len(reviews)} reviews")

        return profiles

    def _extract_single_profile(self, review: Dict[str, Any]) -> DemographicProfile:
        """Extract demographic profile from single review"""
        text = review['text'].lower()

        # Extract age
        age_range, age_conf = self._extract_age(text)

        # Extract gender (only if explicit)
        gender, gender_conf = self._extract_gender(text)

        # Extract occupation
        occupation, occ_conf = self._extract_occupation(text)

        # Extract life stage
        life_stage = self._infer_life_stage(age_range, occupation, text)

        # Extract pain points
        pain_points = self._extract_pain_points(text)

        # Extract interests
        interests = self._extract_interests(text)

        return DemographicProfile(
            review_id=review['id'],
            age_range=age_range,
            age_confidence=age_conf,
            gender=gender,
            gender_confidence=gender_conf,
            occupation=occupation,
            occupation_confidence=occ_conf,
            life_stage=life_stage,
            pain_points=pain_points,
            interests=interests,
            source_text=review['text'][:200]  # First 200 chars for reference
        )

    def _extract_age(self, text: str) -> tuple[str, int]:
        """Extract age range from text"""
        for age_range, patterns in self.AGE_PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, text, re.IGNORECASE):
                    # Higher confidence for explicit age numbers
                    confidence = 9 if r"\b\d+" in pattern else 6
                    return (age_range, confidence)

        # Default: unknown
        return ("unknown", 0)

    def _extract_gender(self, text: str) -> tuple[str, int]:
        """Extract gender from text (only if explicitly stated)"""
        for gender, patterns in self.GENDER_PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, text, re.IGNORECASE):
                    return (gender, 8)

        return ("unknown", 0)

    def _extract_occupation(self, text: str) -> tuple[str, int]:
        """Extract occupation from text"""
        occupation_scores = {}

        for occupation, patterns in self.OCCUPATION_PATTERNS.items():
            score = 0
            for pattern in patterns:
                matches = len(re.findall(pattern, text, re.IGNORECASE))
                score += matches

            if score > 0:
                occupation_scores[occupation] = score

        if not occupation_scores:
            return ("unknown", 0)

        # Return occupation with highest score
        best_occupation = max(occupation_scores.items(), key=lambda x: x[1])
        confidence = min(best_occupation[1] * 3, 10)  # Cap at 10

        return (best_occupation[0], confidence)

    def _infer_life_stage(self, age_range: str, occupation: str, text: str) -> str:
        """Infer life stage from age and occupation"""
        if age_range == "gen_z" or occupation == "student":
            return "student"
        elif age_range == "millennial" and occupation in ["entrepreneur", "software_developer"]:
            return "early_career_professional"
        elif age_range == "gen_x" or "parent" in text.lower():
            return "mid_career_parent"
        elif age_range == "boomer" or "retire" in text.lower():
            return "retiree"
        else:
            return "professional"

    def _extract_pain_points(self, text: str) -> List[str]:
        """Extract pain points mentioned in text"""
        pain_points = []

        for pain, patterns in self.PAIN_POINT_PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, text, re.IGNORECASE):
                    pain_points.append(pain)
                    break  # Only add each pain point once

        return pain_points

    def _extract_interests(self, text: str) -> List[str]:
        """Extract interests mentioned in text"""
        interests = []

        for interest, patterns in self.INTEREST_PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, text, re.IGNORECASE):
                    interests.append(interest)
                    break  # Only add each interest once

        return interests

    def profiles_to_dict(self, profiles: List[DemographicProfile]) -> List[Dict[str, Any]]:
        """Convert profiles to dictionary format for JSON serialization"""
        return [asdict(profile) for profile in profiles]
