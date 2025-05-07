import sys
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
from app.models.database import User
from app.core.security import get_password_hash

def create_admin_user():
    # Create database engine
    engine = create_engine(settings.DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()

    try:
        # Check if admin user already exists
        admin = db.query(User).filter(User.email == "admin@agrivoltaics.com").first()
        if admin:
            print("Admin user already exists")
            return

        # Create admin user
        admin_user = User(
            email="admin@agrivoltaics.com",
            hashed_password=get_password_hash("agri123"),
            full_name="Admin User",
            is_superuser=True,
            is_active=True
        )
        db.add(admin_user)
        db.commit()
        print("Admin user created successfully")
    except Exception as e:
        print(f"Error creating admin user: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    create_admin_user() 