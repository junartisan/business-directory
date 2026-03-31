import json
import os
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.models.location import City  # Adjust based on your folder structure

def import_ph_cities():
    # 1. Start a database session
    db: Session = SessionLocal()
    
    # 2. Locate the JSON file
    json_path = os.path.join(os.getcwd(), "cities.json")
    
    if not os.path.exists(json_path):
        print(f"❌ Error: Could not find {json_path}")
        return

    try:
        with open(json_path, "r") as f:
            cities_data = json.load(f)

        print(f"--- Starting Import of {len(cities_data)} Cities ---")

        for item in cities_data:
            # Check if city already exists by name to prevent duplicates
            existing_city = db.query(City).filter(City.name == item["name"]).first()
            
            if not existing_city:
                new_city = City(
                    name=item["name"],
                    region=item["region"],
                    province=item["province"]
                )
                db.add(new_city)
                print(f"✅ Added: {item['name']}")
            else:
                # Optional: Update existing city info if it changed
                existing_city.region = item["region"]
                existing_city.province = item["province"]
                print(f"🟡 Updated: {item['name']}")

        # 3. Commit all changes at once for speed
        db.commit()
        print("--- Import Successful! ---")

    except Exception as e:
        print(f"❌ An error occurred: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    import_ph_cities()