from fastapi import FastAPI
from app.models import *

from app.database import Base
from app.database import engine

# from app.models import user
# from app.models import resume

from app.routers import admin
from app.routers import auth
from app.routers import resumes
from app.routers import profile
from app.routers import analysis
from app.routers import ats
from app.routers import jobs
from app.routers import ai_resume
from app.routers import cover_letters
from app.routers import interview_questions
from app.routers import learning_roadmaps
from app.routers import job_recommendations
from app.routers import semantic_matches
from app.routers import rag
from app.routers import async_career_coach
# from app.routers import vector_rag

Base.metadata.create_all(
    bind=engine
)


app = FastAPI(
    title="AI Career Intelligence Platform",
    description="AI Resume Analyzer, Profile Matcher, ATS Scoring and RAG Career Coach",
    version="1.0.0"
)


@app.get("/")
def home():
    return {
        "message": "AI Career Intelligence Platform is running successfully"
    }


@app.get("/health")
def health_check():
    return {
        "status": "ok"
    }


app.include_router(
    auth.router,
    prefix="/api/auth",
    tags=["Authentication"]
)


app.include_router(
    admin.router,
    prefix="/api/dashboard",
    tags=["Role Based Dashboards"]
)


app.include_router(
    profile.router,
    prefix="/api/profile",
    tags=["Profiles"]
)

app.include_router(
    resumes.router,
    prefix="/api/resumes",
    tags=["Resumes"]
)

app.include_router(
    analysis.router,
    prefix="/api/analysis",
    tags=["AI Analysis"]
)

app.include_router(
    ats.router,
    prefix="/api/ats",
    tags=["ATS Engine"]
)

app.include_router(
    jobs.router,
    prefix="/api/jobs",
    tags=["Jobs"]
)

app.include_router(
    ai_resume.router,
    prefix="/api/ai",
    tags=["AI Resume Analyzer"]
)

app.include_router(
    cover_letters.router,
    prefix="/api/cover-letters",
    tags=["AI Cover Letters"]
)

app.include_router(
    interview_questions.router,
    prefix="/api/interview-questions",
    tags=["AI Interview Questions"]
)

app.include_router(
    learning_roadmaps.router,
    prefix="/api/learning-roadmap",
    tags=["Learning road map generator"]
)

app.include_router(
    job_recommendations.router,
    prefix="/api/job-recommendations",
    tags=["AI Job Recommendations"]
)


app.include_router(
    semantic_matches.router,
    prefix="/api/semantic-matches",
    tags=["Semantic Matches"]
)

app.include_router(
    rag.router,
    prefix="/api/rag",
    tags=["RAG Knowledge Base"],
)

# app.include_router(
#     vector_rag.router,
#     prefix="/api/vector-rag",
#     tags=["PgVector RAG"],
# )

app.include_router(
    async_career_coach.router,
    prefix="/api/async-career-coach",
    tags=["Async AI Career Coach"],
)