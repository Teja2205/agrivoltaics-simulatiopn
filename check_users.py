# Create a file named check_users.py with this content:
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
from app.models.database import User

def check_users():
    # Create engine
    engine = create_engine(settings.DATABASE_URL)
    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()
    
    try:
        # Get all users
        users = db.query(User).all()
        
        if not users:
            print("No users found in the database!")
            return
        
        print(f"Found {len(users)} users in the database:")
        for i, user in enumerate(users, 1):
            print(f"\nUser {i}:")
            print(f"  ID: {user.id}")
            print(f"  Email: {user.email}")
            print(f"  Is active: {user.is_active}")
            print(f"  Is superuser: {user.is_superuser}")
            # Don't print the password hash for security reasons
            print(f"  Has password: {'Yes' if user.hashed_password else 'No'}")
        
        # Check for crop data
        crop_count = db.query(User).count()
        print(f"\nCrop data count: {crop_count}")
    finally:
        db.close()

if __name__ == "__main__":
    check_users()