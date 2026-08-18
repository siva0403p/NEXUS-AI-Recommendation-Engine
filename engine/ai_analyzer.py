"""
NEXUS - AI Content Analyzer
Analyzes individual watched Reels and extracts rich structured semantic signals
(topic, context, intent, semantic_concepts, interest_signals, skill_signals,
educational value, and hype score).
"""

from typing import List, Dict, Optional
import json
import re
from pathlib import Path

from models.schemas import ReelItem, ReelAnalysis
from services.gemini_service import GeminiService
from config import ANALYSIS_CACHE_PATH, CATEGORY_TAXONOMY


class AIContentAnalyzer:
    """Extracts deep structured semantic understanding from Reels."""

    def __init__(self, gemini_service: Optional[GeminiService] = None):
        self.gemini = gemini_service or GeminiService()
        self.cache: Dict[str, dict] = {}
        self._load_cache()

    def _load_cache(self):
        """Loads persistent analysis cache to avoid repeated LLM calls."""
        if ANALYSIS_CACHE_PATH.exists():
            try:
                with open(ANALYSIS_CACHE_PATH, "r", encoding="utf-8") as f:
                    self.cache = json.load(f)
            except Exception:
                self.cache = {}

    def _save_cache(self):
        """Persists analysis cache."""
        try:
            with open(ANALYSIS_CACHE_PATH, "w", encoding="utf-8") as f:
                json.dump(self.cache, f, indent=2)
        except Exception:
            pass

    def analyze_reel(self, reel: ReelItem) -> ReelAnalysis:
        """
        Analyzes a single reel, using Gemini structured generation when available,
        or deterministic semantic concept extraction with high-fidelity taxonomy.
        """
        cache_key = f"{reel.reel_id}_{reel.title}"
        if cache_key in self.cache:
            try:
                return ReelAnalysis.model_validate(self.cache[cache_key])
            except Exception:
                pass

        # 1. Try Gemini Structured Output if available
        if self.gemini.is_available():
            prompt = f"""
You are an expert AI Content Understanding Engine for NEXUS.
Analyze this short-form technology reel and extract its deep semantic signals.

REEL METADATA:
- ID: {reel.reel_id}
- Title: "{reel.title}"
- Category: "{reel.category}"
- Topic: "{reel.topic}"
- Tags: "{reel.semantic_tags}"
- Stated Difficulty: "{reel.difficulty}"

INSTRUCTIONS:
1. Do NOT just repeat the title or surface language.
2. Identify broader engineering and computer science concepts behind the content.
   (e.g., A "Java meme about semicolons" indicates Developer Culture, Programming Syntax, and Software Engineering).
   (e.g., "MacBook vs Dell" indicates Developer Workstations, Hardware, and Engineering Productivity).
3. Identify viewer intent (e.g. entertainment, learning, career insight, tool evaluation).
4. Extract latent interest signals and skill signals.
5. Score educational depth (0.0 to 1.0) and hype/clickbait level (0.0 to 1.0).
"""
            analysis = self.gemini.generate_structured(
                prompt=prompt,
                response_schema=ReelAnalysis,
                system_instruction="You are NEXUS Semantic Engine. Extract objective, structured semantic signals from technical reels."
            )
            if analysis:
                self.cache[cache_key] = analysis.model_dump()
                self._save_cache()
                return analysis

        # 2. Resilient Deterministic Semantic Extraction (Offline / Fallback)
        analysis = self._deterministic_analysis(reel)
        self.cache[cache_key] = analysis.model_dump()
        self._save_cache()
        return analysis

    def _deterministic_analysis(self, reel: ReelItem) -> ReelAnalysis:
        """
        High-fidelity deterministic semantic extraction mapping surface features
        to broader computer science concepts and interest domains.
        """
        title_lower = reel.title.lower()
        cat_lower = reel.category.lower()
        topic_lower = reel.topic.lower()
        tags_lower = reel.semantic_tags.lower()
        full_text = f"{title_lower} {cat_lower} {topic_lower} {tags_lower}"

        concepts = set()
        interest_signals = set()
        skill_signals = set()

        # Semantic concept mapping rules
        if any(w in full_text for w in ["java", "jvm", "semicolon", "spring", "concurrency", "thread"]):
            concepts.update(["Object-Oriented Programming", "Java Runtime", "Type Safety", "Software Architecture"])
            interest_signals.update(["Software Engineering", "Backend Development", "Programming Languages"])
            skill_signals.update(["Java", "OOP", "Debugging"])

        if any(w in full_text for w in ["lifestyle", "day in", "sf", "developer", "engineer", "career", "salary"]):
            concepts.update(["Developer Culture", "Engineering Practices", "Software Industry"])
            interest_signals.update(["Software Engineering", "Tech Careers", "Engineering Workflow"])
            skill_signals.update(["Workplace Navigation", "Engineering Mindset"])

        if any(w in full_text for w in ["interview", "fizzbuzz", "dsa", "leetcode", "algorithm", "binary search", "graphs", "tree"]):
            concepts.update(["Algorithm Design", "Computational Complexity", "Technical Problem Solving"])
            interest_signals.update(["Software Engineering", "Algorithms & Data Structures", "Interview Prep"])
            skill_signals.update(["Problem Solving", "DSA", "Code Optimization"])

        if any(w in full_text for w in ["macbook", "dell", "laptop", "gpu", "hardware", "cpu", "rig", "cooling", "vulkan", "directx", "graphics"]):
            concepts.update(["Computer Systems Architecture", "Developer Hardware", "Graphics & Systems Performance"])
            interest_signals.update(["Computer Systems & Hardware", "Gaming Technology", "Workstation Optimization"])
            skill_signals.update(["Hardware Evaluation", "System Architecture"])

        if any(w in full_text for w in ["latency", "backend", "api", "rest", "microservices", "distributed", "caching", "scaling", "sharding"]):
            concepts.update(["Distributed Systems", "Backend Scalability", "Performance Optimization", "High-Level Design"])
            interest_signals.update(["Software Engineering", "High-Level System Design", "Backend Systems"])
            skill_signals.update(["System Architecture", "API Design", "Distributed Systems"])

        if any(w in full_text for w in ["python", "pandas", "excel", "automation", "polars", "duckdb", "etl"]):
            concepts.update(["Data Processing", "Scripting & Automation", "ETL Pipelines", "Data Analysis"])
            interest_signals.update(["Data Engineering", "Python Development", "Data Analytics"])
            skill_signals.update(["Python", "Data Wrangling", "Workflow Automation"])

        if any(w in full_text for w in ["rag", "llm", "ai agent", "vector", "embedding", "prompt", "neural"]):
            concepts.update(["Large Language Models", "Information Retrieval", "AI Systems Architecture", "Vector Search"])
            interest_signals.update(["Artificial Intelligence", "AI Engineering", "Machine Learning Systems"])
            skill_signals.update(["RAG", "LLM Orchestration", "Vector Databases"])

        # Determine Context & Intent
        if any(w in full_text for w in ["meme", "joke", "fail", "rich", "secret", "guarantee"]):
            context = "Humor & Social Commentary" if "meme" in full_text or "joke" in full_text else "Clickbait Promotion"
            intent = "Entertainment" if "meme" in full_text or "joke" in full_text else "Shortcuts & Career Hype"
        elif any(w in full_text for w in ["deep dive", "internals", "architecture", "scale", "optimization"]):
            context = "Technical Deep Dive"
            intent = "In-Depth Engineering Skill Acquisition"
        else:
            context = "Educational Tech Tutorial"
            intent = "Skill Exploration"

        # Determine broad domain interest from category taxonomy
        domain = CATEGORY_TAXONOMY.get(reel.category, "Technology & Engineering")
        interest_signals.add(domain)

        # Fallbacks for empty sets
        if not concepts:
            concepts.add(reel.topic)
            concepts.add(f"{reel.category} Concepts")
        if not interest_signals:
            interest_signals.add(domain)
        if not skill_signals:
            skill_signals.add(reel.topic)

        # Hype & Educational value calculation
        hype = reel.hype_score
        edu = reel.educational_value

        return ReelAnalysis(
            reel_id=reel.reel_id,
            title=reel.title,
            topic=reel.topic,
            surface_category=reel.category,
            context=context,
            intent=intent,
            semantic_concepts=sorted(list(concepts)),
            interest_signals=sorted(list(interest_signals)),
            skill_signals=sorted(list(skill_signals)),
            difficulty=reel.difficulty,
            educational_value=edu,
            hype_score=hype,
            confidence=0.92
        )

    def analyze_batch(self, reels: List[ReelItem]) -> List[ReelAnalysis]:
        """Analyzes a collection of watched reels."""
        return [self.analyze_reel(r) for r in reels]
