import enum
from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Enum, Float, Text, CheckConstraint
from sqlalchemy.orm import relationship, backref
from app.db.session import Base

# --- ENUMS ---

class VerificationStatus(enum.Enum):
    UNVERIFIED = "unverified"
    PENDING = "pending"
    VERIFIED = "verified"
    SUSPENDED = "suspended"

class UserRole(str, enum.Enum):
    CONSUMER = "consumer"
    OWNER = "owner"
    ADMIN = "admin"

class ReviewStatus(enum.Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    FLAGGED = "flagged"

# --- MODELS ---

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(100))
    role = Column(Enum(UserRole), default=UserRole.CONSUMER)
    
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

class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, index=True, nullable=False)
    icon = Column(String(50), nullable=True) 
    parent_id = Column(Integer, ForeignKey("categories.id"), nullable=True)
    
    subcategories = relationship(
        "Category", 
        backref=backref("parent", remote_side=[id])
    )
    businesses = relationship("Business", back_populates="category")

class Business(Base):
    __tablename__ = "businesses"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    slug = Column(String(255), unique=True, index=True)
    description = Column(Text, nullable=True)
    address = Column(String(255))
    city_id = Column(Integer, ForeignKey("cities.id"), index=True)
    phone = Column(String(20))
    email = Column(String(255))
    website = Column(String(255))

    verification_status = Column(Enum(VerificationStatus), default=VerificationStatus.UNVERIFIED)
    is_accredited = Column(Boolean, default=False)
    trust_score = Column(Float, default=0.0)
    year_established = Column(Integer)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    category_id = Column(Integer, ForeignKey("categories.id"))
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=True)

    # --- RELATIONSHIP OBJECTS ---
    city = relationship("City", backref="businesses")
    category = relationship("Category", back_populates="businesses")
    owner = relationship("User", back_populates="owned_businesses")
    reviews = relationship("Review", back_populates="business", cascade="all, delete-orphan")

class Review(Base):
    __tablename__ = "reviews"

    id = Column(Integer, primary_key=True, index=True)
    rating = Column(Integer, nullable=False)
    comment = Column(Text, nullable=True)
    is_verified_purchase = Column(Boolean, default=False)
    owner_reply = Column(Text, nullable=True)
    owner_reply_at = Column(DateTime, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    business_id = Column(Integer, ForeignKey("businesses.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=False)
    user_name = Column(String(100), nullable=False)
    
    status = Column(Enum(ReviewStatus), default=ReviewStatus.PENDING)
    moderated_at = Column(DateTime, nullable=True)
    moderator_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    logo_url = Column(String(255), nullable=True)  # Store path like "/static/uploads/logos/sm_mall.png"
    banner_url = Column(String(255), nullable=True)

    # --- UPDATED RELATIONSHIPS ---
    business = relationship("Business", back_populates="reviews")
    
    # Specify which Foreign Key matches the 'user' (the author)
    user = relationship(
        "User", 
        back_populates="reviews", 
        foreign_keys=[user_id]
    )
    
    # Specify which Foreign Key matches the 'moderator'
    moderator = relationship(
        "User", 
        back_populates="moderated_reviews", 
        foreign_keys=[moderator_id]
    )

    __table_args__ = (
        CheckConstraint('rating >= 1 AND rating <= 5', name='check_rating_range'),
    )