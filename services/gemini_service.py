"""
NEXUS - Gemini AI Service
Integrates the official google-genai SDK for structured reasoning and semantic embeddings,
with resilient error handling, parameterization, and offline heuristic fallback.
"""

from typing import List, Dict, Optional, Any, Type, TypeVar
import os
import json
import logging
from pydantic import BaseModel

from config import GEMINI_MODEL, EMBEDDING_MODEL

# Configure logging
logger = logging.getLogger("nexus.gemini_service")

T = TypeVar("T", bound=BaseModel)

# Try importing official google-genai SDK
try:
    from google import genai
    from google.genai import types
    GENAI_AVAILABLE = True
except ImportError:
    GENAI_AVAILABLE = False
    genai = None
    types = None


class GeminiService:
    """Provides LLM reasoning and embedding generation using the official google-genai SDK."""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
        self.client = None
        self._init_client()

    def _init_client(self):
        """Initializes the google-genai client if API key and library are present."""
        if GENAI_AVAILABLE and self.api_key:
            try:
                self.client = genai.Client(api_key=self.api_key)
            except Exception as e:
                logger.warning(f"Failed to initialize google-genai Client: {e}")
                self.client = None
        else:
            self.client = None

    def update_api_key(self, api_key: str):
        """Updates the active API key and reinitializes client."""
        self.api_key = api_key
        self._init_client()

    def is_available(self) -> bool:
        """Returns True if live Gemini API is ready to receive requests."""
        return self.client is not None and bool(self.api_key)

    def generate_structured(
        self,
        prompt: str,
        response_schema: Type[T],
        system_instruction: Optional[str] = None
    ) -> Optional[T]:
        """
        Calls Gemini with structured JSON schema output and parses into Pydantic model.
        Returns None if client is unavailable or API call fails.
        """
        if not self.is_available():
            return None

        try:
            config = types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=response_schema,
                temperature=0.2,
                system_instruction=system_instruction
            )
            response = self.client.models.generate_content(
                model=GEMINI_MODEL,
                contents=prompt,
                config=config
            )
            if response and response.text:
                return response_schema.model_validate_json(response.text)
        except Exception as e:
            logger.warning(f"Gemini generate_structured failed: {e}")
        return None

    def generate_text(self, prompt: str, system_instruction: Optional[str] = None) -> Optional[str]:
        """Generates text from Gemini with optional system instructions."""
        if not self.is_available():
            return None

        try:
            config = types.GenerateContentConfig(
                temperature=0.2,
                system_instruction=system_instruction
            )
            response = self.client.models.generate_content(
                model=GEMINI_MODEL,
                contents=prompt,
                config=config
            )
            return response.text if response else None
        except Exception as e:
            logger.warning(f"Gemini generate_text failed: {e}")
            return None

    def get_embedding(self, text: str) -> Optional[List[float]]:
        """Generates semantic embedding vector using Gemini Embedding model."""
        if not self.is_available():
            return None

        try:
            response = self.client.models.embed_content(
                model=EMBEDDING_MODEL,
                contents=text
            )
            if response and response.embeddings:
                # The first embedding vector
                return response.embeddings[0].values
        except Exception as e:
            logger.warning(f"Gemini get_embedding failed: {e}")
        return None

    def get_batch_embeddings(self, texts: List[str]) -> Optional[List[List[float]]]:
        """Generates batch embeddings using Gemini Embedding model."""
        if not self.is_available():
            return None

        try:
            # google-genai allows batch list of contents
            response = self.client.models.embed_content(
                model=EMBEDDING_MODEL,
                contents=texts
            )
            if response and response.embeddings:
                return [emb.values for emb in response.embeddings]
        except Exception as e:
            logger.warning(f"Gemini get_batch_embeddings failed: {e}")
        return None
