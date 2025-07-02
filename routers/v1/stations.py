from typing import Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from datetime import datetime

router = APIRouter(prefix="/stations", tags=["stations"])


# Pydantic Models
class StationBase(BaseModel):
    name: str
    location: Optional[str] = None
    is_active: bool = True


class StationCreate(StationBase):
    pass


class StationUpdate(BaseModel):
    name: Optional[str] = None
    location: Optional[str] = None
    is_active: Optional[bool] = None


class Station(StationBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# In-memory storage for demo purposes
stations_db: dict[int, dict] = {}
next_id = 1


@router.get(
    "",
    summary="Get all stations",
    description="Retrieve a list of all stations with optional filtering.",
    response_model=list[Station]
)
async def get_stations(
    skip: int = 0,
    limit: int = 100,
    is_active: Optional[bool] = None
) -> list[Station]:
    """Get all stations with optional pagination and filtering."""
    stations = list(stations_db.values())
    
    # Filter by is_active if provided
    if is_active is not None:
        stations = [s for s in stations if s["is_active"] == is_active]
    
    # Apply pagination
    stations = stations[skip:skip + limit]
    
    return [Station(**station) for station in stations]


@router.get(
    "/{station_id}",
    summary="Get a station by ID",
    description="Retrieve a specific station using its unique identifier.",
    response_model=Station
)
async def get_station(station_id: int) -> Station:
    """Get a single station by ID."""
    if station_id not in stations_db:
        raise HTTPException(status_code=404, detail="Station not found")
    
    return Station(**stations_db[station_id])


@router.post(
    "",
    summary="Create a new station",
    description="Create a new station with the provided details.",
    response_model=Station,
    status_code=201
)
async def create_station(station: StationCreate) -> Station:
    """Create a new station."""
    global next_id
    
    # Check if name already exists
    for existing_station in stations_db.values():
        if existing_station["name"] == station.name:
            raise HTTPException(status_code=400, detail="Station name already exists")
    
    now = datetime.now()
    station_data = {
        "id": next_id,
        "created_at": now,
        "updated_at": now,
        **station.model_dump()
    }
    
    stations_db[next_id] = station_data
    result = Station(**station_data)
    next_id += 1
    
    return result


@router.put(
    "/{station_id}",
    summary="Update an existing station",
    description="Update an existing station with the provided details.",
    response_model=Station
)
async def update_station(station_id: int, station_update: StationUpdate) -> Station:
    """Update an existing station."""
    if station_id not in stations_db:
        raise HTTPException(status_code=404, detail="Station not found")
    
    existing_station = stations_db[station_id]
    
    # Check if name is being updated and already exists
    if station_update.name:
        for sid, existing in stations_db.items():
            if sid != station_id and existing["name"] == station_update.name:
                raise HTTPException(status_code=400, detail="Station name already exists")
    
    # Update only provided fields
    update_data = station_update.model_dump(exclude_unset=True)
    if update_data:
        existing_station.update(update_data)
        existing_station["updated_at"] = datetime.now()
    
    return Station(**existing_station)


@router.patch(
    "/{station_id}",
    summary="Partially update a station",
    description="Partially update a station with the provided fields.",
    response_model=Station
)
async def patch_station(station_id: int, station_update: StationUpdate) -> Station:
    """Partially update a station (same as PUT in this implementation)."""
    return await update_station(station_id, station_update)


@router.delete(
    "/{station_id}",
    summary="Delete a station",
    description="Delete a station by ID.",
    status_code=204
)
async def delete_station(station_id: int):
    """Delete a station."""
    if station_id not in stations_db:
        raise HTTPException(status_code=404, detail="Station not found")
    
    del stations_db[station_id]
    return None


@router.post(
    "/{station_id}/activate",
    summary="Activate a station",
    description="Activate a station by setting is_active to True.",
    response_model=Station
)
async def activate_station(station_id: int) -> Station:
    """Activate a station."""
    if station_id not in stations_db:
        raise HTTPException(status_code=404, detail="Station not found")
    
    stations_db[station_id]["is_active"] = True
    stations_db[station_id]["updated_at"] = datetime.now()
    
    return Station(**stations_db[station_id])


@router.post(
    "/{station_id}/deactivate",
    summary="Deactivate a station",
    description="Deactivate a station by setting is_active to False.",
    response_model=Station
)
async def deactivate_station(station_id: int) -> Station:
    """Deactivate a station."""
    if station_id not in stations_db:
        raise HTTPException(status_code=404, detail="Station not found")
    
    stations_db[station_id]["is_active"] = False
    stations_db[station_id]["updated_at"] = datetime.now()
    
    return Station(**stations_db[station_id])