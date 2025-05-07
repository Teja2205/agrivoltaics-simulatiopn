from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from datetime import datetime, date, timedelta

from app.api.dependencies import get_current_user, get_db
from app.models import schemas
from app.models.database import User, WeatherData
from app.services.weather_service import WeatherService

router = APIRouter()

@router.get("/data", response_model=List[schemas.WeatherDataSimple])
async def get_weather_data(
    start_date: Optional[date] = Query(None, description="Start date for weather data"),
    end_date: Optional[date] = Query(None, description="End date for weather data"),
    latitude: Optional[float] = Query(None, ge=-90, le=90, description="Location latitude"),
    longitude: Optional[float] = Query(None, ge=-180, le=180, description="Location longitude"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    Get weather data for a specific location and date range
    """
    # If parameters not provided, use defaults
    if not start_date:
        start_date = datetime.now().date() - timedelta(days=7)
    if not end_date:
        end_date = datetime.now().date()
    if latitude is None or longitude is None:
        # Use default location
        latitude = 40.0
        longitude = -75.0
        
    weather_service = WeatherService(db)
    weather_data = weather_service.get_weather_data(
        location={"lat": latitude, "lng": longitude},
        start_date=start_date.isoformat(),
        end_date=end_date.isoformat()
    )
    
    # Process the data to ensure it matches the schema requirements
    processed_data = []
    for item in weather_data:
        # Ensure date is a string
        if isinstance(item.get("date"), datetime):
            item["date"] = item["date"].isoformat()
            
        # Ensure all required numeric fields have values
        defaults = {
            "temperature_high": 25.0,
            "temperature_low": 15.0,
            "humidity": 50.0,
            "precipitation": 0.0,
            "cloud_cover": 0.3,
            "wind_speed": 5.0,
            "wind_direction": 180.0,
            "solar_radiation": 5.0,
            "location_lat": latitude,
            "location_lng": longitude
        }
        
        # Apply defaults for any None values
        for field, default_value in defaults.items():
            if item.get(field) is None:
                item[field] = default_value
                
        processed_data.append(item)
    
    return processed_data

@router.post("/data", response_model=schemas.WeatherData)
async def create_weather_data(
    weather_data: schemas.WeatherDataCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    Create new weather data entry
    """
    db_weather = WeatherData(
        date=weather_data.date,
        location_lat=weather_data.location_lat,
        location_lng=weather_data.location_lng,
        temperature_high=weather_data.temperature_high,
        temperature_low=weather_data.temperature_low,
        humidity=weather_data.humidity,
        precipitation=weather_data.precipitation,
        cloud_cover=weather_data.cloud_cover,
        wind_speed=weather_data.wind_speed,
        wind_direction=weather_data.wind_direction,
        solar_radiation=weather_data.solar_radiation,
    )
    
    db.add(db_weather)
    db.commit()
    db.refresh(db_weather)
    return db_weather

@router.get("/data/{weather_id}", response_model=schemas.WeatherData)
async def get_weather_data_by_id(
    weather_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    Get specific weather data entry by ID
    """
    weather_data = db.query(WeatherData).filter(WeatherData.id == weather_id).first()
    if not weather_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Weather data not found",
        )
    return weather_data

@router.delete("/data/{weather_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_weather_data(
    weather_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Delete weather data entry
    """
    weather_data = db.query(WeatherData).filter(WeatherData.id == weather_id).first()
    if not weather_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Weather data not found",
        )
    
    db.delete(weather_data)
    db.commit()

@router.get("/forecast", response_model=List[schemas.WeatherDataSimple])
async def get_weather_forecast(
    latitude: float = Query(..., ge=-90, le=90, description="Location latitude"),
    longitude: float = Query(..., ge=-180, le=180, description="Location longitude"),
    days: int = Query(default=7, ge=1, le=14, description="Number of forecast days"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    Get weather forecast for a specific location
    """
    weather_service = WeatherService(db)
    start_date = datetime.now().date()
    end_date = start_date + timedelta(days=days)
    
    forecast = weather_service.get_weather_data(
        location={"lat": latitude, "lng": longitude},
        start_date=start_date.isoformat(),
        end_date=end_date.isoformat()
    )
    
    # Process the data to ensure it matches the schema requirements
    processed_data = []
    for item in forecast:
        # Ensure date is a string
        if isinstance(item.get("date"), datetime):
            item["date"] = item["date"].isoformat()
            
        # Ensure all required numeric fields have values
        defaults = {
            "temperature_high": 25.0,
            "temperature_low": 15.0,
            "humidity": 50.0,
            "precipitation": 0.0,
            "cloud_cover": 0.3,
            "wind_speed": 5.0,
            "wind_direction": 180.0,
            "solar_radiation": 5.0,
            "location_lat": latitude,
            "location_lng": longitude
        }
        
        # Apply defaults for any None values
        for field, default_value in defaults.items():
            if item.get(field) is None:
                item[field] = default_value
                
        processed_data.append(item)
    
    return processed_data