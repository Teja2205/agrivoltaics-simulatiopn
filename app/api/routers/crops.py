from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from datetime import datetime

from app.api.dependencies import get_current_user, get_current_active_superuser, get_db
from app.models import schemas
from app.models.database import User, CropData

router = APIRouter()

@router.get("/", response_model=List[schemas.CropData])
async def list_crops(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    List all available crops
    """
    crops = db.query(CropData).offset(skip).limit(limit).all()
    return crops

@router.post("/", response_model=schemas.CropData)
async def create_crop(
    crop: schemas.CropDataCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_superuser),
) -> Any:
    """
    Create new crop data. Only for superusers.
    """
    # Check if crop already exists
    existing_crop = db.query(CropData).filter(CropData.name == crop.name).first()
    if existing_crop:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Crop with this name already exists",
        )
    
    db_crop = CropData(
        name=crop.name,
        scientific_name=crop.scientific_name,
        growth_period_days=crop.growth_period_days,
        optimal_temperature_min=crop.optimal_temperature_min,
        optimal_temperature_max=crop.optimal_temperature_max,
        water_requirement_mm_day=crop.water_requirement_mm_day,
        shade_tolerance=crop.shade_tolerance,
        typical_yield_per_sqm=crop.typical_yield_per_sqm,
        planting_depth_cm=crop.planting_depth_cm,
        row_spacing_cm=crop.row_spacing_cm,
        plant_spacing_cm=crop.plant_spacing_cm,
        properties=crop.properties,
    )
    
    db.add(db_crop)
    db.commit()
    db.refresh(db_crop)
    return db_crop

@router.get("/{crop_id}", response_model=schemas.CropData)
async def get_crop(
    crop_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    Get specific crop data by ID
    """
    crop = db.query(CropData).filter(CropData.id == crop_id).first()
    if not crop:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Crop not found",
        )
    return crop

@router.put("/{crop_id}", response_model=schemas.CropData)
async def update_crop(
    crop_id: int,
    crop_update: schemas.CropDataUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_superuser),
) -> Any:
    """
    Update crop data. Only for superusers.
    """
    crop = db.query(CropData).filter(CropData.id == crop_id).first()
    if not crop:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Crop not found",
        )
    
    # Update crop attributes
    for field, value in crop_update.dict(exclude_unset=True).items():
        setattr(crop, field, value)
    
    db.add(crop)
    db.commit()
    db.refresh(crop)
    return crop

@router.delete("/{crop_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_crop(
    crop_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_superuser)
):
    """
    Delete crop data. Only for superusers.
    """
    crop = db.query(CropData).filter(CropData.id == crop_id).first()
    if not crop:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Crop not found",
        )
    
    db.delete(crop)
    db.commit()

@router.get("/search/", response_model=List[schemas.CropData])
async def search_crops(
    name: Optional[str] = None,
    scientific_name: Optional[str] = None,
    min_shade_tolerance: Optional[float] = Query(None, ge=0, le=1),
    max_water_requirement: Optional[float] = Query(None, ge=0),
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    Search crops based on various criteria
    """
    query = db.query(CropData)
    
    if name:
        query = query.filter(CropData.name.ilike(f"%{name}%"))
    if scientific_name:
        query = query.filter(CropData.scientific_name.ilike(f"%{scientific_name}%"))
    if min_shade_tolerance is not None:
        query = query.filter(CropData.shade_tolerance >= min_shade_tolerance)
    if max_water_requirement is not None:
        query = query.filter(CropData.water_requirement_mm_day <= max_water_requirement)
    
    crops = query.offset(skip).limit(limit).all()
    return crops 