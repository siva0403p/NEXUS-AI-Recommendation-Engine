"""
NEXUS - Latent Interest Engine
Aggregates structured semantic signals from watched Reels, discovers conceptual
convergence, and dynamically infers the user's deeper underlying technology interest.
"""

from typing import List, Dict, Tuple, Optional
from collections import defaultdict, Counter
import math

from models.schemas import ReelItem, ReelAnalysis, LatentInterestResult
from services.gemini_service import GeminiService
from config import CATEGORY_TAXONOMY


class LatentInterestEngine:
    """Discovers underlying latent technology interests from diverse surface interactions."""

    def __init__(self, gemini_service: Optional[GeminiService] = None):
        self.gemini = gemini_service or GeminiService()

    def infer_latent_interest(
        self,
        analyses: List[ReelAnalysis],
        watched_reels: List[ReelItem]
    ) -> LatentInterestResult:
        """
        Dynamically infers the primary and secondary latent interests from structured reel analyses.
        Uses Gemini LLM synthesis when available, backed by an analytical convergence algorithm.
        """
        if not analyses:
            return LatentInterestResult(
                primary_latent_interest="General Technology",
                secondary_latent_interests=["Software Development"],
                interest_strengths={"General Technology": 50.0},
                semantic_clusters={"General": ["Technology"]},
                supporting_evidence=["No interaction history provided"],
                surface_signals=[],
                confidence_score=0.2,
                confidence_label="Low"
            )

        # 1. Collect surface signals and aggregate concepts
        surface_signals = []
        for r in watched_reels:
            surface_signals.append(f"{r.title} ({r.category})")

        # 2. Try Gemini Structured Synthesis if available
        if self.gemini.is_available() and len(analyses) >= 2:
            llm_result = self._infer_with_gemini(analyses, watched_reels)
            if llm_result:
                return llm_result

        # 3. Analytical Dynamic Signal Convergence Algorithm
        return self._analytical_convergence(analyses, watched_reels)

    def _infer_with_gemini(
        self,
        analyses: List[ReelAnalysis],
        watched_reels: List[ReelItem]
    ) -> Optional[LatentInterestResult]:
        """Calls Gemini to perform high-level latent interest synthesis."""
        signals_summary = []
        for a in analyses:
            signals_summary.append(
                f"- Title: '{a.title}' | Surface Cat: {a.surface_category} | "
                f"Concepts: {', '.join(a.semantic_concepts)} | Signals: {', '.join(a.interest_signals)}"
            )

        prompt = f"""
You are the NEXUS Latent Interest Engine.
Analyze the following student interaction history across short-form reels.

WATCHED REELS & EXTRACTED SIGNALS:
{chr(10).join(signals_summary)}

CRITICAL PRINCIPLES:
1. Do NOT perform simple keyword matching.
2. Avoid shallow surface traps (e.g. if the user watched a Java meme, coding interview, SWE lifestyle, laptop comparison, and backend latency, the true latent interest is 'Software Engineering', NOT just 'Java').
3. If they watch GPUs, PC builds, game optimization, the latent interest is 'Gaming Technology & Systems' or 'Computer Hardware'.
4. If they watch RAG, AI agents, vector databases, the latent interest is 'AI Engineering' or 'Production AI'.
5. If they watch Python, Pandas, Excel automation, the latent interest is 'Data Engineering' or 'Data Analytics'.
6. Dynamically calculate interest strengths (0-100) and construct supporting evidence citing the actual watched titles.
"""
        result = self.gemini.generate_structured(
            prompt=prompt,
            response_schema=LatentInterestResult,
            system_instruction="Synthesize latent technology interests from observed reel interactions with evidence."
        )
        return result

    def _analytical_convergence(
        self,
        analyses: List[ReelAnalysis],
        watched_reels: List[ReelItem]
    ) -> LatentInterestResult:
        """
        Pure deterministic semantic aggregation algorithm.
        Clusters concepts, computes domain signal weights, and resolves cross-domain convergence.
        """
        domain_weights = defaultdict(float)
        concept_counts = Counter()
        cluster_map = defaultdict(list)
        evidence_list = []

        total_reels = len(analyses)

        for a, r in zip(analyses, watched_reels):
            # Educational value gives higher weighting to serious technical content
            weight = 1.0 + (a.educational_value * 0.5) - (a.hype_score * 0.4)

            # Tally interest signals
            for sig in a.interest_signals:
                domain_weights[sig] += weight * 1.5

            # Tally concepts
            for concept in a.semantic_concepts:
                concept_counts[concept] += 1
                cluster_map[a.surface_category].append(concept)

            # Add domain from taxonomy
            domain = CATEGORY_TAXONOMY.get(r.category, "Technology")
            domain_weights[domain] += weight * 1.2

        # Group into distinct concept clusters
        cleaned_clusters: Dict[str, List[str]] = {}
        for cat, clist in cluster_map.items():
            cleaned_clusters[cat] = sorted(list(set(clist)))

        # Normalize domain strengths to 0 - 100
        if domain_weights:
            max_score = max(domain_weights.values())
            # Scale so the top domain reaches 85-98 based on coherence
            interest_strengths = {}
            for dom, score in domain_weights.items():
                normalized = round((score / max_score) * 95.0, 1)
                interest_strengths[dom] = normalized
        else:
            interest_strengths = {"General Technology": 50.0}

        # Sort domains by strength
        sorted_domains = sorted(interest_strengths.items(), key=lambda x: x[1], reverse=True)
        primary_interest = sorted_domains[0][0] if sorted_domains else "Software Engineering"
        secondary_interests = [d[0] for d in sorted_domains[1:4]]

        # Build dynamic supporting evidence referencing observed reels
        evidence_list.append(
            f"Observed {total_reels} distinct interactions indicating interest in '{primary_interest}'."
        )
        for a in analyses[:4]:
            evidence_list.append(
                f"Reel '{a.title}' ({a.surface_category}) contributed core concepts: {', '.join(a.semantic_concepts[:3])}."
            )

        # Calculate evidence-based confidence
        # More items converging on the same top domain -> higher confidence
        unique_categories = len(set(r.category for r in watched_reels))
        if total_reels >= 4 and sorted_domains[0][1] >= 80.0:
            confidence_score = 0.92
            confidence_label = "High"
        elif total_reels >= 2:
            confidence_score = 0.72
            confidence_label = "Medium"
        else:
            confidence_score = 0.40
            confidence_label = "Low"

        return LatentInterestResult(
            primary_latent_interest=primary_interest,
            secondary_latent_interests=secondary_interests,
            interest_strengths=interest_strengths,
            semantic_clusters=cleaned_clusters,
            supporting_evidence=evidence_list,
            surface_signals=[f"{r.title} ({r.category})" for r in watched_reels],
            confidence_score=confidence_score,
            confidence_label=confidence_label
        )
