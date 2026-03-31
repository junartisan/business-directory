from pydantic import BaseModel, ConfigDict, HttpUrl
from typing import Optional
from datetime import datetime
from app.models.business import VerificationStatus

class BusinessBase(BaseModel):
    name: str
    city: str
    address: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    category_id: int

class BusinessCreate(BusinessBase):
    pass  # Used for POST requests

class BusinessUpdate(BaseModel):
    name: Optional[str] = None
    verification_status: Optional[VerificationStatus] = None
    is_accredited: Optional[bool] = None
    trust_score: Optional[float] = None

class BusinessOut(BusinessBase):
    id: int
    slug: str
    verification_status: VerificationStatus
    is_accredited: bool
    trust_score: float
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)