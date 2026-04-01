import enum
from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum
from sqlalchemy.orm import relationship
from app.db.session import Base

class UserRole(str, enum.Enum):
    ADMIN = "admin"
    OWNER = "owner"
    CONSUMER = "consumer"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(100), nullable=True)
    
    role = Column(Enum(UserRole), default=UserRole.CONSUMER)
    
    is_identity_verified = Column(Boolean, default=False)
    is_active = Column(Boolean, default=False)  # User is "locked" until verified
    email_verified = Column(Boolean, default=False)
    verified_at = Column(DateTime, nullable=True)
    
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # --- RELATIONSHIPS ---
    
    # If a user is an 'owner', they can have multiple businesses
    owned_businesses = relationship("Business", back_populates="owner")
    
    # FIX: Added 'foreign_keys' to resolve the AmbiguousForeignKeysError.
    # Replace "Review.user_id" with the actual column name in your Review model 
    # that represents the person writing the review.
    reviews = relationship(
        "Review", 
        back_populates="user", 
        foreign_keys="Review.user_id" 
    )