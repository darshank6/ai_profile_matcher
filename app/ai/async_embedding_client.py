import logging
from typing import Any

import httpx

from app.config import settings


logger = logging.getLogger(__name__)


class AsyncEmbeddingClient:
    """
    Async OpenAI-compatible embedding client.

    This client uses KPIT/OpenAI-compatible embedding endpoint and
    avoids HuggingFace/SentenceTransformer download issues on corporate machines.
    """

    def __init__(
        self,
        base_url: str | None = None,
        model_name: str | None = None,
        api_key: str | None = None,
        timeout_seconds: float = 60.0,
    ) -> None:
        self.base_url = base_url or settings.EMBEDDING_BASE_URL
        self.model_name = model_name or settings.EMBEDDING_MODEL
        self.api_key = api_key or settings.OPENAI_API_KEY
        self.timeout_seconds = timeout_seconds

    async def get_embedding(
        self,
        text: str,
    ) -> list[float]:
        """
        Generate embedding vector asynchronously.

        Returns a list of floats.
        """

        cleaned_text = text.strip()

        if not cleaned_text:
            return []

        if not self.api_key:
            raise RuntimeError(
                "OPENAI_API_KEY is missing. Please set it in your .env file."
            )

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
        }

        payload = {
            "input": cleaned_text,
            "model": self.model_name,
            "encoding_format": "float",
        }

        async with httpx.AsyncClient(
            timeout=self.timeout_seconds,
        ) as client:
            response = await client.post(
                self.base_url,
                headers=headers,
                json=payload,
            )

            response.raise_for_status()

            response_json = response.json()

        return self._extract_embedding(
            response_json
        )

    def _extract_embedding(
        self,
        response_json: dict[str, Any],
    ) -> list[float]:
        """
        Parse OpenAI-compatible embedding response.
        """

        data = response_json.get("data")

        if not isinstance(data, list) or not data:
            raise RuntimeError(
                "Embedding response does not contain valid data list."
            )

        first_item = data[0]

        if not isinstance(first_item, dict):
            raise RuntimeError(
                "Embedding response data item is invalid."
            )

        embedding = first_item.get("embedding")

        if not isinstance(embedding, list):
            raise RuntimeError(
                "Embedding response does not contain embedding list."
            )

        return [
            float(value)
            for value in embedding
        ]