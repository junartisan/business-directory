from fastapi import APIRouter, Depends, HTTPException, status, Request, BackgroundTasks
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
import secrets
from datetime import datetime

from app.db.session import get_db
# --- FIXED IMPORT: Use the specific user model file ---
from app.models.user import User, UserRole
from app.core import security
from app.core.security import (
    create_access_token, 
    get_password_hash, 
    create_verification_token,
    decode_verification_token # Ensure this exists in your security.py
)
from app.dependencies import get_current_user
from app.schemas.user import UserCreate, UserOut
from app.core.config import settings
from app.core.mail import send_verification_email

# SSO Imports
from fastapi_sso.sso.google import GoogleSSO
from fastapi_sso.sso.facebook import FacebookSSO

router = APIRouter(tags=["Authentication"])

# SSO Configuration
google_sso = GoogleSSO(settings.GOOGLE_CLIENT_ID, settings.GOOGLE_CLIENT_SECRET, settings.GOOGLE_REDIRECT_URI)
facebook_sso = FacebookSSO(settings.FB_CLIENT_ID, settings.FB_CLIENT_SECRET, settings.FB_REDIRECT_URI)

# --- REGISTRATION & LOGIN ---

@router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
async def register_user(
    user_in: UserCreate, 
    background_tasks: BackgroundTasks, 
    db: Session = Depends(get_db)
):
    existing_user = db.query(User).filter(User.email == user_in.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # This will now work because 'User' is imported from app.models.user
    new_user = User(
        email=user_in.email,
        hashed_password=get_password_hash(user_in.password),
        full_name=user_in.full_name,
        role=UserRole.OWNER if user_in.role == "owner" else UserRole.CONSUMER,
        is_identity_verified=False,
        is_active=False, 
        email_verified=False
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    verification_token = create_verification_token(new_user.email)
    
    background_tasks.add_task(
        send_verification_email, 
        new_user.email, 
        verification_token
    )

    return new_user

@router.post("/login/access-token")
def login_access_token(
    db: Session = Depends(get_db), 
    form_data: OAuth2PasswordRequestForm = Depends()
):
    user = db.query(User).filter(User.email == form_data.username).first()
    
    if not user or not security.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Incorrect email or password"
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Account is inactive. Please verify your email address before logging in."
        )
    
    return {
        "access_token": security.create_access_token(user.id), 
        "token_type": "bearer"
    }

# --- EMAIL VERIFICATION ---

@router.get("/verify-email")
async def verify_email(token: str, db: Session = Depends(get_db)):
    # Use your security utility to decode the token
    email = decode_verification_token(token) 
    
    if not email:
        raise HTTPException(status_code=400, detail="Invalid or expired token")
        
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
        
    user.is_active = True
    user.email_verified = True
    user.verified_at = datetime.utcnow()
    db.commit()
    
    return {"message": "Email successfully verified! You can now log in."}

# ... (Rest of your SSO and Admin routes remain the same)