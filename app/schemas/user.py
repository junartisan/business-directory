from pydantic import BaseModel, EmailStr, Field
from typing import Optional

class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8)
    full_name: str
    # Optional: allow them to select 'owner' during signup
    role: Optional[str] = "consumer" 

class UserOut(BaseModel):
    id: int
    email: EmailStr
    full_name: str
    role: str
    is_identity_verified: bool

    class Config:
        from_attributes = True