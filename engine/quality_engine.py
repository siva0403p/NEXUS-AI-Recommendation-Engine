"""
NEXUS - Quality & Hype Gate
Evaluates candidate items for sensationalism, low educational depth, clickbait,
and suppressive hype signals while identifying a contrast candidate for 'Why Not This?'.
"""

from typing import List, Tuple, Optional
from models.schemas import ReelItem, ScoredCandidate, LatentInterestResult, NextSkillInference
from config import HYPE_SUPPRESSION_THRESHOLD, MIN_EDUCATIONAL_VALUE


class QualityEngine:
    """Evaluates candidates against quality criteria and flags hype/low-value content."""

    def __init__(
        self,
        hype_threshold: float = HYPE_SUPPRESSION_THRESHOLD,
        min_educational_value: float = MIN_EDUCATIONAL_VALUE
    ):
        self.hype_threshold = hype_threshold
        self.min_educational_value = min_educational_value

    def evaluate_candidate(
        self,
        reel: ReelItem,
        semantic_relevance: float,
        latent_interest: LatentInterestResult
    ) -> Tuple[bool, Optional[str]]:
        """
        Determines whether a candidate passes the quality gate or should be suppressed.
        Returns (is_suppressed, suppression_reason).
        """
        reasons = []

        # Check 1: Excessive Hype Score
        if reel.hype_score >= self.hype_threshold:
            reasons.append(
                f"Elevated hype score ({reel.hype_score:.2f} >= threshold {self.hype_threshold:.2f})"
            )

        # Check 2: Insufficient Educational Depth
        if reel.educational_value < self.min_educational_value:
            reasons.append(
                f"Low educational depth ({reel.educational_value:.2f} < minimum {self.min_educational_value:.2f})"
            )

        # Check 3: Clickbait Title Heuristics
        title_lower = reel.title.lower()
        clickbait_patterns = [
            "get rich", "guarantee", "in 7 days", "overnight", "10x developer",
            "secret trick", "don't want you to know", "make ₹", "replace every developer",
            "10 ai tools that will", "secret prompt that makes"
        ]
        if any(pat in title_lower for pat in clickbait_patterns):
            reasons.append("Sensationalist clickbait / get-rich-quick framing detected")

        if reasons:
            explanation = "Suppressed by Quality Gate: " + "; ".join(reasons) + "."
            return True, explanation

        return False, None

    def find_suppressed_hype_contrast(
        self,
        negative_candidates: List[ReelItem],
        candidate_reels: List[ReelItem],
        latent_interest: LatentInterestResult,
        next_skill: NextSkillInference
    ) -> Optional[ReelItem]:
        """
        Finds a semantically related viral/hype candidate that NEXUS deliberately rejected
        to provide a crystal-clear 'Why Not The Viral One?' contrast.
        """
        # Pool all negative candidates + any high-hype regular candidates
        hype_pool = [r for r in negative_candidates] + [r for r in candidate_reels if r.hype_score >= 0.5]
        if not hype_pool:
            return None

        # Filter to candidates that share some domain relevance with the latent interest or target category
        interest_lower = latent_interest.primary_latent_interest.lower()
        target_cat = next_skill.target_category.lower()

        domain_matched = []
        for r in hype_pool:
            r_cat = r.category.lower()
            r_tags = r.semantic_tags.lower()
            r_title = r.title.lower()

            if (
                r_cat in interest_lower or interest_lower in r_cat or
                r_cat == target_cat or
                any(t in interest_lower for t in r_tags.split(",")) or
                "career" in r_cat or "ai" in r_cat or "hardware" in r_cat
            ):
                domain_matched.append(r)

        if domain_matched:
            # Sort by highest hype score to find the most representative viral clickbait
            domain_matched.sort(key=lambda x: (x.hype_score, -x.educational_value), reverse=True)
            return domain_matched[0]

        # Fallback to the highest hype candidate in pool
        hype_pool.sort(key=lambda x: x.hype_score, reverse=True)
        return hype_pool[0]
