from fastapi import APIRouter, Depends, Query, HTTPException, status, File
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
from app.db.session import get_db
from app.models.business import Business, VerificationStatus, User, UserRole, Review, ReviewStatus
from app.schemas.business import BusinessCreate, BusinessOut, BusinessUpdate, BusinessSummaryOut
from app.dependencies import get_current_user # To identify the owner
from app.utils.uploads import save_upload_file


router = APIRouter(prefix="/businesses", tags=["Directory"])

# --- READ (Search & List) ---
@router.get("/", response_model=List[BusinessSummaryOut])
def list_directory(
    city: str = Query(None, description="Filter by Philippine City"),
    category_id: int = Query(None),
    accredited_only: bool = False,
    db: Session = Depends(get_db)
):
    """
    Retrieves a list of businesses with a summary of their ratings.
    Includes only businesses with active owners.
    """
    # 1. Base Query: Join Business with User (to check activity) 
    # and Outer Join with Review (to count approved reviews)
    query = db.query(
        Business, 
        func.count(Review.id).filter(Review.status == ReviewStatus.APPROVED).label("review_count")
    ).join(User, Business.owner_id == User.id) \
     .outerjoin(Review, Business.id == Review.business_id) \
     .filter(User.is_active == True)

    # 2. Apply Filters
    if city:
        query = query.filter(Business.city.ilike(f"%{city}%"))
    
    if accredited_only:
        query = query.filter(Business.is_accredited == True)

    if category_id:
        # Fetch child categories to include sub-category results
        sub_ids = db.query(Category.id).filter(Category.parent_id == category_id).all()
        ids = [i[0] for i in sub_ids] + [category_id]
        query = query.filter(Business.category_id.in_(ids))

    # 3. Group by and Order
    # Ordering by Accreditation first, then Trust Score keeps the top businesses at the top
    query = query.group_by(Business.id) \
                 .order_by(Business.is_accredited.desc(), Business.trust_score.desc())
    
    results = query.all()
    
    # 4. Map the review_count label back to the Business object
    # This allows Pydantic's BusinessSummaryOut to find the 'review_count' field
    final_list = []
    for business, review_count in results:
        business.review_count = review_count
        final_list.append(business)
        
    return final_list


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

@router.get("/{slug}", response_model=BusinessOut)
def get_business_by_slug(slug: str, db: Session = Depends(get_db)):
    # 1. Fetch the business by its unique slug
    business = db.query(Business).filter(Business.slug == slug).first()
    
    if not business:
        raise HTTPException(status_code=404, detail="Business not found")
    
    # 2. Security Check: Ensure the owner is still active
    if not business.owner.is_active:
        raise HTTPException(status_code=403, detail="This business profile is currently inactive")

    # 3. Filter for ONLY Approved Reviews
    # We manually filter these so the Pydantic schema only serializes the safe ones
    approved_reviews = db.query(Review).filter(
        Review.business_id == business.id,
        Review.status == ReviewStatus.APPROVED
    ).all()
    
    # We attach the filtered list to the object before returning
    business.reviews = approved_reviews
    
    return business

@router.post("/businesses/{business_id}/logo")
async def upload_business_logo(business_id: int, file: UploadFile = File(...)):
    # Save the file to disk using our utility
    file_url = save_upload_file(file, folder="logos")
    
    # Now update your SQLAlchemy model
    # business = db.query(Business).filter(Business.id == business_id).first()
    # business.logo_url = file_url
    # db.commit()
    
    return {"logo_url": file_url}