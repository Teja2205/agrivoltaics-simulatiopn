

# Create a Python file named check_db.py with this content:
from sqlalchemy import create_engine, inspect
from app.core.config import settings

def check_database():
    # Create engine
    engine = create_engine(settings.DATABASE_URL)
    
    # Get inspector
    inspector = inspect(engine)
    
    # Get all table names
    table_names = inspector.get_table_names()
    
    print("Database tables found:", table_names)
    
    # Check if required tables exist
    required_tables = ['users', 'crop_data', 'simulations', 'configurations', 'weather_data']
    for table in required_tables:
        if table in table_names:
            print(f"✓ Table '{table}' exists")
            # Print row count
            try:
                result = engine.execute(f"SELECT COUNT(*) FROM {table}")
                count = result.scalar()
                print(f"  - Row count: {count}")
            except Exception as e:
                print(f"  - Error counting rows: {e}")
        else:
            print(f"✗ Table '{table}' is missing")

if __name__ == "__main__":
    check_database()