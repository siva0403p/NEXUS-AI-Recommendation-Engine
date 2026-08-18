"""
NEXUS - Explainability Engine
Generates clear, evidence-grounded justifications for every recommendation,
explaining WHY interest was inferred, WHY the specific reel was recommended,
and WHY viral hype candidates were suppressed.
"""

from typing import List, Dict, Optional
from models.schemas import (
    ReelItem,
    ReelAnalysis,
    LatentInterestResult,
    NextSkillInference,
    ScoredCandidate,
    RecommendationOutput
)
from services.gemini_service import GeminiService


class ExplanationEngine:
    """Produces human-interpretable, evidence-based recommendation justifications."""

    def __init__(self, gemini_service: Optional[GeminiService] = None):
        self.gemini = gemini_service or GeminiService()

    def build_recommendation_output(
        self,
        winning_candidate: ScoredCandidate,
        latent_interest: LatentInterestResult,
        next_skill: NextSkillInference,
        watched_reels: List[ReelItem],
        analyses: List[ReelAnalysis],
        confidence_label: str,
        confidence_reason: str,
        rejected_candidate: Optional[ScoredCandidate] = None,
        shortlisted_candidates: Optional[List[ScoredCandidate]] = None
    ) -> RecommendationOutput:
        """
        Synthesizes the complete authoritative RecommendationOutput object.
        """
        # 1. Format Current Reel reference
        if watched_reels:
            titles = [f"'{r.title}'" for r in watched_reels]
            if len(titles) == 1:
                current_ref = f"{titles[0]} ({watched_reels[0].category})"
            elif len(titles) <= 3:
                current_ref = f"{', '.join(titles[:-1])} and {titles[-1]}"
            else:
                current_ref = f"{', '.join(titles[:2])}, and {len(titles)-2} other reels"
        else:
            current_ref = "No prior interaction history"

        # 2. Build WHY explanation (Evidence for Latent Interest)
        observed_titles = [f"'{r.title}'" for r in watched_reels[:4]]
        if len(watched_reels) >= 3:
            why_evidence = (
                f"The {', '.join(observed_titles)} share a broader '{latent_interest.primary_latent_interest}' signal. "
                f"Rather than treating these as disconnected surface clips, NEXUS detects recurring concepts in "
                f"{', '.join(list(latent_interest.semantic_clusters.keys())[:3])} and extracts the underlying technological intent."
            )
        elif len(watched_reels) == 1:
            why_evidence = (
                f"Based on a single interaction with '{watched_reels[0].title}', early signals suggest "
                f"curiosity in {latent_interest.primary_latent_interest}, though confidence remains tentative."
            )
        else:
            why_evidence = f"Interaction patterns consistently indicate {latent_interest.primary_latent_interest}."

        # 3. Build WHY THIS RECOMMENDATION explanation
        why_rec = (
            f"Connects to your latent interest in {latent_interest.primary_latent_interest} by advancing "
            f"to the next high-leverage skill: '{next_skill.next_skill}'. '{winning_candidate.reel.title}' "
            f"provides deep educational value ({winning_candidate.educational_value}/100) and zero clickbait hype, "
            f"empowering practical mastery beyond surface-level syntax."
        )

        # 4. Build WHY NOT THIS explanation (for suppressed hype candidate)
        why_not_this = None
        if rejected_candidate:
            why_not_this = (
                f"Candidate '{rejected_candidate.reel.title}' (Category: {rejected_candidate.reel.category}) "
                f"was evaluated due to high keyword/semantic proximity, but was SUPPRESSED by the NEXUS Quality Gate. "
                f"Reason: Hype score of {rejected_candidate.reel.hype_score:.2f} and low educational depth "
                f"({rejected_candidate.reel.educational_value:.2f}) indicate sensationalized clickbait."
            )

        # 5. Build Interest Bridge progression steps
        bridge_steps = [
            f"Surface Interactions: {', '.join([r.category for r in watched_reels[:4]])}",
            f"Semantic Concepts: {', '.join(list(latent_interest.semantic_clusters.keys())[:3])}",
            f"Latent Interest: {latent_interest.primary_latent_interest}",
            f"Next Skill Progression: {next_skill.next_skill}",
            f"Target Recommendation: {winning_candidate.reel.title} ({winning_candidate.reel.category})"
        ]

        # 6. Score Breakdown Dictionary
        score_breakdown = {
            "Semantic Relevance": winning_candidate.semantic_relevance,
            "Interest Alignment": winning_candidate.interest_alignment,
            "Novelty": winning_candidate.novelty,
            "Educational Value": winning_candidate.educational_value,
            "Difficulty Fit": winning_candidate.difficulty_fit,
            "Hype Penalty": winning_candidate.hype_penalty,
            "Redundancy Penalty": winning_candidate.redundancy_penalty,
            "Final NEXUS Score": winning_candidate.nexus_score
        }

        return RecommendationOutput(
            current_reel_reference=current_ref,
            interest_detected=latent_interest.primary_latent_interest,
            why_evidence=why_evidence,
            recommended_tech_reel=winning_candidate.reel,
            category=winning_candidate.reel.category,
            why_this_recommendation=why_rec,
            difficulty=winning_candidate.reel.difficulty,
            confidence=f"{confidence_label} ({confidence_reason})",
            nexus_score=winning_candidate.nexus_score,
            score_breakdown=score_breakdown,
            rejected_candidate=rejected_candidate,
            why_not_this=why_not_this,
            bridge_steps=bridge_steps,
            shortlisted_candidates=shortlisted_candidates or []
        )
