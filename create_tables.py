import os
import sys

# Add the current directory to the path
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

# Import SQLAlchemy components and models
try:
    from sqlalchemy import create_engine
    from app.database import Base
    from app.core.config import settings
    
    # Import all your models to ensure they're registered with the Base metadata
    from app.models.database import User, Simulation, Configuration, WeatherData, CropData
    
    print("Successfully imported database models")
except ImportError as e:
    print(f"Error importing modules: {e}")
    print("Make sure your project structure is set up correctly")
    sys.exit(1)

def create_tables():
    print("Creating database tables...")
    try:
        # Create database engine
        print(f"Using database URL: {settings.DATABASE_URL}")
        print(f"Database URL type: {type(settings.DATABASE_URL)}")
        print(f"Database URL repr: {repr(settings.DATABASE_URL)}")
        engine = create_engine(settings.DATABASE_URL)
        
        # Create all tables defined in the Base metadata
        Base.metadata.create_all(bind=engine)
        
        print("Database tables created successfully")
    except Exception as e:
        print(f"Error creating database tables: {e}")
        sys.exit(1)

if __name__ == "__main__":
    create_tables()