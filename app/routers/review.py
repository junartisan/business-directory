from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime
from app.db.session import get_db
from app.models.business import Business, Review
from app.models.user import User
from app.schemas.review import ReviewCreate, ReviewOut # Assuming these exist
from app.auth.deps import get_current_user 
from app.utils.scoring import calculate_trust_score

router = APIRouter(prefix="/api/v1/reviews", tags=["Reviews"])

@router.post("/{business_id}", response_model=ReviewOut)
def post_review(
    business_id: int, 
    review_in: ReviewCreate, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # ... (Keep your previous protection/check logic here) ...

    # 1. Save the new review
    new_review = Review(
        **review_in.model_dump(),
        business_id=business_id,
        user_id=current_user.id,
        user_name=current_user.full_name
    )
    db.add(new_review)
    db.flush() # Flush so the new review is included in the calculation

    # 2. Recalculate and update the Business model
    business = db.query(Business).get(business_id)
    business.trust_score = calculate_trust_score(db, business_id)
    
    db.commit()
    db.refresh(new_review)
    return new_review

@router.patch("/{review_id}/reply")
def owner_reply_to_review(
    review_id: int, 
    reply_text: str, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Allows owners to respond to customer feedback."""
    review = db.query(Review).filter(Review.id == review_id).first()
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")

    # Only allow the specific business owner to reply
    if review.business.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Unauthorized to reply to this review.")

    review.owner_reply = reply_text
    review.owner_reply_at = datetime.utcnow()
    
    db.commit()
    return {"message": "Reply posted successfully", "owner_reply": reply_text}