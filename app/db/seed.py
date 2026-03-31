from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.models.location import City

def seed_philippine_cities():
    db: Session = SessionLocal()
    
    # Categorized Cities for the entire Philippines
    ph_cities = [
        # NCR (National Capital Region)
        {"name": "Manila", "region": "NCR", "province": "Metro Manila"},
        {"name": "Quezon City", "region": "NCR", "province": "Metro Manila"},
        {"name": "Caloocan", "region": "NCR", "province": "Metro Manila"},
        {"name": "Las Piñas", "region": "NCR", "province": "Metro Manila"},
        {"name": "Makati", "region": "NCR", "province": "Metro Manila"},
        {"name": "Malabon", "region": "NCR", "province": "Metro Manila"},
        {"name": "Mandaluyong", "region": "NCR", "province": "Metro Manila"},
        {"name": "Marikina", "region": "NCR", "province": "Metro Manila"},
        {"name": "Muntinlupa", "region": "NCR", "province": "Metro Manila"},
        {"name": "Navotas", "region": "NCR", "province": "Metro Manila"},
        {"name": "Parañaque", "region": "NCR", "province": "Metro Manila"},
        {"name": "Pasay", "region": "NCR", "province": "Metro Manila"},
        {"name": "Pasig", "region": "NCR", "province": "Metro Manila"},
        {"name": "San Juan", "region": "NCR", "province": "Metro Manila"},
        {"name": "Taguig", "region": "NCR", "province": "Metro Manila"},
        {"name": "Valenzuela", "region": "NCR", "province": "Metro Manila"},
        
        # Region VII (Central Visayas - Your Core Area)
        {"name": "Cebu City", "region": "Region VII", "province": "Cebu"},
        {"name": "Lapu-Lapu City", "region": "Region VII", "province": "Cebu"},
        {"name": "Mandaue City", "region": "Region VII", "province": "Cebu"},
        {"name": "Talisay City", "region": "Region VII", "province": "Cebu"},
        {"name": "Danao City", "region": "Region VII", "province": "Cebu"},
        {"name": "Toledo City", "region": "Region VII", "province": "Cebu"},
        {"name": "Bogo City", "region": "Region VII", "province": "Cebu"},
        {"name": "Carcar City", "region": "Region VII", "province": "Cebu"},
        {"name": "Naga City", "region": "Region VII", "province": "Cebu"},
        {"name": "Tagbilaran City", "region": "Region VII", "province": "Bohol"},
        {"name": "Dumaguete City", "region": "Region VII", "province": "Negros Oriental"},
        
        # Region XI (Davao Region)
        {"name": "Davao City", "region": "Region XI", "province": "Davao del Sur"},
        {"name": "Digos City", "region": "Region XI", "province": "Davao del Sur"},
        {"name": "Tagum City", "region": "Region XI", "province": "Davao del Norte"},
        {"name": "Panabo City", "region": "Region XI", "province": "Davao del Norte"},
        
        # Northern Luzon / Region I & II
        {"name": "Baguio City", "region": "CAR", "province": "Benguet"},
        {"name": "Laoag City", "region": "Region I", "province": "Ilocos Norte"},
        {"name": "Vigan City", "region": "Region I", "province": "Ilocos Sur"},
        {"name": "Tuguegarao City", "region": "Region II", "province": "Cagayan"},
        
        # ... (Include the remaining 100+ cities in a similar format)
    ]

    print("--- Seeding PH Cities ---")
    for city_data in ph_cities:
        exists = db.query(City).filter(City.name == city_data["name"]).first()
        if not exists:
            db_city = City(**city_data)
            db.add(db_city)
            print(f"Added: {city_data['name']}")
    
    db.commit()
    db.close()
    print("--- City Seeding Complete ---")

if __name__ == "__main__":
    seed_philippine_cities()