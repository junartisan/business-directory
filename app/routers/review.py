@router.post("/{business_id}/reviews", response_model=ReviewOut)
def post_review(business_id: int, review_in: ReviewCreate, db: Session = Depends(get_db)):
    business = db.query(Business).filter(Business.id == business_id).first()
    if not business:
        raise HTTPException(status_code=404, detail="Business not found")
        
    new_review = Review(**review_in.model_dump(), business_id=business_id)
    db.add(new_review)
    
    # Update the business trust score immediately
    business.trust_score = calculate_trust_score(business)
    
    db.commit()
    db.refresh(new_review)
    return new_review

@router.post("/")
def create_review(
    review_in: ReviewCreate, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user) # The Protection
):
    # If the code reaches here, 'current_user' is a valid User object!
    new_review = Review(
        **review_in.model_dump(),
        user_name=current_user.full_name, # Automatically use their real name
        business_id=review_in.business_id
    )
    # ... save to DB ...