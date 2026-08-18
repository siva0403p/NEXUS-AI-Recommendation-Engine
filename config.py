"""
NEXUS - Configuration Module
Defines ranking weights, model parameters, thresholds, and data paths.
All weights and parameters are configurable to allow transparent tuning.
"""

from pathlib import Path
import os

# Base paths
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
CACHE_DIR = BASE_DIR / ".cache"

# Ensure cache directory exists
CACHE_DIR.mkdir(parents=True, exist_ok=True)

# Data file paths
INTERACTION_HISTORY_PATH = DATA_DIR / "interaction_history.csv"
CANDIDATE_REELS_PATH = DATA_DIR / "candidate_reels.csv"
NEGATIVE_CANDIDATES_PATH = DATA_DIR / "negative_candidates.csv"
REEL_CATALOG_PATH = DATA_DIR / "reel_catalog.csv"
EMBEDDINGS_CACHE_PATH = CACHE_DIR / "embeddings_cache.json"
ANALYSIS_CACHE_PATH = CACHE_DIR / "analysis_cache.json"

# AI Model Configuration
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "text-embedding-004")

# Multi-Objective NEXUS Ranking Weights (Sum of base weights = 1.0)
WEIGHT_SEMANTIC_RELEVANCE = 0.35
WEIGHT_INTEREST_ALIGNMENT = 0.25
WEIGHT_NOVELTY = 0.15
WEIGHT_EDUCATIONAL_VALUE = 0.15
WEIGHT_DIFFICULTY_FIT = 0.10

# Penalty Weights & Multipliers
HYPE_PENALTY_MULTIPLIER = 1.0       # Max subtraction proportional to hype_score
REDUNDANCY_PENALTY_WEIGHT = 0.15    # Penalty for exact duplicate category/topic matching without growth

# Quality & Hype Filter Thresholds
HYPE_SUPPRESSION_THRESHOLD = 0.65   # Suppress candidates with hype_score above this
MIN_EDUCATIONAL_VALUE = 0.40        # Suppress candidates with educational_value below this

# Retrieval Configuration
TOP_K_CANDIDATES = 10               # Size of shortlisted candidate pool before final ranking

# Difficulty progression mapping
DIFFICULTY_LEVELS = {
    "Beginner": 1,
    "Intermediate": 2,
    "Advanced": 3
}

# Category domain taxonomy for interest mapping
CATEGORY_TAXONOMY = {
    "Java": "Software Engineering",
    "DSA": "Software Engineering",
    "Backend": "Software Engineering",
    "HLD": "Software Engineering",
    "Web Development": "Software Engineering",
    "DevOps": "Cloud & Infrastructure",
    "Cloud": "Cloud & Infrastructure",
    "Databases": "Data & Backend Systems",
    "Python": "Data & Python Engineering",
    "AI": "Artificial Intelligence",
    "Hardware": "Computer Systems & Hardware",
    "Cybersecurity": "Cybersecurity & Systems",
    "Career": "Career & Professional Growth"
}
