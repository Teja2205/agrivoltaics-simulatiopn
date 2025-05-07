from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, Query, status
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
import json
from datetime import datetime
from sqlalchemy import func

from app.api.dependencies import get_current_user, get_db
from app.models import schemas
from app.models.database import User, Simulation
from app.services.simulation_service import SimulationService

router = APIRouter()

@router.get("/stats", response_model=schemas.SimulationStats)
async def get_simulation_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> schemas.SimulationStats:
    """
    Get simulation statistics for the current user
    """
    try:
        # Get total simulations
        total = db.query(Simulation).filter(
            Simulation.owner_id == current_user.id
        ).count()

        # Get active simulations (both pending and running)
        active = db.query(Simulation).filter(
            Simulation.owner_id == current_user.id,
            Simulation.status.in_(["pending", "running"])
        ).count()

        # Get completed simulations
        completed = db.query(Simulation).filter(
            Simulation.owner_id == current_user.id,
            Simulation.status == "completed"
        ).count()

        # Get latest simulation
        latest = db.query(Simulation).filter(
            Simulation.owner_id == current_user.id
        ).order_by(Simulation.created_at.desc()).first()

        last_simulation = None
        if latest:
            last_simulation = {
                "id": str(latest.id),
                "title": latest.title,
                "status": latest.status,
                "created_at": latest.created_at.isoformat(),
                "completed_at": latest.completed_at.isoformat() if latest.completed_at else None
            }

        return schemas.SimulationStats(
            total=total,
            active=active,
            completed=completed,
            lastSimulation=last_simulation
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch simulation stats: {str(e)}"
        )


@router.get("/", response_model=List[schemas.Simulation])
async def get_simulations(
    skip: int = 0,
    limit: int = 100,
    status: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get all simulations for the current user
    """
    query = db.query(Simulation).filter(Simulation.owner_id == current_user.id)
    
    if status:
        query = query.filter(Simulation.status == status)
    
    return query.offset(skip).limit(limit).all()


@router.get("/{simulation_id}", response_model=schemas.Simulation)
async def get_simulation(
    simulation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get a specific simulation by ID
    """
    simulation = db.query(Simulation).filter(
        Simulation.id == simulation_id,
        Simulation.owner_id == current_user.id
    ).first()
    
    if not simulation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Simulation not found"
        )
    
    return simulation


@router.put("/{simulation_id}", response_model=schemas.Simulation)
async def update_simulation(
    simulation_id: int,
    simulation_update: schemas.SimulationUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Update a simulation
    """
    db_simulation = db.query(Simulation).filter(
        Simulation.id == simulation_id,
        Simulation.owner_id == current_user.id
    ).first()
    
    if not db_simulation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Simulation not found"
        )
    
    # Only allow updates if simulation is not running
    if db_simulation.status == "running":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot update a running simulation"
        )
    
    update_data = simulation_update.dict(exclude_unset=True)
    
    for key, value in update_data.items():
        setattr(db_simulation, key, value)
    
    db.commit()
    db.refresh(db_simulation)
    return db_simulation


@router.delete("/{simulation_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_simulation(
    simulation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Delete a simulation
    """
    db_simulation = db.query(Simulation).filter(
        Simulation.id == simulation_id,
        Simulation.owner_id == current_user.id
    ).first()
    
    if not db_simulation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Simulation not found"
        )
    
    # Do not allow deletion of running simulations
    if db_simulation.status == "running":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete a running simulation"
        )
    
    db.delete(db_simulation)
    db.commit()
    
    return None


@router.post("/{simulation_id}/run", response_model=schemas.Simulation)
async def run_simulation(
    simulation_id: int,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Run or re-run a simulation
    """
    db_simulation = db.query(Simulation).filter(
        Simulation.id == simulation_id,
        Simulation.owner_id == current_user.id
    ).first()
    
    if not db_simulation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Simulation not found"
        )
    
    # Check if simulation is already running
    if db_simulation.status == "running":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Simulation is already running"
        )
    
    # Update status to pending
    db_simulation.status = "pending"
    db_simulation.results = None
    db_simulation.completed_at = None
    db.commit()
    db.refresh(db_simulation)
    
    # Start simulation in background
    simulation_service = SimulationService(db)
    background_tasks.add_task(
        simulation_service.run_simulation,
        simulation_id=db_simulation.id
    )
    
    return db_simulation


@router.get("/{simulation_id}/results", response_model=schemas.SimulationResult)
async def get_simulation_results(
    simulation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get the results of a simulation
    """
    db_simulation = db.query(Simulation).filter(
        Simulation.id == simulation_id,
        Simulation.owner_id == current_user.id
    ).first()
    
    if not db_simulation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Simulation not found"
        )
    
    if db_simulation.status != "completed":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Simulation results not available. Current status: {db_simulation.status}"
        )
    
    if not db_simulation.results:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No results found for this simulation"
        )
    
    return schemas.SimulationResult(
        simulation_id=db_simulation.id,
        **db_simulation.results
    )