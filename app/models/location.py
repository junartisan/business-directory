from sqlalchemy import Column, Integer, String
from app.db.session import Base

class City(Base):
    __tablename__ = "cities"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, index=True, nullable=False)
    region = Column(String(100)) # e.g., "NCR", "Region VII"
    province = Column(String(100)) # e.g., "Cebu", "Davao del Sur"