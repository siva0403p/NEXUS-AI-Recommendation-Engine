"""
TEST 2 & 4: Latent Interest & Next-Skill Inference Across Domains
Verifies that:
- Gaming / Hardware signals lead to Hardware / Systems (do NOT force Software Engineering).
- Python / Pandas / Automation leads to Data Engineering / Analytics.
- AI / RAG / Agents leads to AI Engineering.
"""

import pytest
from engine.nexus_pipeline import NexusPipeline
from services.data_loader import DataLoader


def test_gaming_hardware_interest():
    """Verifies that gaming/hardware reels converge on Hardware / Systems and not SWE."""
    pipeline = NexusPipeline()
    loader = DataLoader()
    presets = loader.get_test_presets()
    gaming_reels = presets["Test 2: Gaming & Hardware Systems"]

    output, latent_interest, next_skill, _ = pipeline.run(gaming_reels)

    # Latent interest must be Hardware / Systems / Gaming
    primary = latent_interest.primary_latent_interest.lower()
    assert any(term in primary for term in ["hardware", "systems", "gaming", "computer"])
    assert "software engineering" not in primary or "hardware" in primary

    # Winning recommendation category
    assert output.category in ["Hardware", "Systems", "Performance", "Cloud", "Cybersecurity"]


def test_python_data_interest():
    """Verifies that Python automation and Pandas converge on Data Engineering."""
    pipeline = NexusPipeline()
    loader = DataLoader()
    presets = loader.get_test_presets()
    data_reels = presets["Test 4: Python & Data Engineering"]

    output, latent_interest, next_skill, _ = pipeline.run(data_reels)

    primary = latent_interest.primary_latent_interest.lower()
    assert any(term in primary for term in ["data", "python", "analytics"])
    assert next_skill.target_category in ["Python", "Databases", "Data", "Backend", "AI"]


def test_ai_engineering_interest():
    """Verifies that RAG, Agents, and Vector DBs converge on AI Engineering."""
    pipeline = NexusPipeline()
    loader = DataLoader()
    presets = loader.get_test_presets()
    ai_reels = presets["Test 3: AI Engineering & Agents"]

    output, latent_interest, next_skill, _ = pipeline.run(ai_reels)

    primary = latent_interest.primary_latent_interest.lower()
    assert any(term in primary for term in ["ai", "artificial intelligence", "machine learning"])
    assert output.category == "AI"
