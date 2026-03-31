import enum
from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum
from sqlalchemy.orm import relationship
from app.db.session import Base

class UserRole(str, enum.Enum):
    """
    Using str as a mixin so the Enum is JSON serializable 
    and works easily with your 'user_in.role == "owner"' checks.
    """
    ADMIN = "admin"
    OWNER = "owner"
    CONSUMER = "consumer"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(100), nullable=True)
    
    # Using the Enum defined above
    role = Column(Enum(UserRole), default=UserRole.CONSUMER)
    
    # BBB Logic: Useful for verifying reviewers or business owners
    is_identity_verified = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # --- RELATIONSHIPS ---
    
    # If a user is an 'owner', they can have multiple businesses
    owned_businesses = relationship("Business", back_populates="owner")
    
    # If a user is a 'consumer', they can leave many reviews
    # reviews = relationship("Review", back_populates="user")