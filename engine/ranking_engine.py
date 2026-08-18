"""
NEXUS - Multi-Objective Ranking Engine
Calculates transparent, deterministic multi-objective composite scores combining
semantic relevance, latent interest alignment, novelty, educational value, difficulty fit,
and calibrated hype/redundancy penalties.
"""

from typing import List, Dict, Optional, Tuple
from models.schemas import ReelItem, ScoredCandidate, LatentInterestResult, NextSkillInference, ReelAnalysis
from engine.quality_engine import QualityEngine
from config import (
    WEIGHT_SEMANTIC_RELEVANCE,
    WEIGHT_INTEREST_ALIGNMENT,
    WEIGHT_NOVELTY,
    WEIGHT_EDUCATIONAL_VALUE,
    WEIGHT_DIFFICULTY_FIT,
    HYPE_PENALTY_MULTIPLIER,
    REDUNDANCY_PENALTY_WEIGHT,
    DIFFICULTY_LEVELS,
    CATEGORY_TAXONOMY
)


class RankingEngine:
    """Computes multi-objective NEXUS ranking scores with complete component explainability."""

    def __init__(
        self,
        weight_relevance: float = WEIGHT_SEMANTIC_RELEVANCE,
        weight_interest: float = WEIGHT_INTEREST_ALIGNMENT,
        weight_novelty: float = WEIGHT_NOVELTY,
        weight_educational: float = WEIGHT_EDUCATIONAL_VALUE,
        weight_difficulty: float = WEIGHT_DIFFICULTY_FIT,
        quality_engine: Optional[QualityEngine] = None
    ):
        self.w_rel = weight_relevance
        self.w_int = weight_interest
        self.w_nov = weight_novelty
        self.w_edu = weight_educational
        self.w_dif = weight_difficulty
        self.quality_engine = quality_engine or QualityEngine()

    def update_weights(
        self,
        weight_relevance: float,
        weight_interest: float,
        weight_novelty: float,
        weight_educational: float,
        weight_difficulty: float
    ):
        """Allows real-time tuning of ranking weights via UI controls."""
        total = weight_relevance + weight_interest + weight_novelty + weight_educational + weight_difficulty
        if total > 0:
            self.w_rel = round(weight_relevance / total, 4)
            self.w_int = round(weight_interest / total, 4)
            self.w_nov = round(weight_novelty / total, 4)
            self.w_edu = round(weight_educational / total, 4)
            self.w_dif = round(weight_difficulty / total, 4)

    def score_candidate(
        self,
        candidate: ReelItem,
        raw_semantic_sim: float,
        latent_interest: LatentInterestResult,
        next_skill: NextSkillInference,
        watched_reels: List[ReelItem],
        analyses: List[ReelAnalysis]
    ) -> ScoredCandidate:
        """
        Evaluates a single candidate across all 5 objectives and penalties.
        All individual components are calculated on a [0.0, 100.0] scale.
        """
        # 1. Semantic Relevance (0-100)
        # Scaled from cosine similarity
        semantic_relevance = round(raw_semantic_sim * 100.0, 1)

        # 2. Latent Interest Alignment (0-100)
        # Checks alignment with primary interest, secondary interests, and target skill category
        cand_domain = CATEGORY_TAXONOMY.get(candidate.category, candidate.category)
        primary_match = (
            candidate.category == next_skill.target_category or
            cand_domain == latent_interest.primary_latent_interest or
            candidate.category in latent_interest.primary_latent_interest
        )
        if primary_match:
            interest_alignment = 96.0
        elif any(cand_domain == sec for sec in latent_interest.secondary_latent_interests):
            interest_alignment = 82.0
        else:
            interest_alignment = 65.0

        # 3. Novelty (0-100)
        # Measures discovery value — higher if introducing an adjacent new skill rather than repeating watched topics
        watched_topics = {r.topic.lower() for r in watched_reels}
        watched_categories = {r.category for r in watched_reels}

        if candidate.topic.lower() not in watched_topics and candidate.category not in watched_categories:
            novelty = 92.0  # Fresh domain topic
        elif candidate.topic.lower() not in watched_topics:
            novelty = 84.0  # Fresh topic within familiar category
        else:
            novelty = 45.0  # Exact repeat topic

        # 4. Educational Value (0-100)
        educational_value = round(candidate.educational_value * 100.0, 1)

        # 5. Difficulty Fit (0-100)
        # Inferred student level based on interaction history
        hist_levels = [DIFFICULTY_LEVELS.get(r.difficulty, 2) for r in watched_reels]
        avg_hist_level = sum(hist_levels) / max(1, len(hist_levels))
        cand_level = DIFFICULTY_LEVELS.get(candidate.difficulty, 2)

        # Ideal progression is matching or +0.5 to +1.0 above current level
        diff_gap = abs((avg_hist_level + 0.3) - cand_level)
        difficulty_fit = max(60.0, round(100.0 - (diff_gap * 20.0), 1))

        # 6. Penalties
        # Hype Penalty proportional to hype_score
        hype_penalty = round(candidate.hype_score * 25.0 * HYPE_PENALTY_MULTIPLIER, 1)

        # Redundancy Penalty if the candidate is too similar to the exact last watched reel
        redundancy_penalty = 0.0
        if watched_reels and candidate.topic.lower() == watched_reels[-1].topic.lower():
            redundancy_penalty = 15.0

        # 7. Weighted Composite NEXUS Score
        raw_score = (
            (self.w_rel * semantic_relevance) +
            (self.w_int * interest_alignment) +
            (self.w_nov * novelty) +
            (self.w_edu * educational_value) +
            (self.w_dif * difficulty_fit)
        )
        final_score = round(max(0.0, min(100.0, raw_score - hype_penalty - redundancy_penalty)), 1)

        # 8. Quality Gate Assessment
        is_suppressed, suppression_reason = self.quality_engine.evaluate_candidate(
            candidate, semantic_relevance, latent_interest
        )

        return ScoredCandidate(
            reel=candidate,
            semantic_relevance=semantic_relevance,
            interest_alignment=interest_alignment,
            novelty=novelty,
            educational_value=educational_value,
            difficulty_fit=difficulty_fit,
            hype_penalty=hype_penalty,
            redundancy_penalty=redundancy_penalty,
            nexus_score=final_score,
            is_suppressed=is_suppressed,
            suppression_reason=suppression_reason
        )

    def rank_candidates(
        self,
        candidate_pairs: List[Tuple[ReelItem, float]],
        latent_interest: LatentInterestResult,
        next_skill: NextSkillInference,
        watched_reels: List[ReelItem],
        analyses: List[ReelAnalysis]
    ) -> List[ScoredCandidate]:
        """Scores and sorts candidate pairs into final ranked candidates."""
        scored: List[ScoredCandidate] = []
        for cand, sim in candidate_pairs:
            sc = self.score_candidate(
                candidate=cand,
                raw_semantic_sim=sim,
                latent_interest=latent_interest,
                next_skill=next_skill,
                watched_reels=watched_reels,
                analyses=analyses
            )
            scored.append(sc)

        # Sort: unsuppressed candidates with highest nexus_score first
        scored.sort(key=lambda x: (not x.is_suppressed, x.nexus_score), reverse=True)
        return scored
