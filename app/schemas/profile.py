from typing import Optional

from pydantic import BaseModel


class ProfileCreate(BaseModel):

    phone: Optional[str] = None

    location: Optional[str] = None

    current_role: Optional[str] = None

    target_role: Optional[str] = None

    experience_years: Optional[int] = None

    linkedin_url: Optional[str] = None

    github_url: Optional[str] = None

    

class ProfileUpdate(BaseModel):

    phone: Optional[str] = None

    location: Optional[str] = None

    current_role: Optional[str] = None

    target_role: Optional[str] = None

    experience_years: Optional[int] = None

    linkedin_url: Optional[str] = None

    github_url: Optional[str] = None


class ProfileResponse(BaseModel):

    id: int

    user_id: int

    phone: Optional[str]

    location: Optional[str]

    current_role: Optional[str]

    target_role: Optional[str]

    experience_years: Optional[int]

    linkedin_url: Optional[str]

    github_url: Optional[str]

    class Config:
        from_attributes = True