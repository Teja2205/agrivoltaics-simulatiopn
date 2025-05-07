# crop_prediction.py (to be placed in app/api/routers/)
# At the top of crop_prediction.py, add these imports
import pandas as pd
import numpy as np
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import Dict, Any, List, Optional
from datetime import date

from app.api.dependencies import get_current_user, get_db
from app.models import schemas
from app.models.database import User, CropData
from app.services.ml_service import MLService
from app.services.weather_service import WeatherService

router = APIRouter()

@router.post("/predict", response_model=schemas.CropYieldPrediction)
async def predict_crop_yield(
    prediction_request: schemas.CropYieldPredictionRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    Predict crop yield based on weather, panel configuration, and crop type
    """
    # Initialize services
    ml_service = MLService()
    weather_service = WeatherService(db)
    
    # Validate crop exists
    crop_data = db.query(CropData).filter(CropData.name == prediction_request.crop_type).first()
    if not crop_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Crop type '{prediction_request.crop_type}' not found",
        )
    
    # Get weather data for prediction period
    weather_data = weather_service.get_weather_data(
        location={"lat": prediction_request.latitude, "lng": prediction_request.longitude},
        start_date=prediction_request.start_date,
        end_date=prediction_request.end_date
    )
    
    if not weather_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to retrieve weather data for specified location and period",
        )
    
    # Prepare panel configuration 
    panel_config = {
        "panel_height": prediction_request.panel_height,
        "panel_angle": prediction_request.panel_angle,
        "panel_spacing": prediction_request.panel_spacing,
        "irrigation_amount": prediction_request.irrigation_amount,
        "field_size": prediction_request.field_size,
        "shadow_coverage_percent": prediction_request.shadow_coverage_percent
    }
    
    # Convert crop data to dict format required by ML service
    crop_dict = {
        "optimal_temp_min": crop_data.optimal_temperature_min,
        "optimal_temp_max": crop_data.optimal_temperature_max,
        "water_requirement_mm_day": crop_data.water_requirement_mm_day,
        "shade_tolerance": crop_data.shade_tolerance,
        "typical_yield_per_sqm": crop_data.typical_yield_per_sqm,
        "growth_period_days": crop_data.growth_period_days
    }
    
    try:
        # Convert weather data to DataFrame
        weather_df = pd.DataFrame(weather_data)
        
        # Predict crop growth factors
        daily_growth = ml_service.predict_crop_growth(
            weather_df, panel_config, crop_dict
        )
        
        # Predict total yield
        total_yield = ml_service.predict_crop_yield(
            daily_growth, panel_config, crop_dict
        )
        
        # Calculate shadow patterns
        shadow_patterns = ml_service.calculate_shadow_patterns(
            weather_data, panel_config
        )
        
        # Calculate water usage
        water_usage = prediction_request.field_size * sum(
            max(0, crop_dict["water_requirement_mm_day"] - day.get("precipitation", 0))
            for day in weather_data
        ) / 1000  # Convert mm to m³
        
        # Calculate average growth factor
        avg_growth_factor = sum(daily_growth) / len(daily_growth) if daily_growth else 0
        
        # Return prediction results
        result = {
            "crop_type": prediction_request.crop_type,
            "total_yield_kg": total_yield,
            "yield_per_sqm": total_yield / prediction_request.field_size,
            "growth_factors": {
                "average": avg_growth_factor,
                "daily": daily_growth[:10],  # Return first 10 days only
                "total_days": len(daily_growth)
            },
            "shadow_impact": {
                "average_coverage_percent": shadow_patterns["average_shadow_coverage_percent"],
                "crop_yield_impact": shadow_patterns["crop_yield_impact"]
            },
            "water_usage_cubic_m": water_usage,
            "prediction_period": {
                "start_date": prediction_request.start_date,
                "end_date": prediction_request.end_date,
                "days": len(weather_data)
            }
        }
        
        return result
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error during crop yield prediction: {str(e)}",
        )

@router.get("/factors", response_model=List[schemas.CropGrowthFactors])
async def get_crop_growth_factors(
    crop_type: str = Query(..., description="Crop type name"),
    latitude: float = Query(..., ge=-90, le=90, description="Location latitude"),
    longitude: float = Query(..., ge=-180, le=180, description="Location longitude"),
    start_date: date = Query(..., description="Start date for prediction"),
    end_date: date = Query(..., description="End date for prediction"),
    panel_height: float = Query(2.5, ge=1.0, le=5.0, description="Panel height in meters"),
    panel_angle: float = Query(30.0, ge=0.0, le=90.0, description="Panel angle in degrees"),
    panel_spacing: float = Query(5.0, ge=1.0, le=10.0, description="Panel spacing in meters"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    Get detailed crop growth factors over time for visualization
    """
    # Initialize services
    ml_service = MLService()
    weather_service = WeatherService(db)
    
    # Validate crop exists
    crop_data = db.query(CropData).filter(CropData.name == crop_type).first()
    if not crop_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Crop type '{crop_type}' not found",
        )
    
    # Get weather data
    weather_data = weather_service.get_weather_data(
        location={"lat": latitude, "lng": longitude},
        start_date=start_date.isoformat(),
        end_date=end_date.isoformat()
    )
    
    if not weather_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to retrieve weather data",
        )
    
    # Prepare configuration
    panel_config = {
        "panel_height": panel_height,
        "panel_angle": panel_angle,
        "panel_spacing": panel_spacing,
    }
    
    # Convert crop data to dict
    crop_dict = {
        "optimal_temp_min": crop_data.optimal_temperature_min,
        "optimal_temp_max": crop_data.optimal_temperature_max,
        "water_requirement_mm_day": crop_data.water_requirement_mm_day,
        "shade_tolerance": crop_data.shade_tolerance,
        "growth_period_days": crop_data.growth_period_days
    }
    
    try:
        # Calculate growth factors
        weather_df = pd.DataFrame(weather_data)
        
        # If we have a simplified model, we can calculate individual factors
        temperature_stress = []
        water_stress = []
        light_stress = []
        
        for _, day in weather_df.iterrows():
            # Temperature stress
            temp_avg = (day.get("temperature_high", 25) + day.get("temperature_low", 15)) / 2
            temp_min = crop_dict["optimal_temp_min"]
            temp_max = crop_dict["optimal_temp_max"]
            
            if temp_avg < temp_min:
                temp_stress = 1 - (temp_min - temp_avg) / 10
            elif temp_avg > temp_max:
                temp_stress = 1 - (temp_avg - temp_max) / 10
            else:
                temp_stress = 1.0
            
            temp_stress = max(0.1, min(1.0, temp_stress))
            temperature_stress.append(temp_stress)
            
            # Water stress
            water_req = crop_dict["water_requirement_mm_day"]
            precip = day.get("precipitation", 0)
            water_stress_val = min(1.0, precip / water_req) if water_req > 0 else 1.0
            water_stress.append(max(0.1, water_stress_val))
            
            # Calculate shade impact
            shadow_length = panel_height * np.tan(np.radians(panel_angle))
            shadow_coverage = min(1.0, shadow_length / panel_spacing)
            shade_tolerance = crop_dict["shade_tolerance"]
            light_stress_val = 1.0 - (shadow_coverage * (1.0 - shade_tolerance))
            light_stress.append(light_stress_val)
        
        # Combined growth factors
        combined_factors = []
        for i in range(len(temperature_stress)):
            combined_factors.append({
                "date": weather_data[i]["date"] if i < len(weather_data) else None,
                "temperature_factor": temperature_stress[i],
                "water_factor": water_stress[i],
                "light_factor": light_stress[i],
                "combined_factor": temperature_stress[i] * water_stress[i] * light_stress[i]
            })
        
        return combined_factors
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error calculating growth factors: {str(e)}",
        )