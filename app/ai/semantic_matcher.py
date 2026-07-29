import math
import re
from collections import Counter
from typing import List
from typing import Set


class SemanticMatcher:
    """
    Lightweight local semantic matcher.

    This implementation avoids heavy ML dependencies and uses:
    - Text normalization
    - Token cosine similarity
    - Skill overlap scoring

    It can later be upgraded to:
    - sentence-transformers
    - OpenAI embeddings
    - PgVector
    """

    def normalize_text(
        self,
        text: str,
    ) -> str:
        """
        Normalize text for token-level semantic comparison.
        """

        cleaned_text = text.lower()
        cleaned_text = re.sub(r"[^a-z0-9+#.\- ]+", " ", cleaned_text)
        cleaned_text = re.sub(r"\s+", " ", cleaned_text).strip()

        return cleaned_text

    def tokenize(
        self,
        text: str,
    ) -> List[str]:
        """
        Tokenize normalized text.
        """

        normalized_text = self.normalize_text(text)

        if not normalized_text:
            return []

        return normalized_text.split(" ")

    def cosine_similarity(
        self,
        first_text: str,
        second_text: str,
    ) -> float:
        """
        Compute cosine similarity using token count vectors.
        """

        first_tokens = self.tokenize(first_text)
        second_tokens = self.tokenize(second_text)

        if not first_tokens or not second_tokens:
            return 0.0

        first_counter = Counter(first_tokens)
        second_counter = Counter(second_tokens)

        common_tokens = set(first_counter.keys()).intersection(
            set(second_counter.keys())
        )

        numerator = sum(
            first_counter[token] * second_counter[token]
            for token in common_tokens
        )

        first_norm = math.sqrt(
            sum(value * value for value in first_counter.values())
        )

        second_norm = math.sqrt(
            sum(value * value for value in second_counter.values())
        )

        if first_norm == 0 or second_norm == 0:
            return 0.0

        return numerator / (first_norm * second_norm)

    def keyword_score(
        self,
        resume_skills: Set[str],
        job_skills: Set[str],
    ) -> float:
        """
        Calculate keyword skill score.
        """

        if not job_skills:
            return 0.0

        matched_skills = resume_skills.intersection(job_skills)

        return round(
            (len(matched_skills) / len(job_skills)) * 100,
            2,
        )

    def semantic_score(
        self,
        resume_text: str,
        job_text: str,
    ) -> float:
        """
        Calculate semantic score from text similarity.
        """

        similarity = self.cosine_similarity(
            first_text=resume_text,
            second_text=job_text,
        )

        return round(
            similarity * 100,
            2,
        )

    def overall_score(
        self,
        keyword_score: float,
        semantic_score: float,
    ) -> float:
        """
        Weighted overall score.

        Weight:
        - 60% keyword skill score
        - 40% semantic similarity score
        """

        return round(
            (keyword_score * 0.6) + (semantic_score * 0.4),
            2,
        )

    def build_explanation(
        self,
        overall_score: float,
        keyword_score: float,
        semantic_score: float,
        matched_skills: List[str],
        missing_skills: List[str],
    ) -> str:
        """
        Build human-readable explanation.
        """

        explanation = (
            f"The overall match score is {overall_score}%. "
            f"The keyword skill match score is {keyword_score}%, "
            f"and the semantic similarity score is {semantic_score}%. "
        )

        if matched_skills:
            explanation += (
                "Matched skills include: "
                + ", ".join(matched_skills)
                + ". "
            )

        if missing_skills:
            explanation += (
                "Missing or weak skills include: "
                + ", ".join(missing_skills)
                + "."
            )

        return explanation

    def build_recommendation(
        self,
        overall_score: float,
        missing_skills: List[str],
    ) -> str:
        """
        Build recommendation based on score and gaps.
        """

        if overall_score >= 85:
            return (
                "This is a strong match. The candidate should apply confidently "
                "and ensure the resume highlights measurable technical impact."
            )

        if overall_score >= 65:
            missing_text = ", ".join(missing_skills) if missing_skills else "the missing role-specific skills"

            return (
                "This is a moderate match. The candidate should strengthen "
                f"the resume by improving or highlighting: {missing_text}."
            )

        missing_text = ", ".join(missing_skills) if missing_skills else "core job requirements"

        return (
            "This is a weak match. The candidate should build more practical "
            f"experience in {missing_text} before applying."
        )