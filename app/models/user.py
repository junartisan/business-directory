import enum
from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum
from sqlalchemy.orm import relationship
from app.db.base_class import Base


class UserRole(str, enum.Enum):
    CONSUMER = "consumer"
    OWNER = "owner"
    ADMIN = "admin"
    

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(100))
    role = Column(Enum(UserRole), default=UserRole.CONSUMER)
    
    email_verified = Column(Boolean, default=False)
    is_identity_verified = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True) 
    deleted_at = Column(DateTime, nullable=True) 
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # --- UPDATED RELATIONSHIPS ---
    owned_businesses = relationship("Business", back_populates="owner")
    
    # We specify foreign_keys here so SQLAlchemy knows which ID connects a user to their reviews
    reviews = relationship(
        "Review", 
        back_populates="user", 
        foreign_keys="Review.user_id"
    )
    
    # New relationship for admins to see what they have moderated
    moderated_reviews = relationship(
        "Review", 
        back_populates="moderator", 
        foreign_keys="Review.moderator_id"
    )
