from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
from app.models.database import User, Base
from app.core.security import get_password_hash

def reset_admin():
    # Create database engine
    engine = create_engine(settings.DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()

    try:
        # Remove existing admin user if any
        admin = db.query(User).filter(User.email == "admin@agrivoltaics.com").first()
        if admin:
            db.delete(admin)
            db.commit()
            print("Removed existing admin user")

        # Create new admin user
        admin_user = User(
            email="admin@agrivoltaics.com",  # Fixed email to match the search query
            hashed_password=get_password_hash("admin123"),
            full_name="Admin User",
            is_superuser=True,
            is_active=True
        )
        db.add(admin_user)
        db.commit()
        print("New admin user created successfully")
    except Exception as e:
        print(f"Error creating admin user: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    reset_admin()