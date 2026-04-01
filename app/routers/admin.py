# app/routers/admin.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.business import Review, ReviewStatus
from app.auth.deps import get_admin_user # Your dependency for role='admin'

router = APIRouter(prefix="/api/v1/admin", tags=["Admin Dashboard"])

@router.get("/reviews/pending")
def get_pending_reviews(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    """List all reviews waiting for moderation."""
    return db.query(Review).filter(Review.status == ReviewStatus.PENDING).all()

@router.patch("/reviews/{review_id}/approve")
def approve_review(
    review_id: int, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    review = db.query(Review).get(review_id)
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")

    # 1. Update status
    review.status = ReviewStatus.APPROVED
    review.moderated_at = datetime.utcnow()
    review.moderator_id = current_user.id

    # 2. Recalculate the business trust score NOW
    # Since it's approved, it should finally count towards the total
    business = review.business
    business.trust_score = calculate_trust_score(db, business.id)
    
    db.commit()
    return {"status": "Review Approved", "new_trust_score": business.trust_score}