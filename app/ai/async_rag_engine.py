import logging
import math
import re

from app.ai.async_embedding_client import AsyncEmbeddingClient


logger = logging.getLogger(__name__)


class AsyncRAGEngine:
    """
    Async RAG engine.

    Responsibilities:
    - Normalize text
    - Tokenize text
    - Chunk content
    - Generate async embeddings
    - Calculate cosine similarity
    """

    def __init__(
        self,
        chunk_size: int = 240,
        chunk_overlap: int = 50,
    ) -> None:
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.embedding_client = AsyncEmbeddingClient()

    def normalize_text(
        self,
        text: str,
    ) -> str:
        """
        Normalize text before chunking.
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
    ) -> list[str]:
        """
        Convert text into tokens.
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
    ) -> list[str]:
        """
        Split text into overlapping chunks.
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

        chunks: list[str] = []
        start = 0

        while start < len(tokens):
            end = start + self.chunk_size
            chunk_tokens = tokens[start:end]
            chunk_text = " ".join(chunk_tokens)

            if chunk_text:
                chunks.append(chunk_text)

            if end >= len(tokens):
                break

            start = max(
                end - self.chunk_overlap,
                start + 1,
            )

        return chunks

    async def embed_text(
        self,
        text: str,
    ) -> list[float]:
        """
        Generate async embedding for text.
        """

        cleaned_text = text.strip()

        if not cleaned_text:
            return []

        return await self.embedding_client.get_embedding(
            cleaned_text
        )

    def cosine_similarity(
        self,
        first_vector: list[float],
        second_vector: list[float],
    ) -> float:
        """
        Calculate cosine similarity between two vectors.
        """

        if not first_vector or not second_vector:
            return 0.0

        if len(first_vector) != len(second_vector):
            logger.warning(
                "Vector size mismatch | first=%s second=%s",
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