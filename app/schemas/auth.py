from pydantic import BaseModel
from pydantic import EmailStr
from pydantic import BaseModel, EmailStr, field_validator


class RegisterRequest(BaseModel):
    name: str
    email: EmailStr
    password: str
    role: str = "candidate"

    @field_validator("role")
    @classmethod
    def validate_role(cls, value):
        allowed_roles = [
            "candidate",
            "recruiter",
            "admin"
        ]

        if value not in allowed_roles:
            raise ValueError(
                f"Role must be one of {allowed_roles}"
            )

        return value


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str


class UserResponse(BaseModel):
    id: int
    name: str
    email: str
    role: str
    is_active: bool

    class Config:
        from_attributes = True
