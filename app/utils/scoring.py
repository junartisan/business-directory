from sqlalchemy import func
from app.models.business import Review

def calculate_trust_score(db, business_id: int):
    # 1. Get all reviews for this business
    reviews = db.query(Review.rating).filter(Review.business_id == business_id).all()
    
    if not reviews:
        return 3.0  # Default neutral score for new businesses

    # 2. Basic Stats
    total_reviews = len(reviews)
    avg_rating = sum([r.rating for r in reviews]) / total_reviews
    
    # 3. Bayesian Logic (C=minimum reviews needed, m=prior average)
    # This prevents 1-review businesses from jumping to 5.0 instantly
    C = 5  # We want at least 5 reviews to be "confident"
    m = 3.0 # The "average" starting point
    
    bayesian_score = ( (C * m) + (total_reviews * avg_rating) ) / (C + total_reviews)
    
    # 4. Featured/Accredited Bonus (Optional)
    # You can add +0.5 if business.is_accredited is True
    
    return round(bayesian_score, 2)