# app/routers/search.py
from fastapi import APIRouter, Depends, Query
from sqlalchemy import desc
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.business import Business, Category

router = APIRouter(prefix="/api/v1/search", tags=["Search"])

@router.get("/")
def advanced_search(
    q: str = None,
    city_id: int = None,
    category_id: int = None,
    featured_only: bool = False,
    db: Session = Depends(get_db)
):
    query = db.query(Business)

    # --- FILTERS ---
    if city_id:
        query = query.filter(Business.city_id == city_id)
    
    if category_id:
        # Include all sub-categories if a parent category is selected
        sub_ids = db.query(Category.id).filter(Category.parent_id == category_id).all()
        ids = [i[0] for i in sub_ids] + [category_id]
        query = query.filter(Business.category_id.in_(ids))

    if q:
        query = query.filter(Business.name.ilike(f"%{q}%"))

    if featured_only:
        query = query.filter(Business.is_accredited == True)

    # --- RANKING LOGIC (The "Featured" Boost) ---
    # 1. Show Accredited/Featured businesses first
    # 2. Then sort by Trust Score (Highest to Lowest)
    # 3. Finally, by newest established
    query = query.order_by(
        desc(Business.is_accredited), 
        desc(Business.trust_score),
        desc(Business.year_established)
    )

    return query.limit(20).all()