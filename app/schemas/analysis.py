from pydantic import BaseModel


class AnalysisRequest(BaseModel):
    job_id: int
    resume_text: str


class AnalysisResponse(BaseModel):
    match_score: float
    recommendation: str
    extracted_skills: list[str]

class SkillExtractionResponse(
    BaseModel
):
    skills: list[str]