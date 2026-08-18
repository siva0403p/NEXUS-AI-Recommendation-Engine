"""
NEXUS - Candidate Retrieval Engine
Constructs unified semantic query representations and performs semantic retrieval
over the candidate technology corpus while excluding watched and redundant items.
"""

from typing import List, Tuple, Set, Optional
from models.schemas import ReelItem, LatentInterestResult, NextSkillInference, ReelAnalysis
from engine.embedding_engine import EmbeddingEngine
from config import TOP_K_CANDIDATES


class RetrievalEngine:
    """Performs semantic candidate retrieval over candidate reel catalog."""

    def __init__(self, embedding_engine: EmbeddingEngine):
        self.embedding_engine = embedding_engine

    def build_query_representation(
        self,
        latent_interest: LatentInterestResult,
        next_skill: NextSkillInference,
        analyses: List[ReelAnalysis]
    ) -> str:
        """
        Synthesizes a rich semantic query vector representation balancing
        latent interest domain, target next-skill progression, and key concepts.
        """
        concepts = set()
        for a in analyses:
            for c in a.semantic_concepts:
                concepts.add(c)

        concept_str = " ".join(list(concepts)[:8])
        adjacent_str = " ".join(next_skill.adjacent_skills)

        # Primary emphasis is on the next skill progression aligned with the latent interest
        query = (
            f"Target Skill: {next_skill.next_skill}. "
            f"Category: {next_skill.target_category}. "
            f"Domain Interest: {latent_interest.primary_latent_interest}. "
            f"Related Topics: {adjacent_str}. "
            f"Foundational Concepts: {concept_str}."
        )
        return query

    def retrieve_candidates(
        self,
        query: str,
        candidates: List[ReelItem],
        watched_reels: List[ReelItem],
        top_k: int = TOP_K_CANDIDATES
    ) -> List[Tuple[ReelItem, float]]:
        """
        Retrieves top_k un-watched candidate reels ranked by raw semantic similarity.
        """
        watched_ids: Set[str] = {r.reel_id.strip() for r in watched_reels}
        watched_titles: Set[str] = {r.title.strip().lower() for r in watched_reels}

        # Filter out already-watched reels
        eligible_candidates = [
            c for c in candidates
            if c.reel_id.strip() not in watched_ids
            and c.title.strip().lower() not in watched_titles
        ]

        if not eligible_candidates:
            return []

        # Compute semantic similarities
        similarities = self.embedding_engine.compute_batch_similarities(query, eligible_candidates)

        # Pair and sort
        scored_pairs = list(zip(eligible_candidates, similarities))
        scored_pairs.sort(key=lambda x: x[1], reverse=True)

        return scored_pairs[:top_k]
