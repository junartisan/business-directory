from app.db.session import SessionLocal
from app.models.business import User, UserRole
from app.core.security import get_password_hash

def create_first_admin():
    db = SessionLocal()
    try:
        # Check if admin already exists
        admin_email = "admin@philippinecities.com" # Change to your email
        existing_admin = db.query(User).filter(User.email == admin_email).first()
        
        if not existing_admin:
            admin_user = User(
                email=admin_email,
                hashed_password=get_password_hash("Access@2026"),
                full_name="Rowena Grace",
                role=UserRole.ADMIN,
                is_identity_verified=True
            )
            db.add(admin_user)
            db.commit()
            print(f"Admin {admin_email} created successfully!")
        else:
            print("Admin already exists.")
    finally:
        db.close()

if __name__ == "__main__":
    create_first_admin()