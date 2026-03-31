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

# --- MODELS ---

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(100))
    role = Column(Enum(UserRole), default=UserRole.CONSUMER)
    
    is_identity_verified = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True) # Used for Admin "Blocking"
    deleted_at = Column(DateTime, nullable=True) # Used for User "Soft Delete"
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    owned_businesses = relationship("Business", back_populates="owner")
    reviews = relationship("Review", back_populates="user")

class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, index=True, nullable=False)
    icon = Column(String(50), nullable=True) 
    
    # Hierarchy Logic: Allows subcategories (e.g., Parent: Automotive -> Child: Battery Center)
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
    
    # --- UPDATED LOCATION LOGIC ---
    address = Column(String(255))
    # Links to your 146 Cities table. No more manual typing!
    city_id = Column(Integer, ForeignKey("cities.id"), index=True)
    
    phone = Column(String(20))
    email = Column(String(255))
    website = Column(String(255))

    # BBB-Style Fields
    verification_status = Column(Enum(VerificationStatus), default=VerificationStatus.UNVERIFIED)
    is_accredited = Column(Boolean, default=False)
    trust_score = Column(Float, default=0.0)
    year_established = Column(Integer)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Foreign Keys
    category_id = Column(Integer, ForeignKey("categories.id"))
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=True)

    # Relationship Objects
    # Access city/region via business.city.name or business.city.region
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
    
    created_at = Column(DateTime, default=datetime.utcnow)

    # Foreign Keys
    business_id = Column(Integer, ForeignKey("businesses.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    user_name = Column(String(100), nullable=False)

    # Relationships
    business = relationship("Business", back_populates="reviews")
    user = relationship("User", back_populates="reviews")

    __table_args__ = (
        CheckConstraint('rating >= 1 AND rating <= 5', name='check_rating_range'),
    )