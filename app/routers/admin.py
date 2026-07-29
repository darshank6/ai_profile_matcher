from fastapi import APIRouter
from fastapi import Depends

from app.dependencies import role_required


router = APIRouter()


@router.get("/admin-dashboard")
def admin_dashboard(
    current_user=Depends(
        role_required(["admin"])
    )
):
    return {
        "message": "Welcome to Admin Dashboard",
        "user": current_user.email,
        "role": current_user.role
    }


@router.get("/candidate-dashboard")
def candidate_dashboard(
    current_user=Depends(
        role_required(["candidate", "admin"])
    )
):
    return {
        "message": "Welcome to Candidate Dashboard",
        "user": current_user.email,
        "role": current_user.role
    }


@router.get("/recruiter-dashboard")
def recruiter_dashboard(
    current_user=Depends(
        role_required(["recruiter", "admin"])
    )
):
    return {
        "message": "Welcome to Recruiter Dashboard",
        "user": current_user.email,
        "role": current_user.role
    }


@router.get("/common-dashboard")
def common_dashboard(
    current_user=Depends(
        role_required(["candidate", "recruiter", "admin"])
    )
):
    return {
        "message": "Welcome to Common Dashboard",
        "user": current_user.email,
        "role": current_user.role
    }