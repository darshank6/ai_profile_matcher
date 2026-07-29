import logging
from typing import Any, Dict, List

import requests

from app.config import settings


logger = logging.getLogger(__name__)


class EmbeddingClient:
    """
    Embedding client for OpenAI-compatible embedding APIs.

    This client is designed for corporate environments where
    Hugging Face / SentenceTransformer downloads are blocked.

    It calls an OpenAI-compatible embedding endpoint and returns
    a list of floating-point vector values.
    """

    def __init__(
        self,
        base_url: str | None = None,
        model_name: str | None = None,
        api_key: str | None = None,
        timeout_seconds: int = 60,
    ) -> None:
        self.base_url = base_url or settings.EMBEDDING_BASE_URL
        self.model_name = model_name or settings.EMBEDDING_MODEL
        self.api_key = api_key or settings.OPENAI_API_KEY
        self.timeout_seconds = timeout_seconds

    def get_embedding(
        self,
        text: str,
    ) -> List:
        """
        Generate embedding vector for a single text input.

        Args:
            text: Input text to embed.

        Returns:
            List of float values representing the embedding vector.

        Raises:
            RuntimeError: If API key is missing, API request fails,
            or embedding response format is invalid.
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

        try:
            response = requests.post(
                self.base_url,
                headers=headers,
                json=payload,
                timeout=self.timeout_seconds,
            )

            response.raise_for_status()

            response_json = response.json()

            return self._extract_embedding(
                response_json
            )

        except requests.exceptions.Timeout as exc:
            logger.exception(
                "Embedding API request timed out."
            )

            raise RuntimeError(
                "Embedding API request timed out."
            ) from exc

        except requests.exceptions.RequestException as exc:
            logger.exception(
                "Embedding API request failed."
            )

            raise RuntimeError(
                f"Embedding API request failed: {str(exc)}"
            ) from exc

        except Exception as exc:
            logger.exception(
                "Embedding generation failed."
            )

            raise RuntimeError(
                f"Embedding generation failed: {str(exc)}"
            ) from exc

    def _extract_embedding(
        self,
        response_json: Dict[str, Any],
    ):
        """
        Extract embedding vector from OpenAI-compatible response.

        Expected format:
        {
            "data": [
                {
                    "embedding": [...]
                }
            ]
        }
        """

        data = response_json.get("data")

        if not isinstance(data, list) or not data:
            raise RuntimeError(
                "Embedding API response does not contain data list."
            )

        first_item = data[0]

        if not isinstance(first_item, dict):
            raise RuntimeError(
                "Embedding API response data item is invalid."
            )

        embedding = first_item.get("embedding")

        if not isinstance(embedding, list):
            raise RuntimeError(
                "Embedding API response does not contain embedding list."
            )

        return [
            float(value)
            for value in embedding
        ]