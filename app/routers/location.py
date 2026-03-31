from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.location import City

router = APIRouter(prefix="/locations", tags=["Locations"])

@router.get("/cities")
def get_all_cities(db: Session = Depends(get_db)):
    # Returns all 146 cities sorted alphabetically
    return db.query(City).order_by(City.name.asc()).all()