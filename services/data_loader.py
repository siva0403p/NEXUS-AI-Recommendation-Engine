"""
NEXUS - Data Loader & Validation Service
Loads, validates, and manages interaction history, candidate reels,
negative hype candidates, and full catalog with robust error handling and presets.
"""

from typing import List, Dict, Optional, Tuple
import os
import pandas as pd
from pathlib import Path

from config import (
    INTERACTION_HISTORY_PATH,
    CANDIDATE_REELS_PATH,
    NEGATIVE_CANDIDATES_PATH,
    REEL_CATALOG_PATH,
    DATA_DIR
)
from models.schemas import ReelItem


class DataLoader:
    """Manages data ingestion, validation, and test presets for NEXUS."""

    def __init__(self):
        self.interaction_history: List[ReelItem] = []
        self.candidate_reels: List[ReelItem] = []
        self.negative_candidates: List[ReelItem] = []
        self.full_catalog: List[ReelItem] = []
        self._load_all_data()

    def _safe_read_csv(self, file_path: Path) -> pd.DataFrame:
        """Reads CSV with UTF-8 encoding, handling alternative filenames or missing files."""
        if not file_path.exists():
            # Check for alternative filename patterns (e.g. 'candidate_reels (1).csv')
            stem = file_path.stem
            alt_path = file_path.parent / f"{stem} (1).csv"
            if alt_path.exists():
                file_path = alt_path
            else:
                raise FileNotFoundError(f"Required dataset file not found: {file_path}")

        try:
            df = pd.read_csv(file_path, encoding="utf-8")
        except UnicodeDecodeError:
            df = pd.read_csv(file_path, encoding="latin-1")
        return df

    def _validate_and_clean_df(self, df: pd.DataFrame, expected_type: str) -> List[ReelItem]:
        """Validates schema, cleans nulls, deduplicates, and parses into ReelItem models."""
        items: List[ReelItem] = []
        seen_ids = set()

        for idx, row in df.iterrows():
            reel_id = str(row.get("reel_id", f"UNK_{idx}")).strip()
            if not reel_id or reel_id in seen_ids:
                continue
            seen_ids.add(reel_id)

            title = str(row.get("title", "Untitled Reel")).strip()
            category = str(row.get("category", "General Tech")).strip()
            topic = str(row.get("topic", category)).strip()
            difficulty = str(row.get("difficulty", "Intermediate")).strip()
            if difficulty not in ["Beginner", "Intermediate", "Advanced"]:
                difficulty = "Intermediate"

            # Parse numeric scores with bounds [0.0, 1.0]
            try:
                edu_val = float(row.get("educational_value", 0.8))
                edu_val = max(0.0, min(1.0, edu_val))
            except (ValueError, TypeError):
                edu_val = 0.8

            try:
                hype_score = float(row.get("hype_score", 0.1))
                hype_score = max(0.0, min(1.0, hype_score))
            except (ValueError, TypeError):
                hype_score = 0.1

            tags = str(row.get("semantic_tags", "")).strip()
            if tags.lower() == "nan":
                tags = ""

            prereqs = str(row.get("prerequisites", "")).strip()
            if prereqs.lower() == "nan":
                prereqs = ""

            source = str(row.get("source_type", expected_type)).strip()

            items.append(ReelItem(
                reel_id=reel_id,
                title=title,
                category=category,
                topic=topic,
                difficulty=difficulty,
                educational_value=edu_val,
                hype_score=hype_score,
                semantic_tags=tags,
                prerequisites=prereqs,
                source_type=source
            ))

        return items

    def _load_all_data(self):
        """Loads and initializes all 4 dataset components."""
        # 1. Interaction History
        if INTERACTION_HISTORY_PATH.exists():
            df_hist = self._safe_read_csv(INTERACTION_HISTORY_PATH)
            self.interaction_history = self._validate_and_clean_df(df_hist, "history")

        # 2. Candidate Reels
        if CANDIDATE_REELS_PATH.exists() or (DATA_DIR / "candidate_reels (1).csv").exists():
            df_cand = self._safe_read_csv(CANDIDATE_REELS_PATH)
            self.candidate_reels = self._validate_and_clean_df(df_cand, "candidate")

        # 3. Negative Candidates (Hype items)
        if NEGATIVE_CANDIDATES_PATH.exists():
            df_neg = self._safe_read_csv(NEGATIVE_CANDIDATES_PATH)
            self.negative_candidates = self._validate_and_clean_df(df_neg, "negative")

        # 4. Full Catalog
        if REEL_CATALOG_PATH.exists():
            df_cat = self._safe_read_csv(REEL_CATALOG_PATH)
            self.full_catalog = self._validate_and_clean_df(df_cat, "catalog")
        else:
            self.full_catalog = self.candidate_reels + self.negative_candidates

    def get_test_presets(self) -> Dict[str, List[ReelItem]]:
        """Returns the mandatory pre-defined test scenario presets for evaluation and demo."""
        # Preset 1: Built-in Trap (The core demo story)
        trap_reels = [
            ReelItem(
                reel_id="TRAP_01",
                title="Java Meme: Why Semicolons Matter",
                category="Java",
                topic="Java",
                difficulty="Intermediate",
                semantic_tags="programming,java,developer,meme",
                educational_value=0.6,
                hype_score=0.1
            ),
            ReelItem(
                reel_id="TRAP_02",
                title="Software Engineer Lifestyle: Day in SF",
                category="Career",
                topic="Software Engineering",
                difficulty="Intermediate",
                semantic_tags="career,software-engineering,developer,lifestyle",
                educational_value=0.5,
                hype_score=0.2
            ),
            ReelItem(
                reel_id="TRAP_03",
                title="Coding Interview Joke: FizzBuzz Fail",
                category="DSA",
                topic="Coding Interviews",
                difficulty="Intermediate",
                semantic_tags="dsa,interview,programming,humor",
                educational_value=0.6,
                hype_score=0.15
            ),
            ReelItem(
                reel_id="TRAP_04",
                title="MacBook vs Dell: Best Laptop for Developers",
                category="Hardware",
                topic="Developer Hardware",
                difficulty="Intermediate",
                semantic_tags="hardware,laptop,developer,workstation",
                educational_value=0.7,
                hype_score=0.2
            ),
            ReelItem(
                reel_id="TRAP_05",
                title="Why Backend Engineers Care About Latency",
                category="Backend",
                topic="Backend Performance",
                difficulty="Intermediate",
                semantic_tags="backend,performance,software-engineering,latency",
                educational_value=0.9,
                hype_score=0.05
            )
        ]

        # Preset 2: Gaming & Hardware Systems
        gaming_reels = [
            ReelItem(
                reel_id="GAME_01",
                title="RTX 4090 vs 5090: Architecture Deep Dive",
                category="Hardware",
                topic="GPU Architecture",
                difficulty="Intermediate",
                semantic_tags="gpu,hardware,nvidia,graphics,architecture",
                educational_value=0.88,
                hype_score=0.1
            ),
            ReelItem(
                reel_id="GAME_02",
                title="Building a Custom Liquid-Cooled Gaming Rig",
                category="Hardware",
                topic="PC Building",
                difficulty="Intermediate",
                semantic_tags="hardware,pc-building,cooling,custom-pc",
                educational_value=0.82,
                hype_score=0.15
            ),
            ReelItem(
                reel_id="GAME_03",
                title="Game Engine Optimization: Frame Times & Shaders",
                category="Hardware",
                topic="Game Optimization",
                difficulty="Advanced",
                semantic_tags="graphics,rendering,optimization,shaders,performance",
                educational_value=0.92,
                hype_score=0.05
            ),
            ReelItem(
                reel_id="GAME_04",
                title="DirectX 12 vs Vulkan: Low-Level GPU APIs",
                category="Hardware",
                topic="Graphics Settings",
                difficulty="Advanced",
                semantic_tags="vulkan,directx,gpu,low-level,systems",
                educational_value=0.94,
                hype_score=0.04
            )
        ]

        # Preset 3: AI Engineering / Production AI
        ai_reels = [
            ReelItem(
                reel_id="AI_01",
                title="RAG Architecture: Chunking Strategies That Work",
                category="AI",
                topic="RAG",
                difficulty="Intermediate",
                semantic_tags="ai,rag,llm,retrieval,embeddings",
                educational_value=0.95,
                hype_score=0.05
            ),
            ReelItem(
                reel_id="AI_02",
                title="Autonomous AI Agents with Tool Calling",
                category="AI",
                topic="AI Agents",
                difficulty="Intermediate",
                semantic_tags="ai,agents,llm,function-calling,reasoning",
                educational_value=0.94,
                hype_score=0.06
            ),
            ReelItem(
                reel_id="AI_03",
                title="Vector Database Indexing: HNSW vs IVF",
                category="AI",
                topic="Vector Databases",
                difficulty="Advanced",
                semantic_tags="ai,vector-search,databases,indexing,hnsw",
                educational_value=0.96,
                hype_score=0.03
            ),
            ReelItem(
                reel_id="AI_04",
                title="LLM Evaluation: Moving Beyond Vibe Checks",
                category="AI",
                topic="Model Evaluation",
                difficulty="Advanced",
                semantic_tags="ai,evaluation,benchmarks,production,reliability",
                educational_value=0.95,
                hype_score=0.04
            )
        ]

        # Preset 4: Python & Data Engineering
        data_reels = [
            ReelItem(
                reel_id="DATA_01",
                title="Python Pandas Memory Optimization for Large Datasets",
                category="Python",
                topic="Pandas",
                difficulty="Intermediate",
                semantic_tags="python,pandas,data-engineering,memory,optimization",
                educational_value=0.92,
                hype_score=0.04
            ),
            ReelItem(
                reel_id="DATA_02",
                title="Automating Excel Reports with Python & OpenPyXL",
                category="Python",
                topic="Automation",
                difficulty="Beginner",
                semantic_tags="python,automation,excel,reporting,productivity",
                educational_value=0.85,
                hype_score=0.08
            ),
            ReelItem(
                reel_id="DATA_03",
                title="Building Production ETL Pipelines with Polars & DuckDB",
                category="Python",
                topic="Data Engineering",
                difficulty="Intermediate",
                semantic_tags="python,polars,duckdb,etl,data-pipelines",
                educational_value=0.94,
                hype_score=0.04
            ),
            ReelItem(
                reel_id="DATA_04",
                title="Interactive Data Visualizations with Plotly",
                category="Python",
                topic="Data Visualization",
                difficulty="Beginner",
                semantic_tags="python,plotly,visualization,dashboards,analytics",
                educational_value=0.88,
                hype_score=0.05
            )
        ]

        # Preset 5: Viral Hype Mix
        hype_reels = [
            ReelItem(
                reel_id="HYPE_01",
                title="How to Use 10 AI Tools to Get Rich",
                category="Career",
                topic="AI Tools",
                difficulty="Beginner",
                semantic_tags="ai,career,hype,clickbait,money",
                educational_value=0.18,
                hype_score=0.96
            ),
            ReelItem(
                reel_id="HYPE_02",
                title="Become a Software Engineer in 7 Days",
                category="Career",
                topic="Career hype",
                difficulty="Beginner",
                semantic_tags="career,hype,fast-track",
                educational_value=0.12,
                hype_score=0.98
            ),
            ReelItem(
                reel_id="HYPE_03",
                title="Secret Prompt That Makes Gemini Do Your Job",
                category="AI",
                topic="Prompt hype",
                difficulty="Beginner",
                semantic_tags="ai,prompting,hype,shortcuts",
                educational_value=0.25,
                hype_score=0.92
            )
        ]

        # Preset 6: Single Ambiguous Interaction
        ambiguous_reels = [
            ReelItem(
                reel_id="AMB_01",
                title="Cool Tech Gadget You Didn't Know Existed",
                category="Gadgets",
                topic="Consumer Tech",
                difficulty="Beginner",
                semantic_tags="gadgets,consumer,random",
                educational_value=0.4,
                hype_score=0.3
            )
        ]

        # Return dictionary of all presets with 8-Reel Default History first
        return {
            "Default History (8 Reels from CSV)": self.interaction_history,
            "Test 1: Built-in Trap (Java/SWE/Interview/Laptop -> System Design)": trap_reels,
            "Test 2: Gaming & Hardware Systems": gaming_reels,
            "Test 3: AI Engineering & Agents": ai_reels,
            "Test 4: Python & Data Engineering": data_reels,
            "Test 5: Viral Hype Mixture": hype_reels,
            "Test 6: Single Ambiguous Interaction (Low Confidence)": ambiguous_reels
        }
