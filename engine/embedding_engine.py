"""
NEXUS - Semantic Embedding Engine
Generates, caches, and computes cosine similarities across semantic embeddings
using Gemini Embeddings when online, backed by an isolated persistent cache
and deterministic dense vectorization fallback.
"""

from typing import List, Dict, Tuple, Optional, Any
import json
import numpy as np
from pathlib import Path
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from models.schemas import ReelItem
from services.gemini_service import GeminiService
from config import EMBEDDINGS_CACHE_PATH, EMBEDDING_MODEL


class EmbeddingEngine:
    """Isolated semantic embedding manager with persistent caching and cosine retrieval."""

    def __init__(self, gemini_service: Optional[GeminiService] = None):
        self.gemini = gemini_service or GeminiService()
        self.cache: Dict[str, List[float]] = {}
        self._tfidf_vectorizer: Optional[TfidfVectorizer] = None
        self._tfidf_corpus_matrix = None
        self._corpus_reels: List[ReelItem] = []
        self._load_cache()

    def _load_cache(self):
        """Loads cached embeddings from disk."""
        if EMBEDDINGS_CACHE_PATH.exists():
            try:
                with open(EMBEDDINGS_CACHE_PATH, "r", encoding="utf-8") as f:
                    self.cache = json.load(f)
            except Exception:
                self.cache = {}

    def _save_cache(self):
        """Saves embedding cache to disk."""
        try:
            with open(EMBEDDINGS_CACHE_PATH, "w", encoding="utf-8") as f:
                json.dump(self.cache, f)
        except Exception:
            pass

    def _make_reel_text(self, reel: ReelItem) -> str:
        """Constructs rich semantic text representation for a reel."""
        tags = reel.semantic_tags.replace(",", " ")
        prereqs = (reel.prerequisites or "").replace(",", " ")
        return f"{reel.title}. Category: {reel.category}. Topic: {reel.topic}. Concepts: {tags}. Prerequisites: {prereqs}. Difficulty: {reel.difficulty}."

    def build_corpus_index(self, candidates: List[ReelItem]):
        """Indexes candidate reels, generates missing embeddings, and prepares fast similarity search."""
        self._corpus_reels = candidates
        texts_to_embed = []
        keys_to_embed = []

        for reel in candidates:
            cache_key = f"{reel.reel_id}_{reel.title}"
            if cache_key not in self.cache:
                reel_text = self._make_reel_text(reel)
                texts_to_embed.append(reel_text)
                keys_to_embed.append(cache_key)

        # Batch embed missing items if Gemini is available
        if texts_to_embed and self.gemini.is_available():
            try:
                embeddings = self.gemini.get_batch_embeddings(texts_to_embed)
                if embeddings and len(embeddings) == len(keys_to_embed):
                    for k, emb in zip(keys_to_embed, embeddings):
                        self.cache[k] = emb
                    self._save_cache()
            except Exception:
                pass

        # Also fit TF-IDF vectorizer over the corpus for dense deterministic semantic fallback
        all_corpus_texts = [self._make_reel_text(r) for r in candidates]
        self._tfidf_vectorizer = TfidfVectorizer(
            ngram_range=(1, 3),
            sublinear_tf=True,
            stop_words="english",
            max_features=2000
        )
        self._tfidf_corpus_matrix = self._tfidf_vectorizer.fit_transform(all_corpus_texts)

    def embed_text(self, text: str) -> List[float]:
        """Generates embedding for arbitrary query string with caching."""
        cache_key = f"query_{text.strip()}"
        if cache_key in self.cache:
            return self.cache[cache_key]

        if self.gemini.is_available():
            emb = self.gemini.get_embedding(text)
            if emb:
                self.cache[cache_key] = emb
                self._save_cache()
                return emb

        # Fallback to TF-IDF vector representation
        if self._tfidf_vectorizer:
            vec = self._tfidf_vectorizer.transform([text]).toarray()[0]
            return vec.tolist()

        return [0.0]

    def compute_similarity(self, query_text: str, candidate: ReelItem) -> float:
        """
        Computes cosine similarity (0.0 to 1.0) between query text and a candidate reel.
        """
        cand_key = f"{candidate.reel_id}_{candidate.title}"

        # If using Gemini embeddings
        if self.gemini.is_available():
            query_emb = self.embed_text(query_text)
            cand_emb = self.cache.get(cand_key)
            if not cand_emb:
                cand_text = self._make_reel_text(candidate)
                cand_emb = self.embed_text(cand_text)

            if query_emb and cand_emb and len(query_emb) == len(cand_emb):
                q = np.array(query_emb).reshape(1, -1)
                c = np.array(cand_emb).reshape(1, -1)
                sim = cosine_similarity(q, c)[0][0]
                # Normalize cosine similarity to [0.0, 1.0]
                return float(max(0.0, min(1.0, (sim + 1.0) / 2.0 if sim < 0 else sim)))

        # Fallback to TF-IDF cosine similarity
        if self._tfidf_vectorizer is not None:
            q_vec = self._tfidf_vectorizer.transform([query_text])
            c_vec = self._tfidf_vectorizer.transform([self._make_reel_text(candidate)])
            sim = cosine_similarity(q_vec, c_vec)[0][0]
            return float(max(0.0, min(1.0, sim)))

        return 0.5

    def compute_batch_similarities(self, query_text: str, candidates: List[ReelItem]) -> List[float]:
        """Computes similarity scores across an entire list of candidates."""
        if self._tfidf_vectorizer is not None and not self.gemini.is_available():
            # Fast vectorized batch computation
            q_vec = self._tfidf_vectorizer.transform([query_text])
            c_texts = [self._make_reel_text(c) for c in candidates]
            c_mat = self._tfidf_vectorizer.transform(c_texts)
            sims = cosine_similarity(q_vec, c_mat)[0]
            return [float(max(0.0, min(1.0, s))) for s in sims]

        return [self.compute_similarity(query_text, c) for c in candidates]
