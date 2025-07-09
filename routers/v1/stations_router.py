from typing import Optional
from fastapi import APIRouter, HTTPException, Depends
from datetime import datetime
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from flasx.schemas import station_schema
from flasx.models import get_session, Station

router = APIRouter(prefix="/stations", tags=["stations"])


@router.get(
    "",
    summary="Get all stations",
    description="Retrieve a list of all stations with optional filtering.",
    response_model=list[station_schema.Station],
)
async def get_stations(
    skip: int = 0,
    limit: int = 100,
    city: Optional[str] = None,
    state: Optional[str] = None,
    is_active: Optional[bool] = None,
    session: AsyncSession = Depends(get_session),
) -> list[station_schema.Station]:
    """Get all stations with optional pagination and filtering."""
    query = select(Station)

    # Apply filters
    if city:
        query = query.where(Station.city.ilike(f"%{city}%"))
    if state:
        query = query.where(Station.state.ilike(f"%{state}%"))
    if is_active is not None:
        query = query.where(Station.is_active == is_active)

    # Apply pagination
    query = query.offset(skip).limit(limit)

    result = await session.exec(query)
    stations = result.all()

    return [station_schema.Station.model_validate(station) for station in stations]


@router.get(
    "/{station_id}",
    summary="Get a station by ID",
    description="Retrieve a specific station using its unique identifier.",
    response_model=station_schema.Station,
)
async def get_station(
    station_id: int, session: AsyncSession = Depends(get_session)
) -> station_schema.Station:
    """Get a single station by ID."""
    station = await session.get(Station, station_id)
    if not station:
        raise HTTPException(status_code=404, detail="Station not found")

    return station_schema.Station.model_validate(station)


@router.get(
    "/code/{station_code}",
    summary="Get a station by code",
    description="Retrieve a specific station using its code.",
    response_model=station_schema.Station,
)
async def get_station_by_code(
    station_code: str, session: AsyncSession = Depends(get_session)
) -> station_schema.Station:
    """Get a single station by code."""
    query = select(Station).where(Station.code == station_code)
    result = await session.exec(query)
    station = result.first()

    if not station:
        raise HTTPException(status_code=404, detail="Station not found")

    return station_schema.Station.model_validate(station)


@router.post(
    "",
    summary="Create a new station",
    description="Create a new station with the provided details.",
    response_model=station_schema.Station,
    status_code=201,
)
async def create_station(
    station: station_schema.StationCreate,
    session: AsyncSession = Depends(get_session),
) -> station_schema.Station:
    """Create a new station."""
    # Check if code already exists
    query = select(Station).where(Station.code == station.code)
    result = await session.exec(query)
    existing_station = result.first()

    if existing_station:
        raise HTTPException(status_code=400, detail="Station code already exists")

    # Create new station
    db_station = Station(**station.model_dump())
    session.add(db_station)
    await session.commit()
    await session.refresh(db_station)

    return station_schema.Station.model_validate(db_station)


@router.put(
    "/{station_id}",
    summary="Update an existing station",
    description="Update an existing station with the provided details.",
    response_model=station_schema.Station,
)
async def update_station(
    station_id: int,
    station_update: station_schema.StationUpdate,
    session: AsyncSession = Depends(get_session),
) -> station_schema.Station:
    """Update an existing station."""
    db_station = await session.get(Station, station_id)
    if not db_station:
        raise HTTPException(status_code=404, detail="Station not found")

    # Check if code is being updated and already exists
    if station_update.code:
        query = select(Station).where(
            Station.code == station_update.code, Station.id != station_id
        )
        result = await session.exec(query)
        existing_station = result.first()

        if existing_station:
            raise HTTPException(status_code=400, detail="Station code already exists")

    # Update only provided fields
    update_data = station_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_station, field, value)

    # Update timestamp
    db_station.updated_at = datetime.now()

    await session.commit()
    await session.refresh(db_station)

    return station_schema.Station.model_validate(db_station)


@router.delete(
    "/{station_id}",
    summary="Delete a station",
    description="Delete a station by ID.",
    status_code=204,
)
async def delete_station(station_id: int, session: AsyncSession = Depends(get_session)):
    """Delete a station."""
    db_station = await session.get(Station, station_id)
    if not db_station:
        raise HTTPException(status_code=404, detail="Station not found")

    await session.delete(db_station)
    await session.commit()
    return None