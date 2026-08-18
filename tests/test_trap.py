"""
TEST 1: Built-in Trap Verification
Verifies that watching Java meme, SWE lifestyle, interview joke, laptop comparison,
and backend latency infers 'Software Engineering' (NOT just Java) and recommends
an adjacent next-skill like System Design / HLD.
"""

import pytest
from engine.nexus_pipeline import NexusPipeline
from services.data_loader import DataLoader
from models.schemas import ReelItem


def test_builtin_trap_evasion():
    """Verifies that the system avoids recommending another Java reel and recommends System Design."""
    pipeline = NexusPipeline()
    loader = DataLoader()
    presets = loader.get_test_presets()
    trap_reels = presets["Test 1: Built-in Trap (Java/SWE/Interview/Laptop -> System Design)"]

    output, latent_interest, next_skill, analyses = pipeline.run(trap_reels)

    # 1. Latent interest must be Software Engineering or broader engineering domain, NOT just 'Java'
    assert "Software Engineering" in latent_interest.primary_latent_interest or "Technology" in latent_interest.primary_latent_interest
    assert latent_interest.primary_latent_interest.strip().lower() != "java"

    # 2. Next skill must be an adjacent high-value architectural skill (e.g. System Design / HLD)
    assert next_skill.target_category in ["HLD", "Backend", "Architecture"] or "System Design" in next_skill.next_skill

    # 3. Winning recommendation should be in HLD / Backend / Architecture, NOT a repeat of generic Java syntax
    winning_category = output.category
    assert winning_category in ["HLD", "Backend", "DSA", "Software Engineering"]

    # 4. Explanation should explicitly mention the broader software engineering / system design connection
    assert "Software Engineering" in output.why_evidence or "software" in output.why_evidence.lower()
    assert output.why_this_recommendation is not None

    # 5. Confidence should be High since 5 converging interactions were observed
    assert "High" in output.confidence
