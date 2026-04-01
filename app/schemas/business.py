from pydantic import BaseModel, ConfigDict, HttpUrl
from typing import Optional, List
from datetime import datetime
from app.models.business import VerificationStatus



class ReviewOut(BaseModel):
    id: int
    rating: int
    comment: Optional[str]
    user_name: str
    owner_reply: Optional[str]
    owner_reply_at: Optional[datetime]
    is_verified_purchase: bool
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)
    
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
    
    # Add this line so reviews show up in the JSON response
    reviews: List[ReviewOut] = [] 

    model_config = ConfigDict(from_attributes=True)
    
    
class BusinessSummaryOut(BusinessBase):
    """Used for high-speed Search Results and Category Lists"""
    id: int
    slug: str
    trust_score: float
    is_accredited: bool
    verification_status: VerificationStatus
    
    # We can add a simple count instead of the full review list
    review_count: int = 0 

    model_config = ConfigDict(from_attributes=True)

class BusinessOut(BusinessSummaryOut):
    """Used for the dedicated Business Profile page"""
    address: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    created_at: datetime
    
    # This is where the heavy data lives
    reviews: List[ReviewOut] = []