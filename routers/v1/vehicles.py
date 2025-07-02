from typing import Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from datetime import datetime

router = APIRouter(prefix="/vehicles", tags=["vehicles"])


# Pydantic Models
class VehicleBase(BaseModel):
    license_plate: str
    type: Optional[str] = None
    brand: Optional[str] = None
    color: Optional[str] = None
    is_active: bool = True


class VehicleCreate(VehicleBase):
    pass


class VehicleUpdate(BaseModel):
    license_plate: Optional[str] = None
    type: Optional[str] = None
    brand: Optional[str] = None
    color: Optional[str] = None
    is_active: Optional[bool] = None


class Vehicle(VehicleBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# In-memory storage for demo purposes
vehicles_db: dict[int, dict] = {}
next_id = 1


@router.get(
    "",
    summary="Get all vehicles",
    description="Retrieve a list of all vehicles with optional filtering.",
    response_model=list[Vehicle]
)
async def get_vehicles(
    skip: int = 0,
    limit: int = 100,
    is_active: Optional[bool] = None
) -> list[Vehicle]:
    """Get all vehicles with optional pagination and filtering."""
    vehicles = list(vehicles_db.values())
    
    # Filter by is_active if provided
    if is_active is not None:
        vehicles = [v for v in vehicles if v["is_active"] == is_active]
    
    # Apply pagination
    vehicles = vehicles[skip:skip + limit]
    
    return [Vehicle(**vehicle) for vehicle in vehicles]


@router.get(
    "/{vehicle_id}",
    summary="Get a vehicle by ID",
    description="Retrieve a specific vehicle using its unique identifier.",
    response_model=Vehicle
)
async def get_vehicle(vehicle_id: int) -> Vehicle:
    """Get a single vehicle by ID."""
    if vehicle_id not in vehicles_db:
        raise HTTPException(status_code=404, detail="Vehicle not found")
    
    return Vehicle(**vehicles_db[vehicle_id])


@router.post(
    "",
    summary="Create a new vehicle",
    description="Create a new vehicle with the provided details.",
    response_model=Vehicle,
    status_code=201
)
async def create_vehicle(vehicle: VehicleCreate) -> Vehicle:
    """Create a new vehicle."""
    global next_id
    
    # Check if license plate already exists
    for existing_vehicle in vehicles_db.values():
        if existing_vehicle["license_plate"] == vehicle.license_plate:
            raise HTTPException(status_code=400, detail="License plate already exists")
    
    now = datetime.now()
    vehicle_data = {
        "id": next_id,
        "created_at": now,
        "updated_at": now,
        **vehicle.model_dump()
    }
    
    vehicles_db[next_id] = vehicle_data
    result = Vehicle(**vehicle_data)
    next_id += 1
    
    return result


@router.put(
    "/{vehicle_id}",
    summary="Update an existing vehicle",
    description="Update an existing vehicle with the provided details.",
    response_model=Vehicle
)
async def update_vehicle(vehicle_id: int, vehicle_update: VehicleUpdate) -> Vehicle:
    """Update an existing vehicle."""
    if vehicle_id not in vehicles_db:
        raise HTTPException(status_code=404, detail="Vehicle not found")
    
    existing_vehicle = vehicles_db[vehicle_id]
    
    # Check if license plate is being updated and already exists
    if vehicle_update.license_plate:
        for vid, existing in vehicles_db.items():
            if vid != vehicle_id and existing["license_plate"] == vehicle_update.license_plate:
                raise HTTPException(status_code=400, detail="License plate already exists")
    
    # Update only provided fields
    update_data = vehicle_update.model_dump(exclude_unset=True)
    if update_data:
        existing_vehicle.update(update_data)
        existing_vehicle["updated_at"] = datetime.now()
    
    return Vehicle(**existing_vehicle)


@router.patch(
    "/{vehicle_id}",
    summary="Partially update a vehicle",
    description="Partially update a vehicle with the provided fields.",
    response_model=Vehicle
)
async def patch_vehicle(vehicle_id: int, vehicle_update: VehicleUpdate) -> Vehicle:
    """Partially update a vehicle (same as PUT in this implementation)."""
    return await update_vehicle(vehicle_id, vehicle_update)


@router.delete(
    "/{vehicle_id}",
    summary="Delete a vehicle",
    description="Delete a vehicle by ID.",
    status_code=204
)
async def delete_vehicle(vehicle_id: int):
    """Delete a vehicle."""
    if vehicle_id not in vehicles_db:
        raise HTTPException(status_code=404, detail="Vehicle not found")
    
    del vehicles_db[vehicle_id]
    return None


@router.post(
    "/{vehicle_id}/activate",
    summary="Activate a vehicle",
    description="Activate a vehicle by setting is_active to True.",
    response_model=Vehicle
)
async def activate_vehicle(vehicle_id: int) -> Vehicle:
    """Activate a vehicle."""
    if vehicle_id not in vehicles_db:
        raise HTTPException(status_code=404, detail="Vehicle not found")
    
    vehicles_db[vehicle_id]["is_active"] = True
    vehicles_db[vehicle_id]["updated_at"] = datetime.now()
    
    return Vehicle(**vehicles_db[vehicle_id])


@router.post(
    "/{vehicle_id}/deactivate",
    summary="Deactivate a vehicle",
    description="Deactivate a vehicle by setting is_active to False.",
    response_model=Vehicle
)
async def deactivate_vehicle(vehicle_id: int) -> Vehicle:
    """Deactivate a vehicle."""
    if vehicle_id not in vehicles_db:
        raise HTTPException(status_code=404, detail="Vehicle not found")
    
    vehicles_db[vehicle_id]["is_active"] = False
    vehicles_db[vehicle_id]["updated_at"] = datetime.now()
    
    return Vehicle(**vehicles_db[vehicle_id])