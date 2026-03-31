import json
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.models.business import Category

def seed_master_categories():
    db: Session = SessionLocal()
    
    # Load the master JSON we created
    try:
        with open("categories.json", "r") as f:
            data = json.load(f)

        print("--- Starting Master Category Seed ---")
        
        for item in data:
            # 1. Handle Parent Category
            parent = db.query(Category).filter(Category.name == item["name"]).first()
            if not parent:
                parent = Category(
                    name=item["name"], 
                    icon=item["icon"], 
                    parent_id=None
                )
                db.add(parent)
                db.commit()
                db.refresh(parent)
                print(f"📁 Created Parent: {parent.name}")

            # 2. Handle Sub-Categories (The "Details")
            for sub in item["sub_categories"]:
                sub_exists = db.query(Category).filter(
                    Category.name == sub["name"], 
                    Category.parent_id == parent.id
                ).first()
                
                if not sub_exists:
                    new_sub = Category(
                        name=sub["name"], 
                        icon=sub["icon"], 
                        parent_id=parent.id
                    )
                    db.add(new_sub)
                    print(f"   └─ ✅ Added Sub: {sub['name']}")
        
        db.commit()
        print("--- Category Seeding Complete ---")

    except Exception as e:
        print(f"❌ Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_master_categories()