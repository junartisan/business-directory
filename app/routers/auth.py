from fastapi import APIRouter, Depends, HTTPException, status, Request, BackgroundTasks
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
import secrets
from datetime import datetime

from app.db.session import get_db
from app.models.business import User, UserRole
from app.core import security
from app.core.security import create_access_token, get_password_hash, create_verification_token
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

# --- REGISTRATION & LOGIN (Standard) ---
@router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
async def register_user(
    user_in: UserCreate, 
    background_tasks: BackgroundTasks, 
    db: Session = Depends(get_db)
):
    # 1. Check if user exists
    existing_user = db.query(User).filter(User.email == user_in.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # 2. Create the new user (Locked by default)
    new_user = User(
        email=user_in.email,
        hashed_password=get_password_hash(user_in.password),
        full_name=user_in.full_name,
        role=UserRole.OWNER if user_in.role == "owner" else UserRole.CONSUMER,
        is_identity_verified=False,
        is_active=False,  # <--- CRITICAL: User cannot log in yet
        email_verified=False
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # 3. Handle Email Verification
    # Create a token (e.g., a timed JWT or a random UUID)
    verification_token = create_verification_token(new_user.email)
    
    # Send email in the background so the user doesn't wait for the SMTP server
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
    # 1. Look for the user by email only first
    user = db.query(User).filter(User.email == form_data.username).first()
    
    # 2. Check if user exists and if password is correct
    if not user or not security.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Incorrect email or password"
        )
    
    # 3. CRITICAL: Check if the account is active/verified
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Account is inactive. Please verify your email address before logging in."
        )
    
    # 4. If all checks pass, issue the token
    return {
        "access_token": security.create_access_token(user.id), 
        "token_type": "bearer"
    }


# --- USER MANAGEMENT (SOFT DELETE & BLOCKING) ---

@router.delete("/me", status_code=status.HTTP_200_OK)
def deactivate_own_account(
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    """
    Allows a User/Owner to 'delete' their own profile. 
    Data remains in DB but is marked as inactive and hidden.
    """
    current_user.is_active = False
    # If you added the deleted_at column to your model:
    # current_user.deleted_at = datetime.utcnow() 
    db.commit()
    return {"message": "Account deactivated successfully."}

@router.patch("/admin/users/{user_id}/manage", status_code=status.HTTP_200_OK)
def admin_manage_user(
    user_id: int, 
    action: str, # expected values: "block", "unblock", "soft-delete"
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Strictly for Admins to manage users.
    """
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Not authorized to perform admin actions")

    target_user = db.query(User).filter(User.id == user_id).first()
    if not target_user:
        raise HTTPException(status_code=404, detail="User not found")

    if action == "block":
        target_user.is_active = False
    elif action == "unblock":
        target_user.is_active = True
    elif action == "soft-delete":
        target_user.is_active = False
        # target_user.deleted_at = datetime.utcnow() 
    
    db.commit()
    return {"message": f"User {action}ed successfully."}

# --- SSO CALLBACKS ---

async def handle_sso_callback(user_data, db: Session):
    user = db.query(User).filter(User.email == user_data.email).first()
    if not user:
        user = User(
            email=user_data.email,
            full_name=user_data.display_name,
            hashed_password=get_password_hash(secrets.token_urlsafe(24)), 
            is_identity_verified=True,
            role=UserRole.CONSUMER
        )
        db.add(user)
        db.commit()
        db.refresh(user)
    
    if not user.is_active:
        raise HTTPException(status_code=403, detail="Account is blocked or deactivated")
        
    return create_access_token(user.id)

@router.get("/google/callback")
async def google_callback(request: Request, db: Session = Depends(get_db)):
    user_data = await google_sso.verify_and_process(request)
    token = await handle_sso_callback(user_data, db)
    return {"access_token": token, "token_type": "bearer"}

@router.get("/facebook/callback")
async def facebook_callback(request: Request, db: Session = Depends(get_db)):
    user_data = await facebook_sso.verify_and_process(request)
    token = await handle_sso_callback(user_data, db)
    return {"access_token": token, "token_type": "bearer"}

@router.get("/verify-email")
async def verify_email(token: str, db: Session = Depends(get_db)):
    # 1. Decode/Validate the token (check if it's expired)
    email = get_email_from_token(token) 
    
    if not email:
        raise HTTPException(status_code=400, detail="Invalid or expired token")
        
    # 2. Find the user
    user = db.query(User).filter(User.email == email).first()
    
    # 3. Activate them
    user.is_active = True
    user.email_verified = True
    user.verified_at = datetime.utcnow()
    db.commit()
    
    return {"message": "Email successfully verified! You can now log in."}