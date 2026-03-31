from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
from app.db.session import get_db
from app.models.business import Business, VerificationStatus, User, UserRole
from app.schemas.business import BusinessCreate, BusinessOut, BusinessUpdate
from app.dependencies import get_current_user # To identify the owner

router = APIRouter(prefix="/businesses", tags=["Directory"])

# --- READ (Search & List) ---
@router.get("/", response_model=List[BusinessOut])
def list_directory(
    city: str = Query(None, description="Filter by Philippine City (e.g. Cebu City)"),
    accredited_only: bool = False,
    db: Session = Depends(get_db)
):
    """
    Retrieves businesses. 
    CRITICAL: Only shows businesses where the owner is still active (not soft-deleted).
    """
    # Join with User table to check if the owner is active/not deleted
    query = db.query(Business).join(User, Business.owner_id == User.id)
    
    # Global Filter: Hide businesses from blocked or soft-deleted users
    query = query.filter(User.is_active == True)
    
    if city:
        query = query.filter(Business.city.ilike(f"%{city}%"))
    
    if accredited_only:
        query = query.filter(Business.is_accredited == True)
        
    return query.all()

# --- CREATE ---
@router.post("/", response_model=BusinessOut, status_code=status.HTTP_201_CREATED)
def create_business(
    obj_in: BusinessCreate, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Creates a business and automatically links it to the logged-in owner.
    """
    slug = obj_in.name.lower().replace(" ", "-")
    
    existing = db.query(Business).filter(Business.slug == slug).first()
    if existing:
        slug = f"{slug}-{int(datetime.timestamp(datetime.now()))}"

    db_business = Business(
        **obj_in.model_dump(),
        slug=slug,
        owner_id=current_user.id, # Automatically link to the logged-in user
        verification_status=VerificationStatus.PENDING 
    )
    db.add(db_business)
    db.commit()
    db.refresh(db_business)
    return db_business

# --- UPDATE (Owner or Admin) ---
@router.patch("/{business_id}", response_model=BusinessOut)
def update_business(
    business_id: int, 
    obj_in: BusinessUpdate, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    db_business = db.query(Business).filter(Business.id == business_id).first()
    if not db_business:
        raise HTTPException(status_code=404, detail="Business not found")
    
    # Permission Check: Only the Owner or an Admin can edit
    if db_business.owner_id != current_user.id and current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Not authorized to edit this business")
    
    update_data = obj_in.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_business, key, value)
    
    db.commit()
    db.refresh(db_business)
    return db_business

# --- DELETE (Owner or Admin) ---
@router.delete("/{business_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_business(
    business_id: int, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    db_business = db.query(Business).filter(Business.id == business_id).first()
    if not db_business:
        raise HTTPException(status_code=404, detail="Business not found")
    
    # Permission Check
    if db_business.owner_id != current_user.id and current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Not authorized to delete this business")
    
    db.delete(db_business)
    db.commit()
    return None

# --- ADMIN ONLY: BBB ACCREDITATION ---
@router.patch("/{business_id}/verify", response_model=BusinessOut)
def verify_business(
    business_id: int, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Official Accreditation: Strictly Admin-only.
    """
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Only Admins can verify businesses")

    business = db.query(Business).filter(Business.id == business_id).first()
    if not business:
        raise HTTPException(status_code=404, detail="Business not found")
    
    business.verification_status = VerificationStatus.VERIFIED
    business.is_accredited = True
    
    if business.trust_score < 4.0:
        business.trust_score = 4.0
    
    db.commit()
    db.refresh(business)
    return business