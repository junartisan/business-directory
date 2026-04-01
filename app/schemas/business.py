from pydantic import BaseModel, ConfigDict
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
    # --- ADDED FOR IMAGES ---
    logo_url: Optional[str] = None
    banner_url: Optional[str] = None

class BusinessCreate(BusinessBase):
    pass 

class BusinessUpdate(BaseModel):
    name: Optional[str] = None
    verification_status: Optional[VerificationStatus] = None
    is_accredited: Optional[bool] = None
    trust_score: Optional[float] = None
    # Allow updating images via standard update if needed
    logo_url: Optional[str] = None
    banner_url: Optional[str] = None

class BusinessSummaryOut(BusinessBase):
    """Used for high-speed Search Results and Category Lists"""
    id: int
    slug: str
    trust_score: float
    is_accredited: bool
    verification_status: VerificationStatus
    
    # logo_url is inherited from BusinessBase, so it will show up here!
    review_count: int = 0 

    model_config = ConfigDict(from_attributes=True)

class BusinessOut(BusinessSummaryOut):
    """Used for the dedicated Business Profile page"""
    address: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    created_at: datetime
    
    # Both logo_url and banner_url are inherited and will be included here
    reviews: List[ReviewOut] = []
    
    model_config = ConfigDict(from_attributes=True)