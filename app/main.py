from fastapi import FastAPI, Depends, HTTPException, BackgroundTasks, Query, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
import os
import json
import numpy as np
import pandas as pd
from datetime import datetime, timedelta

from app.database import engine, SessionLocal
from app.models import database as db_models
from app.models import schemas
from app.core import security
from app.core.config import settings
from app.api.dependencies import get_current_user, get_db
from app.services.simulation_service import SimulationService
from app.services.ml_service import MLService
from app.services.weather_service import WeatherService
from app.api.routers import simulation, optimization, auth, users, weather, crops

# Create database tables
db_models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Agrivoltaics Simulation API",
    description="API for simulating and optimizing agrivoltaics systems",
    version="1.0.0",
)
# In main.py
app.include_router(simulation.router, prefix="/api/simulation", tags=["Simulation"])

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],  # Frontend URLs
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["*"],
    max_age=3600,  # Cache preflight requests for 1 hour
)

# Mount static files
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(users.router, prefix="/api/users", tags=["Users"])
app.include_router(simulation.router, prefix="/api/simulation", tags=["Simulation"])
app.include_router(optimization.router, prefix="/api/optimization", tags=["Optimization"])
app.include_router(weather.router, prefix="/api/weather", tags=["Weather"])
app.include_router(crops.router, prefix="/api/crops", tags=["Crops"])

@app.get("/", response_model=Dict[str, str])
async def root():
    """
    Root endpoint with API information
    """
    return {
        "name": "Agrivoltaics Simulation API",
        "version": "1.0.0",
        "status": "active",
    }

@app.get("/api/health", response_model=Dict[str, Any])
async def health_check():
    """
    Health check endpoint
    """
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0",
        "environment": settings.ENVIRONMENT,
    }