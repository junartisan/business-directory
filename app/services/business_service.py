from sqlalchemy.orm import Session
from app.models.business import Business, VerificationStatus

def verify_business(db: Session, business_id: int):
    """
    Simulates the BBB Accreditation process.
    In a real app, you'd check for DTI/SEC permits here.
    """
    business = db.query(Business).filter(Business.id == business_id).first()
    if business:
        business.verification_status = VerificationStatus.VERIFIED
        business.is_accredited = True
        # Initial trust score for passing verification
        business.trust_score = 4.0 
        db.commit()
        db.refresh(business)
    return business