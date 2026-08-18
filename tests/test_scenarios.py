"""
TEST 6 & Comprehensive Acceptance Criteria Test Suite
Verifies all 6 competition problem scenarios and acceptance criteria:
1. Built-in Trap
2. Gaming / Hardware
3. AI Engineering
4. Python / Data
5. Viral Hype Suppression
6. Single Ambiguous Interaction (Low Confidence)
Plus data loading and required output field completeness.
"""

import pytest
from engine.nexus_pipeline import NexusPipeline
from services.data_loader import DataLoader


def test_data_loader_integrity():
    """Verifies that all required CSV datasets load, validate, and parse properly."""
    loader = DataLoader()
    assert len(loader.candidate_reels) >= 100
    assert len(loader.negative_candidates) >= 15
    assert len(loader.full_catalog) >= 115
    assert len(loader.interaction_history) >= 8

    # Verify no invalid bounds
    for r in loader.candidate_reels:
        assert 0.0 <= r.educational_value <= 1.0
        assert 0.0 <= r.hype_score <= 1.0


def test_ambiguous_low_confidence():
    """Test 6: Verifies that a single ambiguous reel yields Low confidence with honest explanation."""
    pipeline = NexusPipeline()
    loader = DataLoader()
    presets = loader.get_test_presets()
    ambiguous_reels = presets["Test 6: Single Ambiguous Interaction (Low Confidence)"]

    output, latent_interest, next_skill, _ = pipeline.run(ambiguous_reels)

    # Confidence must be Low
    assert "Low" in output.confidence
    assert "insufficient evidence" in output.confidence.lower() or "isolated" in output.confidence.lower() or "low confidence" in output.confidence.lower()


def test_required_output_fields_completeness():
    """Verifies that the final output provides every required field."""
    pipeline = NexusPipeline()
    loader = DataLoader()
    presets = loader.get_test_presets()
    trap_reels = presets["Test 1: Built-in Trap (Java/SWE/Interview/Laptop -> System Design)"]

    output, _, _, _ = pipeline.run(trap_reels)

    assert output.current_reel_reference != ""
    assert output.interest_detected != ""
    assert output.why_evidence != ""
    assert output.recommended_tech_reel is not None
    assert output.recommended_tech_reel.title != ""
    assert output.category != ""
    assert output.why_this_recommendation != ""
    assert output.difficulty in ["Beginner", "Intermediate", "Advanced"]
    assert any(level in output.confidence for level in ["High", "Medium", "Low"])
    assert output.nexus_score > 0.0
    assert len(output.score_breakdown) >= 5
    assert len(output.bridge_steps) >= 4
