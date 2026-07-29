import json
import logging
from typing import Dict
from typing import List
from typing import Any

import httpx

from app.config import settings


logger = logging.getLogger(__name__)


class LLMClient:
    """
    Reusable LLM client for Ollama and OpenAI-compatible APIs.
    """

    def __init__(
        self,
        provider: str | None = None,
        model_name: str | None = None
    ):
        self.provider = provider or settings.LLM_PROVIDER
        self.model_name = model_name or settings.LLM_MODEL

    def generate_rag_answer(
        self,
        question: str,
        context: str,
    ) -> str:
        """
        Generate an answer using retrieved RAG context.
        """

        system_prompt = (
            "You are an AI career assistant. "
            "Answer the user's question using only the provided context. "
            "If the context is insufficient, say that the knowledge base does not contain enough information. "
            "Keep the answer clear, practical, and career-focused."
        )

        user_prompt = (
            f"Context:\n{context}\n\n"
            f"Question:\n{question}\n\n"
            "Answer:"
        )

        return self._call_llm(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
        )

    def generate_learning_roadmap(
        self,
        resume_text: str,
        target_role: str,
    ) -> dict:
        """
        Generate an AI learning roadmap based on
        resume content and target role.
        """

        system_prompt = (
            "You are a senior technical mentor, engineering manager, "
            "career coach, and learning advisor. "
            "Analyze the resume and create a personalized learning roadmap. "
            "Return ONLY valid JSON with the following keys:\n"
            "{\n"
            '  "current_skills": "string",\n'
            '  "missing_skills": "string",\n'
            '  "roadmap_title": "string",\n'
            '  "roadmap_summary": "string",\n'
            '  "weekly_plan": "string",\n'
            '  "recommended_projects": "string",\n'
            '  "recommended_courses": "string",\n'
            '  "recommended_certifications": "string",\n'
            '  "priority_topics": "string",\n'
            '  "estimated_duration": "string"\n'
            "}\n"
            "Do not return markdown. "
            "Do not return explanations. "
            "Return only JSON."
        )

        user_prompt = (
            f"Target Role: {target_role}\n\n"
            f"Resume:\n{resume_text}\n\n"
            "Generate a detailed learning roadmap."
        )

        content = self._call_llm(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
        )

        try:
            parsed = json.loads(content)

            return {
                "current_skills": str(
                    parsed.get(
                        "current_skills",
                        ""
                    )
                ),
                "missing_skills": str(
                    parsed.get(
                        "missing_skills",
                        ""
                    )
                ),
                "roadmap_title": str(
                    parsed.get(
                        "roadmap_title",
                        f"{target_role} Learning Roadmap",
                    )
                ),
                "roadmap_summary": str(
                    parsed.get(
                        "roadmap_summary",
                        ""
                    )
                ),
                "weekly_plan": str(
                    parsed.get(
                        "weekly_plan",
                        ""
                    )
                ),
                "recommended_projects": str(
                    parsed.get(
                        "recommended_projects",
                        ""
                    )
                ),
                "recommended_courses": str(
                    parsed.get(
                        "recommended_courses",
                        ""
                    )
                ),
                "recommended_certifications": str(
                    parsed.get(
                        "recommended_certifications",
                        ""
                    )
                ),
                "priority_topics": str(
                    parsed.get(
                        "priority_topics",
                        ""
                    )
                ),
                "estimated_duration": str(
                    parsed.get(
                        "estimated_duration",
                        ""
                    )
                ),
            }

        except Exception:
            logger.exception(
                "Failed to parse learning roadmap response."
            )

            return {
                "current_skills": "",
                "missing_skills": "",
                "roadmap_title": (
                    f"{target_role} Learning Roadmap"
                ),
                "roadmap_summary": content,
                "weekly_plan": (
                    "Week 1-2: Core Concepts\n"
                    "Week 3-4: Intermediate Concepts\n"
                    "Week 5-6: Advanced Concepts\n"
                    "Week 7-8: Projects"
                ),
                "recommended_projects": "",
                "recommended_courses": "",
                "recommended_certifications": "",
                "priority_topics": "",
                "estimated_duration": "8 Weeks",
            }

    def generate_job_recommendation_summary(
        self,
        resume_text: str,
        target_role: str | None,
        recommended_jobs: List[Dict[str, Any]]
    ) -> str:
        system_prompt = (
            "You are a senior career advisor. "
            "Write a concise job recommendation summary based on resume and matched jobs."
        )

        user_prompt = (
            f"Target Role: {target_role or 'Not specified'}\n\n"
            f"Resume:\n{resume_text}\n\n"
            f"Recommended Jobs JSON:\n{json.dumps(recommended_jobs)}\n\n"
            "Explain why these jobs are suitable and what the candidate should improve."
        )

        return self._call_llm(
            system_prompt=system_prompt,
            user_prompt=user_prompt
        )

    def generate_resume_analysis(
        self,
        resume_text: str
    ) -> dict:
        system_prompt = (
            "You are a senior technical recruiter and resume coach. "
            "Analyze the resume professionally. "
            "Return only valid JSON with keys: summary, strengths, weaknesses, suggestions."
        )

        user_prompt = (
            "Analyze this resume and return JSON only.\n\n"
            f"Resume:\n{resume_text}"
        )

        content = self._call_llm(
            system_prompt=system_prompt,
            user_prompt=user_prompt
        )

        try:
            parsed = json.loads(content)

            return {
                "summary": str(parsed.get("summary", "")),
                "strengths": str(parsed.get("strengths", "")),
                "weaknesses": str(parsed.get("weaknesses", "")),
                "suggestions": str(parsed.get("suggestions", ""))
            }

        except Exception:
            return {
                "summary": content,
                "strengths": "AI response generated but not in strict JSON format.",
                "weaknesses": "JSON parsing failed.",
                "suggestions": "Use a stricter JSON prompt or a stronger model."
            }

    def generate_cover_letter(
        self,
        resume_text: str,
        job_title: str,
        company_name: str | None,
        job_description: str
    ) -> str:
        company_display_name = company_name or "the company"

        system_prompt = (
            "You are an expert career coach and professional cover letter writer. "
            "Write a concise, professional, ATS-friendly cover letter. "
            "Do not include fake achievements. "
            "Use only the provided resume and job description."
        )

        user_prompt = (
            f"Job Title: {job_title}\n"
            f"Company: {company_display_name}\n\n"
            f"Job Description:\n{job_description}\n\n"
            f"Candidate Resume:\n{resume_text}\n\n"
            "Write a professional cover letter in 4 concise paragraphs."
        )

        return self._call_llm(
            system_prompt=system_prompt,
            user_prompt=user_prompt
        )

    def generate_interview_questions(
        self,
        resume_text: str,
        job_title: str,
        company_name: str | None,
        job_description: str
    ) -> Dict[str, List[str]]:
        company_display_name = company_name or "the company"

        system_prompt = (
            "You are a senior technical interviewer. "
            "Generate interview questions based only on the candidate resume and job description. "
            "Return only valid JSON with these exact keys: "
            "easy_questions, medium_questions, hard_questions, behavioral_questions, system_design_questions. "
            "Each key must contain a list of strings."
        )

        user_prompt = (
            f"Job Title: {job_title}\n"
            f"Company: {company_display_name}\n\n"
            f"Job Description:\n{job_description}\n\n"
            f"Candidate Resume:\n{resume_text}\n\n"
            "Generate 5 easy, 5 medium, 5 hard, 5 behavioral, and 5 system design interview questions. "
            "Return valid JSON only."
        )

        content = self._call_llm(
            system_prompt=system_prompt,
            user_prompt=user_prompt
        )

        try:
            parsed = json.loads(content)

            return {
                "easy_questions": self._safe_list(parsed.get("easy_questions")),
                "medium_questions": self._safe_list(parsed.get("medium_questions")),
                "hard_questions": self._safe_list(parsed.get("hard_questions")),
                "behavioral_questions": self._safe_list(parsed.get("behavioral_questions")),
                "system_design_questions": self._safe_list(parsed.get("system_design_questions")),
            }

        except Exception:
            logger.exception("Failed to parse interview question JSON response.")

            return {
                "easy_questions": [
                    "What are your strongest technical skills based on your resume?",
                    "Explain your experience with Python.",
                    "What is FastAPI?",
                    "What is PostgreSQL?",
                    "What is REST API?"
                ],
                "medium_questions": [
                    "How do you structure a FastAPI application?",
                    "Explain authentication using JWT.",
                    "How do you design database relationships in SQLAlchemy?",
                    "How do you handle file uploads in FastAPI?",
                    "Explain repository and service layer patterns."
                ],
                "hard_questions": [
                    "How would you scale this platform for thousands of users?",
                    "How would you optimize slow PostgreSQL queries?",
                    "How would you design secure multi-tenant APIs?",
                    "How would you implement background processing using Celery?",
                    "How would you debug production memory issues?"
                ],
                "behavioral_questions": [
                    "Tell me about a challenging bug you fixed.",
                    "How do you handle unclear requirements?",
                    "How do you work with cross-functional teams?",
                    "Describe a time you improved a system.",
                    "How do you handle feedback during code reviews?"
                ],
                "system_design_questions": [
                    "Design an AI resume analysis platform.",
                    "Design a scalable file upload service.",
                    "Design an ATS scoring engine.",
                    "Design a notification system for completed AI tasks.",
                    "Design a RAG-based career coach."
                ]
            }

    def _parse_json_with_defaults(
        self,
        content: str,
        defaults: Dict[str, Any]
    ) -> Dict[str, Any]:
        try:
            parsed = json.loads(content)

            if not isinstance(parsed, dict):
                return defaults

            result = {}

            for key, default_value in defaults.items():
                result[key] = parsed.get(key, default_value)

            return result

        except Exception:
            logger.exception("JSON parsing failed.")
            return defaults

    def _ensure_list(
        self,
        value: Any
    ) -> List[str]:
        if value is None:
            return []

        if isinstance(value, list):
            return [str(item) for item in value]

        if isinstance(value, str):
            return [value]

        return [str(value)]

    def _safe_list(
        self,
        value
    ) -> List[str]:
        if isinstance(value, list):
            return [str(item) for item in value]

        if isinstance(value, str):
            return [value]

        return []

    def _call_llm(
        self,
        system_prompt: str,
        user_prompt: str
    ) -> str:
        provider = self.provider.lower()

        if provider == "openai":
            return self._call_openai(
                system_prompt=system_prompt,
                user_prompt=user_prompt
            )

        return self._call_ollama(
            system_prompt=system_prompt,
            user_prompt=user_prompt
        )

    def _call_openai(
        self,
        system_prompt: str,
        user_prompt: str
    ) -> str:
        if not settings.OPENAI_API_KEY:
            logger.error("OpenAI API key is not configured.")
            return "OpenAI API key is not configured."

        url = f"{settings.OPENAI_BASE_URL}/chat/completions"

        payload = {
            "model": self.model_name,
            "messages": [
                {
                    "role": "system",
                    "content": system_prompt
                },
                {
                    "role": "user",
                    "content": user_prompt
                }
            ],
            "temperature": 0.3
        }

        headers = {
            "Authorization": f"Bearer {settings.OPENAI_API_KEY}",
            "Content-Type": "application/json"
        }

        try:
            response = httpx.post(
                url,
                headers=headers,
                json=payload,
                timeout=120
            )
            response.raise_for_status()

            return response.json()["choices"][0]["message"]["content"]

        except Exception as exc:
            logger.exception("OpenAI request failed.")
            return f"OpenAI generation failed: {str(exc)}"

    def _call_ollama(
        self,
        system_prompt: str,
        user_prompt: str
    ) -> str:
        url = f"{settings.OLLAMA_BASE_URL}/api/chat"

        payload = {
            "model": self.model_name,
            "messages": [
                {
                    "role": "system",
                    "content": system_prompt
                },
                {
                    "role": "user",
                    "content": user_prompt
                }
            ],
            "stream": False
        }

        try:
            response = httpx.post(
                url,
                json=payload,
                timeout=180
            )
            response.raise_for_status()

            return response.json()["message"]["content"]

        except Exception as exc:
            logger.exception("Ollama request failed.")
            return f"Ollama generation failed: {str(exc)}"
