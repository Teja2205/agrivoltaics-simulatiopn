import json
import sys
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime

# Adjust the path to import from your app
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app.models.database import CropData, Base
from app.core.config import settings

def load_crop_data(json_file):
    # Create database connection
    engine = create_engine(settings.DATABASE_URL)
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()
    
    # Load JSON data
    with open(json_file, 'r') as f:
        crops = json.load(f)
    
    # Check if crops already exist
    existing_crops = {crop.name for crop in db.query(CropData).all()}
    
    # Insert crops that don't already exist
    for crop_data in crops:
        if crop_data['name'] not in existing_crops:
            # Create crop object
            crop = CropData(
                name=crop_data['name'],
                scientific_name=crop_data['scientific_name'],
                growth_period_days=crop_data['growth_period_days'],
                optimal_temperature_min=crop_data['optimal_temperature_min'],
                optimal_temperature_max=crop_data['optimal_temperature_max'],
                water_requirement_mm_day=crop_data['water_requirement_mm_day'],
                shade_tolerance=crop_data['shade_tolerance'],
                typical_yield_per_sqm=crop_data['typical_yield_per_sqm'],
                planting_depth_cm=crop_data['planting_depth_cm'],
                row_spacing_cm=crop_data['row_spacing_cm'],
                plant_spacing_cm=crop_data['plant_spacing_cm'],
                properties=crop_data['properties'],
                created_at=datetime.now()
            )
            db.add(crop)
            print(f"Added crop: {crop_data['name']}")
        else:
            print(f"Crop already exists: {crop_data['name']}")
    
    # Commit changes
    db.commit()
    db.close()
    print("Crop data loading complete")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python load_crop_data.py <json_file>")
        sys.exit(1)
    
    json_file = sys.argv[1]
    load_crop_data(json_file)