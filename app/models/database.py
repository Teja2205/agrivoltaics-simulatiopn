from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Float, DateTime, JSON, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    full_name = Column(String)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    simulations = relationship("Simulation", back_populates="owner")
    configurations = relationship("Configuration", back_populates="owner")


class Simulation(Base):
    __tablename__ = "simulations"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    description = Column(Text, nullable=True)
    owner_id = Column(Integer, ForeignKey("users.id"))
    status = Column(String)  # pending, running, completed, failed
    parameters = Column(JSON)
    results = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)

    owner = relationship("User", back_populates="simulations")
    configurations = relationship("Configuration", back_populates="simulation")


class Configuration(Base):
    __tablename__ = "configurations"

    id = Column(Integer, primary_key=True, index=True)
    simulation_id = Column(Integer, ForeignKey("simulations.id"))
    owner_id = Column(Integer, ForeignKey("users.id"))
    name = Column(String)
    description = Column(Text, nullable=True)
    parameters = Column(JSON)
    is_optimized = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    simulation = relationship("Simulation", back_populates="configurations")
    owner = relationship("User", back_populates="configurations")


class WeatherData(Base):
    __tablename__ = "weather_data"

    id = Column(Integer, primary_key=True, index=True)
    date = Column(DateTime(timezone=True), index=True)
    location_lat = Column(Float)
    location_lng = Column(Float)
    temperature_high = Column(Float)
    temperature_low = Column(Float)
    humidity = Column(Float)
    precipitation = Column(Float)
    cloud_cover = Column(Float)
    wind_speed = Column(Float)
    wind_direction = Column(Float)
    solar_radiation = Column(Float)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class CropData(Base):
    __tablename__ = "crop_data"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    scientific_name = Column(String, nullable=True)
    growth_period_days = Column(Integer)
    optimal_temperature_min = Column(Float)
    optimal_temperature_max = Column(Float)
    water_requirement_mm_day = Column(Float)
    shade_tolerance = Column(Float)  # 0-1 scale
    typical_yield_per_sqm = Column(Float)
    planting_depth_cm = Column(Float)
    row_spacing_cm = Column(Float)
    plant_spacing_cm = Column(Float)
    properties = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
