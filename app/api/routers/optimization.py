from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, status
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from datetime import datetime

from app.api.dependencies import get_current_user, get_db
from app.models import schemas
from app.models.database import User, Simulation, Configuration
from app.services.simulation_service import SimulationService

router = APIRouter()

@router.post("/optimize/{simulation_id}", response_model=schemas.Configuration)
async def optimize_simulation(
    simulation_id: int,
    optimization_request: schemas.OptimizationRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    Optimize a simulation configuration based on given constraints and goals
    """
    # Check if simulation exists and belongs to user
    simulation = db.query(Simulation).filter(
        Simulation.id == simulation_id,
        Simulation.owner_id == current_user.id
    ).first()
    
    if not simulation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Simulation not found or access denied",
        )
    
    # Create new configuration for optimization
    config = Configuration(
        simulation_id=simulation_id,
        owner_id=current_user.id,
        name=f"Optimized Configuration {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        description="Automatically optimized configuration",
        parameters=simulation.parameters,
        is_optimized=True
    )
    
    db.add(config)
    db.commit()
    db.refresh(config)
    
    # Start optimization in background
    simulation_service = SimulationService(db)
    background_tasks.add_task(
        simulation_service.optimize_configuration,
        config_id=config.id,
        constraints=optimization_request.constraints,
        optimization_goals=optimization_request.optimization_goals,
        weather_data_id=optimization_request.weather_data_id,
        custom_weather_data=optimization_request.custom_weather_data
    )
    
    return config

@router.get("/configurations/{config_id}", response_model=schemas.Configuration)
async def get_optimization_result(
    config_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    Get the results of an optimization
    """
    config = db.query(Configuration).filter(
        Configuration.id == config_id,
        Configuration.owner_id == current_user.id
    ).first()
    
    if not config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Configuration not found or access denied",
        )
    
    return config

@router.get("/configurations", response_model=List[schemas.Configuration])
async def list_optimized_configurations(
    simulation_id: Optional[int] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    List all optimized configurations for a user
    """
    query = db.query(Configuration).filter(
        Configuration.owner_id == current_user.id,
        Configuration.is_optimized == True
    )
    
    if simulation_id:
        query = query.filter(Configuration.simulation_id == simulation_id)
    
    configurations = query.offset(skip).limit(limit).all()
    return configurations

@router.delete("/configurations/{config_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_optimization_result(
    config_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Delete an optimization result
    """
    config = db.query(Configuration).filter(
        Configuration.id == config_id,
        Configuration.owner_id == current_user.id
    ).first()
    
    if not config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Configuration not found or access denied",
        )
    
    db.delete(config)
    db.commit() 