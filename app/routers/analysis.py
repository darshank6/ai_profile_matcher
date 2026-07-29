from fastapi import APIRouter
from fastapi import Depends

from sqlalchemy.orm import Session

from app.database import get_db

from app.dependencies import get_current_user

from app.schemas.analysis import (
    SkillExtractionResponse
)

from app.services.analysis_service import (
    AnalysisService
)

router = APIRouter()

@router.get(
    "/extract-skills/{resume_id}",
    response_model=SkillExtractionResponse
)
def extract_resume_skills(
    resume_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(
        get_current_user
    )
):

    service = AnalysisService(db)

    return service.extract_resume_skills(
        current_user.id,
        resume_id
    )

