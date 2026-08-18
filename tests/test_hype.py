"""
TEST 5: Quality Gate & Hype Suppression
Verifies that low-value, high-hype content like '10 AI Tools That Will Guarantee You a Job'
is suppressed despite high surface keyword or semantic similarity.
"""

import pytest
from engine.quality_engine import QualityEngine
from engine.nexus_pipeline import NexusPipeline
from services.data_loader import DataLoader
from models.schemas import ReelItem, LatentInterestResult


def test_quality_gate_suppresses_hype():
    """Verifies that high-hype clickbait reels are suppressed by the Quality Gate."""
    gate = QualityEngine()

    hype_reel = ReelItem(
        reel_id="N001",
        title="10 AI Tools That Will Guarantee You a Job",
        category="Career",
        topic="AI Tools",
        difficulty="Beginner",
        educational_value=0.18,
        hype_score=0.96,
        semantic_tags="ai,career,hype"
    )

    latent_interest = LatentInterestResult(
        primary_latent_interest="Artificial Intelligence",
        confidence_score=0.9,
        confidence_label="High"
    )

    is_suppressed, reason = gate.evaluate_candidate(hype_reel, semantic_relevance=92.0, latent_interest=latent_interest)

    assert is_suppressed is True
    assert reason is not None
    assert "hype score" in reason.lower() or "clickbait" in reason.lower() or "educational" in reason.lower()


def test_contrast_candidate_selection():
    """Verifies that the pipeline identifies a suppressed hype candidate for transparent comparison."""
    pipeline = NexusPipeline()
    loader = DataLoader()
    presets = loader.get_test_presets()
    trap_reels = presets["Test 1: Built-in Trap (Java/SWE/Interview/Laptop -> System Design)"]

    output, _, _, _ = pipeline.run(trap_reels)

    # There should be a rejected candidate identified for 'Why Not This?'
    assert output.rejected_candidate is not None
    assert output.rejected_candidate.is_suppressed is True
    assert output.why_not_this is not None
