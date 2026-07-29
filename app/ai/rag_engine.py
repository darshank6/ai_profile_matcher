import logging
import math
import re
from typing import List

from app.ai.embedding_client import EmbeddingClient


logger = logging.getLogger(__name__)


class RAGEngine:
    """
    RAG vector engine using OpenAI-compatible embeddings.

    Responsibilities:
    - Normalize text
    - Tokenize text
    - Split large documents into overlapping chunks
    - Generate vector embeddings using corporate embedding API
    - Calculate cosine similarity between vectors
    """

    def __init__(
        self,
        chunk_size: int = 240,
        chunk_overlap: int = 50,
    ) -> None:
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.embedding_client = EmbeddingClient()

    def normalize_text(
        self,
        text: str,
    ) -> str:
        """
        Normalize input text for chunking and embedding.
        """

        cleaned_text = text.lower()
        cleaned_text = re.sub(
            r"[^a-z0-9+#.\- ]+",
            " ",
            cleaned_text,
        )
        cleaned_text = re.sub(
            r"\s+",
            " ",
            cleaned_text,
        ).strip()

        return cleaned_text

    def tokenize(
        self,
        text: str,
    ):
        """
        Convert text into normalized tokens.
        """

        normalized_text = self.normalize_text(
            text
        )

        if not normalized_text:
            return []

        return normalized_text.split(" ")

    def chunk_text(
        self,
        text: str,
    ):
        """
        Split long text into overlapping chunks.
        """

        tokens = self.tokenize(
            text
        )

        if not tokens:
            return []

        if len(tokens) <= self.chunk_size:
            return [
                " ".join(tokens)
            ]

        chunks: List[str] = []
        start = 0

        while start < len(tokens):
            end = start + self.chunk_size

            chunk_tokens = tokens[
                start:end
            ]

            chunk_text = " ".join(
                chunk_tokens
            )

            if chunk_text:
                chunks.append(
                    chunk_text
                )

            if end >= len(tokens):
                break

            start = max(
                end - self.chunk_overlap,
                start + 1,
            )

        return chunks

    def embed_text(
        self,
        text: str,
    ):
        """
        Generate vector embedding for text using OpenAI-compatible API.
        """

        cleaned_text = text.strip()

        if not cleaned_text:
            return []

        return self.embedding_client.get_embedding(
            cleaned_text
        )

    def cosine_similarity(
        self,
        first_vector: List[float],
        second_vector: List[float],
    ) -> float:
        """
        Calculate cosine similarity between two vectors.
        """

        if not first_vector or not second_vector:
            return 0.0

        if len(first_vector) != len(second_vector):
            logger.warning(
                "Vector size mismatch. first=%s second=%s",
                len(first_vector),
                len(second_vector),
            )
            return 0.0

        numerator = sum(
            first_value * second_value
            for first_value, second_value in zip(
                first_vector,
                second_vector,
            )
        )

        first_norm = math.sqrt(
            sum(
                value * value
                for value in first_vector
            )
        )

        second_norm = math.sqrt(
            sum(
                value * value
                for value in second_vector
            )
        )

        if first_norm == 0 or second_norm == 0:
            return 0.0

        return numerator / (
            first_norm * second_norm
        )