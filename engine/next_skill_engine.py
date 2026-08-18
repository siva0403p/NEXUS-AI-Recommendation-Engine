"""
NEXUS - Next-Skill Inference Engine
Determines the logical technological progression and recommends an adjacent,
high-leverage engineering skill rather than repeating watched surface topics.
"""

from typing import List, Dict, Optional
from models.schemas import LatentInterestResult, ReelAnalysis, NextSkillInference
from services.gemini_service import GeminiService


class NextSkillEngine:
    """Infers the optimal next technology skill to learn based on latent interests and current mastery."""

    def __init__(self, gemini_service: Optional[GeminiService] = None):
        self.gemini = gemini_service or GeminiService()

    def infer_next_skill(
        self,
        latent_interest: LatentInterestResult,
        analyses: List[ReelAnalysis]
    ) -> NextSkillInference:
        """
        Infers the next technological skill using Gemini when available,
        or domain pedagogical progression mapping.
        """
        # 1. Try Gemini Structured Inference
        if self.gemini.is_available():
            llm_result = self._infer_with_gemini(latent_interest, analyses)
            if llm_result:
                return llm_result

        # 2. Heuristic Domain Progression Mapping
        return self._heuristic_progression(latent_interest, analyses)

    def _infer_with_gemini(
        self,
        latent_interest: LatentInterestResult,
        analyses: List[ReelAnalysis]
    ) -> Optional[NextSkillInference]:
        """Generates structured next-skill recommendation via Gemini."""
        prompt = f"""
You are the NEXUS Next-Skill Engine.
A student has demonstrated a primary latent interest in: "{latent_interest.primary_latent_interest}"
Secondary interests: {', '.join(latent_interest.secondary_latent_interests)}

Observed content topics & concepts:
{', '.join([f"{a.topic} ({a.surface_category})" for a in analyses])}

YOUR TASK:
Determine what technology skill SHOULD COME NEXT in their engineering journey.
Do NOT just recommend the exact same language or surface topic they watched.
Recommend an adjacent, higher-value technological skill (e.g. if they know Java syntax, coding interviews, and backend basics, recommend System Design / High-Level Architecture).
If they know Python automation and Pandas, recommend Data Engineering.
If they know LLMs and RAG, recommend Production AI / Evaluation.
If they know GPUs and gaming hardware, recommend GPU Programming & Computer Systems.
"""
        return self.gemini.generate_structured(
            prompt=prompt,
            response_schema=NextSkillInference,
            system_instruction="Infer the adjacent next technology skill in the student's learning progression."
        )

    def _heuristic_progression(
        self,
        latent_interest: LatentInterestResult,
        analyses: List[ReelAnalysis]
    ) -> NextSkillInference:
        """
        Curated pedagogical progression pathways for technical disciplines.
        """
        primary = latent_interest.primary_latent_interest.lower()
        all_concepts = [c.lower() for a in analyses for c in a.semantic_concepts]
        all_topics = [a.topic.lower() for a in analyses]

        # Case 1: AI / LLMs / Agents
        if any(term in primary for term in ["artificial intelligence", "ai engineering", "machine learning", "rag", "agent"]) or (primary == "ai"):
            return NextSkillInference(
                next_skill="Production AI Systems & LLM Evaluation",
                target_category="AI",
                reason=(
                    "Observed interest in prompt engineering, RAG, and AI agents. "
                    "The next professional leap is production-grade AI engineering: benchmark evaluation, "
                    "guardrails, vector indexing scalability, and latency optimization."
                ),
                adjacent_skills=["Vector Index Optimization", "Agent Tool Calling Architecture", "Fine-Tuning & Quantization"],
                learning_path_stage="Production AI Engineering",
                confidence="High"
            )

        # Case 2: Gaming Technology / Hardware / Systems
        elif any(term in primary for term in ["hardware", "gaming", "systems", "gpu"]):
            return NextSkillInference(
                next_skill="Computer Systems & Low-Level Architecture",
                target_category="Hardware",
                reason=(
                    "Observed interest in GPUs, PC hardware, and graphics performance. "
                    "Progression advances to understanding computer architecture, memory hierarchies, "
                    "and low-level hardware optimizations."
                ),
                adjacent_skills=["GPU Compute & CUDA", "Low-Level Systems Programming", "Operating Systems Internals"],
                learning_path_stage="Systems Engineering",
                confidence="High"
            )

        # Case 3: Data Engineering / Python / Analytics
        elif any(term in primary for term in ["data", "analytics", "etl", "pandas"]) or ("python" in primary and "software" not in primary):
            return NextSkillInference(
                next_skill="Data Engineering & Pipeline Scalability",
                target_category="Python",
                reason=(
                    "Observed scripting, automation, and exploratory pandas workflows. "
                    "The adjacent high-value competency is modern data engineering: scalable data pipelines, "
                    "Polars/DuckDB execution, and streaming data transformations."
                ),
                adjacent_skills=["ETL Pipeline Architecture", "Distributed Dataframes", "Data Warehousing", "Stream Processing"],
                learning_path_stage="Data Engineering Mastery",
                confidence="High"
            )

        # Case 4: Software Engineering / Java / Backend / DSA
        elif any(term in primary for term in ["software engineering", "programming", "backend", "java", "dsa"]):
            return NextSkillInference(
                next_skill="System Design & High-Level Architecture",
                target_category="HLD",
                reason=(
                    "Student demonstrates solid grasp of coding syntax, interviews, and developer workflow. "
                    "The natural high-leverage progression is moving from component implementation to "
                    "distributed systems, caching, load balancing, and high-level architectural design."
                ),
                adjacent_skills=["Distributed Systems", "Database Sharding", "Microservices Architecture", "API Reliability"],
                learning_path_stage="Architectural Mastery",
                confidence="High"
            )

        # Default fallback progression
        return NextSkillInference(
            next_skill="Software Architecture & Best Practices",
            target_category="HLD",
            reason=(
                f"Transitioning from exploratory interactions to structured engineering practices in {latent_interest.primary_latent_interest}."
            ),
            adjacent_skills=["System Design", "Cloud Architecture", "Clean Code & Scaling"],
            learning_path_stage="Engineering Core",
            confidence="Medium"
        )
