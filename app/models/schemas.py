from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime


class UserBase(BaseModel):
    email: EmailStr
    full_name: Optional[str] = None
    is_active: Optional[bool] = True
    is_superuser: bool = False


class UserCreate(UserBase):
    password: str


class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    password: Optional[str] = None
    is_active: Optional[bool] = None
    is_superuser: Optional[bool] = None


class User(UserBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str
    user_id: str
    email: str
    full_name: Optional[str] = None
    is_superuser: bool = False


class TokenPayload(BaseModel):
    sub: str  # user id
    exp: int  # expiration timestamp
    type: str = "access"  # token type


class SimulationBase(BaseModel):
    title: str
    description: Optional[str] = None
    parameters: Dict[str, Any]


class SimulationCreate(SimulationBase):
    pass


class SimulationUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    parameters: Optional[Dict[str, Any]] = None
    status: Optional[str] = None


class Simulation(SimulationBase):
    id: int
    owner_id: int
    status: str
    results: Optional[Dict[str, Any]] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class ConfigurationBase(BaseModel):
    simulation_id: int
    name: str
    description: Optional[str] = None
    parameters: Dict[str, Any]
    is_optimized: bool = False


class ConfigurationCreate(ConfigurationBase):
    pass


class ConfigurationUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    parameters: Optional[Dict[str, Any]] = None
    is_optimized: Optional[bool] = None


class Configuration(ConfigurationBase):
    id: int
    owner_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class WeatherDataBase(BaseModel):
    date: datetime
    location_lat: float = Field(..., ge=-90, le=90)
    location_lng: float = Field(..., ge=-180, le=180)
    temperature_high: float
    temperature_low: float
    humidity: float = Field(..., ge=0, le=100)
    precipitation: float = Field(..., ge=0)
    cloud_cover: float = Field(..., ge=0, le=1)
    wind_speed: float = Field(..., ge=0)
    wind_direction: float = Field(..., ge=0, le=360)
    solar_radiation: float = Field(..., ge=0)


class WeatherDataCreate(WeatherDataBase):
    pass


class WeatherData(WeatherDataBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


# This is the simplified schema for weather data that uses string for date
class WeatherDataSimple(BaseModel):
    date: str
    temperature_high: float
    temperature_low: float
    humidity: float
    precipitation: float
    cloud_cover: float
    wind_speed: float
    wind_direction: float
    solar_radiation: float
    location_lat: float
    location_lng: float


class CropDataBase(BaseModel):
    name: str
    scientific_name: Optional[str] = None
    growth_period_days: int = Field(..., gt=0)
    optimal_temperature_min: float
    optimal_temperature_max: float
    water_requirement_mm_day: float = Field(..., ge=0)
    shade_tolerance: float = Field(..., ge=0, le=1)
    typical_yield_per_sqm: float = Field(..., ge=0)
    planting_depth_cm: float = Field(..., ge=0)
    row_spacing_cm: float = Field(..., ge=0)
    plant_spacing_cm: float = Field(..., ge=0)
    properties: Optional[Dict[str, Any]] = None


class CropDataCreate(CropDataBase):
    pass


class CropDataUpdate(BaseModel):
    scientific_name: Optional[str] = None
    growth_period_days: Optional[int] = Field(None, gt=0)
    optimal_temperature_min: Optional[float] = None
    optimal_temperature_max: Optional[float] = None
    water_requirement_mm_day: Optional[float] = Field(None, ge=0)
    shade_tolerance: Optional[float] = Field(None, ge=0, le=1)
    typical_yield_per_sqm: Optional[float] = Field(None, ge=0)
    planting_depth_cm: Optional[float] = Field(None, ge=0)
    row_spacing_cm: Optional[float] = Field(None, ge=0)
    plant_spacing_cm: Optional[float] = Field(None, ge=0)
    properties: Optional[Dict[str, Any]] = None


class CropData(CropDataBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class SimulationResult(BaseModel):
    simulation_id: int
    configuration_id: Optional[int] = None
    energy_production: Dict[str, Any]
    crop_yield: Dict[str, Any]
    shadow_patterns: Optional[Dict[str, Any]] = None
    water_usage: Dict[str, Any]
    financial_metrics: Dict[str, Any]
    environmental_metrics: Optional[Dict[str, Any]] = None


class OptimizationRequest(BaseModel):
    simulation_id: int
    constraints: Dict[str, Any]
    optimization_goals: Dict[str, float]  # Weights for each objective
    weather_data_id: Optional[int] = None
    custom_weather_data: Optional[List[Dict[str, Any]]] = None


# Schema for simulation statistics
class SimulationStats(BaseModel):
    total: int
    active: int
    completed: int
    lastSimulation: Optional[Dict[str, Any]] = None
# Add to app/models/schemas.py

class CropYieldPredictionRequest(BaseModel):
    crop_type: str
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    start_date: str
    end_date: str
    panel_height: float = Field(2.5, ge=1.0, le=5.0)
    panel_angle: float = Field(30.0, ge=0.0, le=90.0)
    panel_spacing: float = Field(5.0, ge=1.0, le=10.0)
    shadow_coverage_percent: float = Field(30.0, ge=0.0, le=100.0)
    irrigation_amount: float = Field(5.0, ge=0.0)
    field_size: float = Field(10000.0, gt=0.0)  # m²

class GrowthFactorData(BaseModel):
    average: float
    daily: List[float]
    total_days: int

class ShadowImpactData(BaseModel):
    average_coverage_percent: float
    crop_yield_impact: float

class PredictionPeriodData(BaseModel):
    start_date: str
    end_date: str
    days: int

class CropYieldPrediction(BaseModel):
    crop_type: str
    total_yield_kg: float
    yield_per_sqm: float
    growth_factors: GrowthFactorData
    shadow_impact: ShadowImpactData
    water_usage_cubic_m: float
    prediction_period: PredictionPeriodData

class CropGrowthFactors(BaseModel):
    date: Optional[str] = None
    temperature_factor: float
    water_factor: float
    light_factor: float
    combined_factor: float