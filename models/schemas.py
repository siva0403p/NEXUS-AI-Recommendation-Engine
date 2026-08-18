"""
NEXUS - Data Models & Schemas
Defines all Pydantic schemas for structured AI analysis, latent interest,
next-skill inference, candidate scoring, and explainable recommendations.
"""

from typing import List, Dict, Optional, Any
from pydantic import BaseModel, Field


class ReelItem(BaseModel):
    """Represents a Reel record from interaction history or candidate corpus."""
    reel_id: str = Field(..., description="Unique Reel identifier, e.g. R001, T001, N001")
    title: str = Field(..., description="Title or headline of the reel")
    category: str = Field(..., description="High-level category, e.g. Java, AI, Hardware, Career")
    topic: str = Field(..., description="Specific topic, e.g. JVM Internals, Caching, RAG")
    difficulty: str = Field("Intermediate", description="Difficulty level: Beginner, Intermediate, Advanced")
    semantic_tags: str = Field("", description="Comma-separated semantic tags")
    educational_value: float = Field(0.8, description="Educational quality score from 0.0 to 1.0")
    hype_score: float = Field(0.1, description="Hype/clickbait score from 0.0 to 1.0")
    prerequisites: Optional[str] = Field("", description="Prerequisites for understanding this reel")
    source_type: Optional[str] = Field("candidate", description="Source type: history, candidate, negative")

    @property
    def tag_list(self) -> List[str]:
        if not self.semantic_tags:
            return []
        return [t.strip() for t in self.semantic_tags.split(",") if t.strip()]


class ReelAnalysis(BaseModel):
    """Structured semantic output produced by Gemini for a single watched reel."""
    reel_id: str = Field(..., description="Identifier of the analyzed reel")
    title: str = Field(..., description="Title of the reel")
    topic: str = Field(..., description="Underlying topic identified")
    surface_category: str = Field(..., description="Surface category of the content")
    context: str = Field(..., description="Contextual setting of the reel (e.g. workplace humor, tutorial, opinion)")
    intent: str = Field(..., description="Viewer intent (e.g. entertainment, learning, career insight, tool evaluation)")
    semantic_concepts: List[str] = Field(default_factory=list, description="Broader engineering concepts extracted")
    interest_signals: List[str] = Field(default_factory=list, description="Latent interest domain signals")
    skill_signals: List[str] = Field(default_factory=list, description="Current skills or technical areas demonstrated")
    difficulty: str = Field("Intermediate", description="Assessed difficulty")
    educational_value: float = Field(..., ge=0.0, le=1.0, description="Estimated educational depth score 0-1")
    hype_score: float = Field(..., ge=0.0, le=1.0, description="Estimated sensationalism/hype score 0-1")
    confidence: float = Field(0.9, ge=0.0, le=1.0, description="Confidence in this semantic analysis")


class SemanticCluster(BaseModel):
    """Cluster of related semantic concepts across watched reels."""
    cluster_name: str
    concepts: List[str]
    frequency: int
    relevance_weight: float


class LatentInterestResult(BaseModel):
    """Aggregated output from the Latent Interest Engine."""
    primary_latent_interest: str = Field(..., description="Primary inferred latent interest domain")
    secondary_latent_interests: List[str] = Field(default_factory=list, description="Secondary interest domains")
    interest_strengths: Dict[str, float] = Field(default_factory=dict, description="Calculated strength per interest domain (0-100)")
    semantic_clusters: Dict[str, List[str]] = Field(default_factory=dict, description="Mapped concept clusters")
    supporting_evidence: List[str] = Field(default_factory=list, description="Observable facts from interaction history")
    surface_signals: List[str] = Field(default_factory=list, description="Original surface categories/tags watched")
    confidence_score: float = Field(..., ge=0.0, le=1.0, description="Overall confidence score 0.0 to 1.0")
    confidence_label: str = Field(..., description="High, Medium, or Low")


class NextSkillInference(BaseModel):
    """Inferred next technological progression or adjacent skill."""
    next_skill: str = Field(..., description="Recommended next technology skill, e.g. System Design")
    target_category: str = Field(..., description="Category for candidate retrieval, e.g. HLD, Backend")
    reason: str = Field(..., description="Why this next skill logically follows the inferred interest")
    adjacent_skills: List[str] = Field(default_factory=list, description="Other adjacent learning pathways")
    learning_path_stage: str = Field("Next Step", description="Current stage in tech progression")
    confidence: str = Field("High", description="High / Medium / Low")


class ScoredCandidate(BaseModel):
    """Candidate reel with detailed multi-objective NEXUS ranking breakdown."""
    reel: ReelItem
    semantic_relevance: float = Field(..., ge=0.0, le=100.0, description="Semantic similarity score (0-100)")
    interest_alignment: float = Field(..., ge=0.0, le=100.0, description="Alignment with latent interest (0-100)")
    novelty: float = Field(..., ge=0.0, le=100.0, description="Novelty/discovery score (0-100)")
    educational_value: float = Field(..., ge=0.0, le=100.0, description="Educational quality score (0-100)")
    difficulty_fit: float = Field(..., ge=0.0, le=100.0, description="Difficulty suitability (0-100)")
    hype_penalty: float = Field(0.0, ge=0.0, le=100.0, description="Subtracted hype penalty (0-100)")
    redundancy_penalty: float = Field(0.0, ge=0.0, le=100.0, description="Subtracted redundancy penalty (0-100)")
    nexus_score: float = Field(..., description="Final composite NEXUS score (0-100)")
    is_suppressed: bool = Field(False, description="True if rejected by Quality/Hype Gate")
    suppression_reason: Optional[str] = Field(None, description="Detailed explanation if suppressed")


class RecommendationOutput(BaseModel):
    """The final authoritative NEXUS recommendation output structure."""
    current_reel_reference: str = Field(..., description="CURRENT REEL: reference to watched history/context")
    interest_detected: str = Field(..., description="INTEREST DETECTED: inferred latent interest")
    why_evidence: str = Field(..., description="WHY: evidence from content interactions")
    recommended_tech_reel: ReelItem = Field(..., description="RECOMMENDED TECH REEL: winning candidate")
    category: str = Field(..., description="CATEGORY: topic category")
    why_this_recommendation: str = Field(..., description="WHY THIS RECOMMENDATION: connection to interest")
    difficulty: str = Field(..., description="DIFFICULTY: Beginner / Intermediate / Advanced")
    confidence: str = Field(..., description="CONFIDENCE: High / Medium / Low")
    nexus_score: float = Field(..., description="NEXUS SCORE: final composite score")
    score_breakdown: Dict[str, float] = Field(default_factory=dict, description="Component scores for explainability")
    rejected_candidate: Optional[ScoredCandidate] = Field(None, description="Suppressed hype candidate if available")
    why_not_this: Optional[str] = Field(None, description="WHY NOT THIS: explanation for hype rejection")
    bridge_steps: List[str] = Field(default_factory=list, description="Step-by-step Interest Bridge progression")
    shortlisted_candidates: List[ScoredCandidate] = Field(default_factory=list, description="Top ranked candidates")
