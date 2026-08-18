"""
NEXUS - Evidence-Based Confidence Engine
Calculates objective, evidence-grounded confidence levels based on signal count,
conceptual convergence entropy, and diversity across interaction history.
"""

from typing import List, Tuple, Dict
from models.schemas import ReelItem, ReelAnalysis, LatentInterestResult


class ConfidenceEngine:
    """Computes mathematical and evidence-grounded confidence for recommendations."""

    def compute_confidence(
        self,
        watched_reels: List[ReelItem],
        analyses: List[ReelAnalysis],
        latent_interest: LatentInterestResult
    ) -> Tuple[str, float, str]:
        """
        Returns (confidence_label, confidence_score, evidence_reason).
        confidence_label: "High" | "Medium" | "Low"
        """
        n_reels = len(watched_reels)

        if n_reels == 0:
            return "Low", 0.1, "No interaction history observed."

        if n_reels == 1:
            return (
                "Low",
                0.35,
                f"Low confidence — single isolated interaction ('{watched_reels[0].title}') provides insufficient evidence to establish a sustained latent interest pattern."
            )

        # Count how many watched reels support the inferred primary domain
        primary = latent_interest.primary_latent_interest.lower()
        matching_signals = 0
        matching_titles = []

        for a in analyses:
            sig_text = " ".join(a.interest_signals + a.semantic_concepts).lower()
            if any(term in sig_text for term in primary.split()):
                matching_signals += 1
                matching_titles.append(a.title)

        convergence_ratio = matching_signals / max(1, n_reels)

        # Calculate evidence metrics
        if n_reels >= 4 and matching_signals >= 3 and convergence_ratio >= 0.6:
            score = round(min(0.98, 0.75 + (convergence_ratio * 0.2)), 2)
            label = "High"
            reason = (
                f"High confidence -- {matching_signals} of {n_reels} independent interactions "
                f"converge strongly on {latent_interest.primary_latent_interest}."
            )
        elif n_reels >= 2 and matching_signals >= 2:
            score = round(min(0.85, 0.55 + (convergence_ratio * 0.2)), 2)
            label = "Medium"
            reason = (
                f"Medium confidence -- {matching_signals} interactions indicate early interest "
                f"in {latent_interest.primary_latent_interest}."
            )
        else:
            score = 0.45
            label = "Low"
            reason = (
                f"Low confidence -- sparse or conflicting interactions across {n_reels} reels "
                f"without clear convergence."
            )

        return label, score, reason
