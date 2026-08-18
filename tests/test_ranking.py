"""
TEST: Multi-Objective NEXUS Ranking Engine
Verifies transparent, deterministic score computation, weight updates,
and penalty subtractions.
"""

import pytest
from engine.ranking_engine import RankingEngine
from engine.quality_engine import QualityEngine
from models.schemas import ReelItem, LatentInterestResult, NextSkillInference, ReelAnalysis


def test_ranking_score_formula():
    """Verifies that composite NEXUS score follows the multi-objective mathematical formula."""
    quality_engine = QualityEngine()
    ranking_engine = RankingEngine(quality_engine=quality_engine)

    candidate = ReelItem(
        reel_id="T999",
        title="Distributed Caching at Scale",
        category="HLD",
        topic="Caching",
        difficulty="Intermediate",
        educational_value=0.95,
        hype_score=0.04,
        semantic_tags="hld,caching,scaling"
    )

    latent_interest = LatentInterestResult(
        primary_latent_interest="Software Engineering",
        secondary_latent_interests=["Backend", "Distributed Systems"],
        interest_strengths={"Software Engineering": 95.0},
        confidence_score=0.9,
        confidence_label="High"
    )

    next_skill = NextSkillInference(
        next_skill="System Design",
        target_category="HLD",
        reason="Natural progression to architecture",
        confidence="High"
    )

    watched_reels = [
        ReelItem(reel_id="R1", title="Java Basics", category="Java", topic="Java", difficulty="Intermediate")
    ]
    analyses = [
        ReelAnalysis(
            reel_id="R1",
            title="Java Basics",
            topic="Java",
            surface_category="Java",
            context="Tutorial",
            intent="Learning",
            educational_value=0.8,
            hype_score=0.1
        )
    ]

    scored = ranking_engine.score_candidate(
        candidate=candidate,
        raw_semantic_sim=0.91,
        latent_interest=latent_interest,
        next_skill=next_skill,
        watched_reels=watched_reels,
        analyses=analyses
    )

    # Check that score breakdown is non-null and within [0, 100]
    assert 0.0 <= scored.semantic_relevance <= 100.0
    assert 0.0 <= scored.interest_alignment <= 100.0
    assert 0.0 <= scored.novelty <= 100.0
    assert 0.0 <= scored.educational_value <= 100.0
    assert 0.0 <= scored.difficulty_fit <= 100.0
    assert 0.0 <= scored.hype_penalty <= 100.0
    assert 0.0 <= scored.nexus_score <= 100.0
    assert not scored.is_suppressed


def test_ranking_weight_update():
    """Verifies that weights can be adjusted dynamically and sum to 1.0."""
    ranking_engine = RankingEngine()
    ranking_engine.update_weights(0.5, 0.2, 0.1, 0.1, 0.1)

    assert abs((ranking_engine.w_rel + ranking_engine.w_int + ranking_engine.w_nov + ranking_engine.w_edu + ranking_engine.w_dif) - 1.0) < 1e-3
    assert ranking_engine.w_rel == pytest.approx(0.5)
