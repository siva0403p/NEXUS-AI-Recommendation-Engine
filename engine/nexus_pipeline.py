"""
NEXUS - Pipeline Orchestrator
Master coordinator executing the complete end-to-end NEXUS recommendation pipeline:
Watched Reels -> AI Content Understanding -> Latent Interest Engine -> Interest Bridge
-> Next-Skill Inference -> Semantic Retrieval -> Quality/Hype Gate -> Multi-Objective Ranking
-> Confidence Calculation -> Explainable Output.
"""

from typing import List, Optional, Tuple, Dict
from models.schemas import (
    ReelItem,
    ReelAnalysis,
    LatentInterestResult,
    NextSkillInference,
    ScoredCandidate,
    RecommendationOutput
)
from services.gemini_service import GeminiService
from services.data_loader import DataLoader
from engine.ai_analyzer import AIContentAnalyzer
from engine.interest_engine import LatentInterestEngine
from engine.next_skill_engine import NextSkillEngine
from engine.embedding_engine import EmbeddingEngine
from engine.retrieval_engine import RetrievalEngine
from engine.quality_engine import QualityEngine
from engine.ranking_engine import RankingEngine
from engine.confidence_engine import ConfidenceEngine
from engine.explanation_engine import ExplanationEngine


class NexusPipeline:
    """Master pipeline managing end-to-end analysis, ranking, and recommendation."""

    def __init__(self, api_key: Optional[str] = None):
        self.data_loader = DataLoader()
        self.gemini_service = GeminiService(api_key=api_key)

        # Initialize engine modules
        self.ai_analyzer = AIContentAnalyzer(self.gemini_service)
        self.interest_engine = LatentInterestEngine(self.gemini_service)
        self.next_skill_engine = NextSkillEngine(self.gemini_service)
        self.embedding_engine = EmbeddingEngine(self.gemini_service)
        self.retrieval_engine = RetrievalEngine(self.embedding_engine)
        self.quality_engine = QualityEngine()
        self.ranking_engine = RankingEngine(quality_engine=self.quality_engine)
        self.confidence_engine = ConfidenceEngine()
        self.explanation_engine = ExplanationEngine(self.gemini_service)

        # Index candidates into embedding cache
        self.embedding_engine.build_corpus_index(self.data_loader.candidate_reels)

    def set_api_key(self, api_key: str):
        """Updates API key across all sub-services."""
        self.gemini_service.update_api_key(api_key)
        self.embedding_engine.build_corpus_index(self.data_loader.candidate_reels)

    def run(
        self,
        watched_reels: List[ReelItem],
        candidates: Optional[List[ReelItem]] = None,
        negative_candidates: Optional[List[ReelItem]] = None
    ) -> Tuple[RecommendationOutput, LatentInterestResult, NextSkillInference, List[ReelAnalysis]]:
        """
        Executes the full NEXUS recommendation pipeline on a sequence of watched reels.
        """
        candidate_pool = candidates if candidates is not None else self.data_loader.candidate_reels
        negative_pool = negative_candidates if negative_candidates is not None else self.data_loader.negative_candidates

        # Step 1: AI Content Understanding per watched reel
        analyses = self.ai_analyzer.analyze_batch(watched_reels)

        # Step 2: Latent Interest Engine
        latent_interest = self.interest_engine.infer_latent_interest(analyses, watched_reels)

        # Step 3: Next-Skill Engine
        next_skill = self.next_skill_engine.infer_next_skill(latent_interest, analyses)

        # Step 4: Semantic Query Formulation & Retrieval
        query = self.retrieval_engine.build_query_representation(latent_interest, next_skill, analyses)
        candidate_pairs = self.retrieval_engine.retrieve_candidates(
            query=query,
            candidates=candidate_pool,
            watched_reels=watched_reels,
            top_k=12
        )

        # Step 5: Multi-Objective NEXUS Ranking
        scored_candidates = self.ranking_engine.rank_candidates(
            candidate_pairs=candidate_pairs,
            latent_interest=latent_interest,
            next_skill=next_skill,
            watched_reels=watched_reels,
            analyses=analyses
        )

        # Pick the top unsuppressed winning candidate
        unsuppressed = [c for c in scored_candidates if not c.is_suppressed]
        if unsuppressed:
            winning_candidate = unsuppressed[0]
        elif scored_candidates:
            winning_candidate = scored_candidates[0]
        else:
            # Fallback if no candidate available
            dummy_reel = ReelItem(
                reel_id="T_FALLBACK",
                title="System Design Fundamentals",
                category="HLD",
                topic="System Design",
                difficulty="Intermediate",
                educational_value=0.9,
                hype_score=0.05
            )
            winning_candidate = ScoredCandidate(
                reel=dummy_reel,
                semantic_relevance=88.0,
                interest_alignment=92.0,
                novelty=85.0,
                educational_value=90.0,
                difficulty_fit=90.0,
                hype_penalty=1.0,
                redundancy_penalty=0.0,
                nexus_score=89.5,
                is_suppressed=False
            )

        # Step 6: Identify Hype Contrast Candidate ("Why Not This?")
        rejected_item = self.quality_engine.find_suppressed_hype_contrast(
            negative_candidates=negative_pool,
            candidate_reels=candidate_pool,
            latent_interest=latent_interest,
            next_skill=next_skill
        )
        rejected_scored = None
        if rejected_item:
            # Compute score and suppression reason for contrast
            rejected_sim = self.embedding_engine.compute_similarity(query, rejected_item)
            rejected_scored = self.ranking_engine.score_candidate(
                candidate=rejected_item,
                raw_semantic_sim=rejected_sim,
                latent_interest=latent_interest,
                next_skill=next_skill,
                watched_reels=watched_reels,
                analyses=analyses
            )
            # Ensure it is flagged as suppressed for display
            rejected_scored.is_suppressed = True
            if not rejected_scored.suppression_reason:
                rejected_scored.suppression_reason = (
                    f"Suppressed by Quality Gate: Elevated hype score ({rejected_item.hype_score:.2f}) "
                    f"and low educational depth ({rejected_item.educational_value:.2f})."
                )

        # Step 7: Calculate Evidence-Based Confidence
        conf_label, conf_score, conf_reason = self.confidence_engine.compute_confidence(
            watched_reels=watched_reels,
            analyses=analyses,
            latent_interest=latent_interest
        )

        # Step 8: Construct Explainable Output
        output = self.explanation_engine.build_recommendation_output(
            winning_candidate=winning_candidate,
            latent_interest=latent_interest,
            next_skill=next_skill,
            watched_reels=watched_reels,
            analyses=analyses,
            confidence_label=conf_label,
            confidence_reason=conf_reason,
            rejected_candidate=rejected_scored,
            shortlisted_candidates=scored_candidates[:6]
        )

        return output, latent_interest, next_skill, analyses
