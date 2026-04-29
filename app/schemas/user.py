from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional

from app.schemas.auth import UserRole


class UserOut(BaseModel):
    id: int
    name: str
    email: EmailStr
    role: str
    avatar: Optional[str] = None
    created_at: datetime

    model_config = {"from_attributes": True}


class UserUpdateMe(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None


class UserRoleUpdate(BaseModel):
    role: UserRole
