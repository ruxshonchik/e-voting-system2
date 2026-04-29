from enum import Enum
from pydantic import BaseModel, EmailStr, Field


class UserRole(str, Enum):
    user = "user"
    admin = "admin"
    superuser = "superuser"


class RegisterRequest(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    email: EmailStr
    password: str = Field(min_length=6, max_length=128)
    role: UserRole = Field(default=UserRole.user, description="Foydalanuvchi roli")

    model_config = {
        "json_schema_extra": {
            "example": {
                "name": "Ali Valiyev",
                "email": "ali@example.com",
                "password": "secret123",
                "role": "user"
            }
        }
    }


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class RefreshRequest(BaseModel):
    refresh_token: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
