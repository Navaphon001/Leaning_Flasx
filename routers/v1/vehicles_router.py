from typing import Optional
from fastapi import APIRouter, HTTPException, Depends
from datetime import datetime
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from schemas import vehicle_schema
from models import get_session, Vehicle

router = APIRouter(prefix="/vehicles", tags=["vehicles"])


@router.get(
    "",
    summary="Get all vehicles",
    description="Retrieve a list of all vehicles with optional filtering.",
    response_model=list[vehicle_schema.Vehicle],
)
async def get_vehicles(
    skip: int = 0,
    limit: int = 100,
    type: Optional[str] = None,
    is_active: Optional[bool] = None,
    session: AsyncSession = Depends(get_session),
) -> list[vehicle_schema.Vehicle]:
    """Get all vehicles with optional pagination and filtering."""
    query = select(Vehicle)

    # Apply filters
    if type:
        query = query.where(Vehicle.type.ilike(f"%{type}%"))
    if is_active is not None:
        query = query.where(Vehicle.is_active == is_active)

    # Apply pagination
    query = query.offset(skip).limit(limit)

    result = await session.exec(query)
    vehicles = result.all()

    return [vehicle_schema.Vehicle.model_validate(vehicle) for vehicle in vehicles]


@router.get(
    "/{vehicle_id}",
    summary="Get a vehicle by ID",
    description="Retrieve a specific vehicle using its unique identifier.",
    response_model=vehicle_schema.Vehicle,
)
async def get_vehicle(
    vehicle_id: int, session: AsyncSession = Depends(get_session)
) -> vehicle_schema.Vehicle:
    """Get a single vehicle by ID."""
    vehicle = await session.get(Vehicle, vehicle_id)
    if not vehicle:
        raise HTTPException(status_code=404, detail="Vehicle not found")

    return vehicle_schema.Vehicle.model_validate(vehicle)


@router.get(
    "/license/{license_plate}",
    summary="Get a vehicle by license plate",
    description="Retrieve a specific vehicle using its license plate.",
    response_model=vehicle_schema.Vehicle,
)
async def get_vehicle_by_license(
    license_plate: str, session: AsyncSession = Depends(get_session)
) -> vehicle_schema.Vehicle:
    """Get a single vehicle by license plate."""
    query = select(Vehicle).where(Vehicle.license_plate == license_plate)
    result = await session.exec(query)
    vehicle = result.first()

    if not vehicle:
        raise HTTPException(status_code=404, detail="Vehicle not found")

    return vehicle_schema.Vehicle.model_validate(vehicle)


@router.post(
    "",
    summary="Create a new vehicle",
    description="Create a new vehicle with the provided details.",
    response_model=vehicle_schema.Vehicle,
    status_code=201,
)
async def create_vehicle(
    vehicle: vehicle_schema.VehicleCreate,
    session: AsyncSession = Depends(get_session),
) -> vehicle_schema.Vehicle:
    """Create a new vehicle."""
    # Check if license plate already exists
    query = select(Vehicle).where(Vehicle.license_plate == vehicle.license_plate)
    result = await session.exec(query)
    existing_vehicle = result.first()

    if existing_vehicle:
        raise HTTPException(status_code=400, detail="License plate already exists")

    # Create new vehicle
    db_vehicle = Vehicle(**vehicle.model_dump())
    session.add(db_vehicle)
    await session.commit()
    await session.refresh(db_vehicle)

    return vehicle_schema.Vehicle.model_validate(db_vehicle)


@router.put(
    "/{vehicle_id}",
    summary="Update an existing vehicle",
    description="Update an existing vehicle with the provided details.",
    response_model=vehicle_schema.Vehicle,
)
async def update_vehicle(
    vehicle_id: int,
    vehicle_update: vehicle_schema.VehicleUpdate,
    session: AsyncSession = Depends(get_session),
) -> vehicle_schema.Vehicle:
    """Update an existing vehicle."""
    db_vehicle = await session.get(Vehicle, vehicle_id)
    if not db_vehicle:
        raise HTTPException(status_code=404, detail="Vehicle not found")

    # Check if license plate is being updated and already exists
    if vehicle_update.license_plate:
        query = select(Vehicle).where(
            Vehicle.license_plate == vehicle_update.license_plate,
            Vehicle.id != vehicle_id,
        )
        result = await session.exec(query)
        existing_vehicle = result.first()

        if existing_vehicle:
            raise HTTPException(status_code=400, detail="License plate already exists")

    # Update only provided fields
    update_data = vehicle_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_vehicle, field, value)

    # Update timestamp
    db_vehicle.updated_at = datetime.now()

    await session.commit()
    await session.refresh(db_vehicle)

    return vehicle_schema.Vehicle.model_validate(db_vehicle)


@router.delete(
    "/{vehicle_id}",
    summary="Delete a vehicle",
    description="Delete a vehicle by ID.",
    status_code=204,
)
async def delete_vehicle(vehicle_id: int, session: AsyncSession = Depends(get_session)):
    """Delete a vehicle."""
    db_vehicle = await session.get(Vehicle, vehicle_id)
    if not db_vehicle:
        raise HTTPException(status_code=404, detail="Vehicle not found")

    await session.delete(db_vehicle)
    await session.commit()
    return None