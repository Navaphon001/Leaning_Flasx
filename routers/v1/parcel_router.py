from typing import Optional
from fastapi import APIRouter, HTTPException, Depends
from datetime import datetime
import random
import string
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from flasx.schemas import parcel_schema
from flasx.models import get_session, Parcel, Station

router = APIRouter(prefix="/parcels", tags=["parcels"])


def generate_tracking_number() -> str:
    """Generate a unique tracking number."""
    prefix = "PKG"
    timestamp = datetime.now().strftime("%Y%m%d")
    random_suffix = "".join(random.choices(string.ascii_uppercase + string.digits, k=6))
    return f"{prefix}{timestamp}{random_suffix}"


@router.get(
    "",
    summary="Get all parcels",
    description="Retrieve a list of all parcels with optional filtering.",
    response_model=list[parcel_schema.Parcel],
)
async def get_parcels(
    skip: int = 0,
    limit: int = 100,
    status: Optional[parcel_schema.ParcelStatus] = None,
    sender_id: Optional[int] = None,
    receiver_id: Optional[int] = None,
    session: AsyncSession = Depends(get_session),
) -> list[parcel_schema.Parcel]:
    """Get all parcels with optional pagination and filtering."""
    query = select(Parcel)

    # Apply filters
    if status:
        query = query.where(Parcel.status == status)
    if sender_id:
        query = query.where(Parcel.sender_id == sender_id)
    if receiver_id:
        query = query.where(Parcel.receiver_id == receiver_id)

    # Apply pagination
    query = query.offset(skip).limit(limit)

    result = await session.exec(query)
    parcels = result.all()

    return [parcel_schema.Parcel.model_validate(parcel) for parcel in parcels]


@router.get(
    "/{parcel_id}",
    summary="Get a parcel by ID",
    description="Retrieve a specific parcel using its unique identifier.",
    response_model=parcel_schema.Parcel,
)
async def get_parcel(
    parcel_id: int, session: AsyncSession = Depends(get_session)
) -> parcel_schema.Parcel:
    """Get a single parcel by ID."""
    parcel = await session.get(Parcel, parcel_id)
    if not parcel:
        raise HTTPException(status_code=404, detail="Parcel not found")

    return parcel_schema.Parcel.model_validate(parcel)


@router.get(
    "/track/{tracking_number}",
    summary="Track a parcel",
    description="Track a parcel using its tracking number (public endpoint).",
    response_model=parcel_schema.ParcelTracking,
)
async def track_parcel(
    tracking_number: str, session: AsyncSession = Depends(get_session)
) -> parcel_schema.ParcelTracking:
    """Track a parcel by tracking number."""
    query = (
        select(
            Parcel,
            Station.name.label("origin_station_name"),
            Station.name.label("destination_station_name"),
        )
        .outerjoin(Station, Parcel.origin_station_id == Station.id)
        .where(Parcel.tracking_number == tracking_number)
    )
    result = await session.exec(query)
    parcel_data = result.first()

    if not parcel_data:
        raise HTTPException(status_code=404, detail="Parcel not found")

    parcel = parcel_data[0]

    # Get station names separately for better handling
    origin_station_name = None
    destination_station_name = None

    if parcel.origin_station_id:
        origin_station = await session.get(Station, parcel.origin_station_id)
        origin_station_name = origin_station.name if origin_station else None

    if parcel.destination_station_id:
        destination_station = await session.get(Station, parcel.destination_station_id)
        destination_station_name = (
            destination_station.name if destination_station else None
        )

    return parcel_schema.ParcelTracking(
        tracking_number=parcel.tracking_number,
        status=parcel.status,
        created_at=parcel.created_at,
        updated_at=parcel.updated_at,
        origin_station_name=origin_station_name,
        destination_station_name=destination_station_name,
    )


@router.post(
    "",
    summary="Create a new parcel",
    description="Create a new parcel with the provided details.",
    response_model=parcel_schema.Parcel,
    status_code=201,
)
async def create_parcel(
    parcel: parcel_schema.ParcelCreate,
    session: AsyncSession = Depends(get_session),
) -> parcel_schema.Parcel:
    """Create a new parcel."""
    # Generate unique tracking number
    tracking_number = generate_tracking_number()

    # Ensure tracking number is unique
    while True:
        query = select(Parcel).where(Parcel.tracking_number == tracking_number)
        result = await session.exec(query)
        existing_parcel = result.first()

        if not existing_parcel:
            break
        tracking_number = generate_tracking_number()

    # Create new parcel
    parcel_data = parcel.model_dump()
    parcel_data["tracking_number"] = tracking_number

    db_parcel = Parcel(**parcel_data)
    session.add(db_parcel)
    await session.commit()
    await session.refresh(db_parcel)

    return parcel_schema.Parcel.model_validate(db_parcel)


@router.put(
    "/{parcel_id}",
    summary="Update an existing parcel",
    description="Update an existing parcel with the provided details.",
    response_model=parcel_schema.Parcel,
)
async def update_parcel(
    parcel_id: int,
    parcel_update: parcel_schema.ParcelUpdate,
    session: AsyncSession = Depends(get_session),
) -> parcel_schema.Parcel:
    """Update an existing parcel."""
    db_parcel = await session.get(Parcel, parcel_id)
    if not db_parcel:
        raise HTTPException(status_code=404, detail="Parcel not found")

    # Update only provided fields
    update_data = parcel_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_parcel, field, value)

    # Update timestamp
    db_parcel.updated_at = datetime.now()

    await session.commit()
    await session.refresh(db_parcel)

    return parcel_schema.Parcel.model_validate(db_parcel)


@router.patch(
    "/{parcel_id}/status",
    summary="Update parcel status",
    description="Update the status of a parcel.",
    response_model=parcel_schema.Parcel,
)
async def update_parcel_status(
    parcel_id: int,
    status: parcel_schema.ParcelStatus,
    session: AsyncSession = Depends(get_session),
) -> parcel_schema.Parcel:
    """Update parcel status."""
    db_parcel = await session.get(Parcel, parcel_id)
    if not db_parcel:
        raise HTTPException(status_code=404, detail="Parcel not found")

    db_parcel.status = status
    db_parcel.updated_at = datetime.now()

    await session.commit()
    await session.refresh(db_parcel)

    return parcel_schema.Parcel.model_validate(db_parcel)


@router.patch(
    "/{parcel_id}/assign-vehicle",
    summary="Assign vehicle to parcel",
    description="Assign a vehicle to a parcel for transportation.",
    response_model=parcel_schema.Parcel,
)
async def assign_vehicle_to_parcel(
    parcel_id: int,
    vehicle_id: int,
    session: AsyncSession = Depends(get_session),
) -> parcel_schema.Parcel:
    """Assign a vehicle to a parcel."""
    db_parcel = await session.get(Parcel, parcel_id)
    if not db_parcel:
        raise HTTPException(status_code=404, detail="Parcel not found")

    db_parcel.vehicle_id = vehicle_id
    db_parcel.updated_at = datetime.now()

    await session.commit()
    await session.refresh(db_parcel)

    return parcel_schema.Parcel.model_validate(db_parcel)


@router.patch(
    "/{parcel_id}/assign-delivery-staff",
    summary="Assign delivery staff to parcel",
    description="Assign delivery staff to a parcel for final delivery.",
    response_model=parcel_schema.Parcel,
)
async def assign_delivery_staff_to_parcel(
    parcel_id: int,
    delivery_staff_id: int,
    session: AsyncSession = Depends(get_session),
) -> parcel_schema.Parcel:
    """Assign delivery staff to a parcel."""
    db_parcel = await session.get(Parcel, parcel_id)
    if not db_parcel:
        raise HTTPException(status_code=404, detail="Parcel not found")

    db_parcel.delivery_staff_id = delivery_staff_id
    db_parcel.updated_at = datetime.now()

    await session.commit()
    await session.refresh(db_parcel)

    return parcel_schema.Parcel.model_validate(db_parcel)


@router.delete(
    "/{parcel_id}",
    summary="Delete a parcel",
    description="Delete a parcel by ID.",
    status_code=204,
)
async def delete_parcel(parcel_id: int, session: AsyncSession = Depends(get_session)):
    """Delete a parcel."""
    db_parcel = await session.get(Parcel, parcel_id)
    if not db_parcel:
        raise HTTPException(status_code=404, detail="Parcel not found")

    await session.delete(db_parcel)
    await session.commit()
    return None