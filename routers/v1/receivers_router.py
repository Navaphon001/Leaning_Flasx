from typing import Optional
from fastapi import APIRouter, HTTPException, Depends
from datetime import datetime
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from schemas import receiver_schema
from models import get_session, Receiver

router = APIRouter(prefix="/receivers", tags=["receivers"])



@router.get(
    "",
    summary="Get all receivers",
    description="Retrieve a list of all receivers with optional filtering.",
    response_model=list[receiver_schema.Receiver],
)
async def get_receivers(
    skip: int = 0,
    limit: int = 100,
    is_active: Optional[bool] = None,
    session: AsyncSession = Depends(get_session),
) -> list[receiver_schema.Receiver]:
    """Get all receivers with optional pagination and filtering."""
    query = select(Receiver)


    # Filter by is_active if provided
    if is_active is not None:
        query = query.where(Receiver.is_active == is_active)

    # Apply pagination
    query = query.offset(skip).limit(limit)

    result = await session.exec(query)
    receivers = result.all()    

    return [receiver_schema.Receiver.model_validate(receiver) for receiver in receivers]


@router.get(
    "/{receiver_id}",
    summary="Get a receiver by ID",
    description="Retrieve a specific receiver using its unique identifier.",
    response_model=receiver_schema.Receiver,
)
async def get_receiver(
    receiver_id: int, session: AsyncSession = Depends(get_session)
) -> receiver_schema.Receiver:
    """Get a single receiver by ID."""
    receiver = await session.get(Receiver, receiver_id)
    if not receiver:
        raise HTTPException(status_code=404, detail="Receiver not found")
    return receiver_schema.Receiver.model_validate(receiver)


@router.post(
    "",
    summary="Create a new receiver",
    description="Create a new receiver with the provided details.",
    response_model=receiver_schema.Receiver,
    status_code=201,
)
async def create_receiver(
    receiver: receiver_schema.ReceiverCreate,
    session: AsyncSession = Depends(get_session),
) -> receiver_schema.Receiver:
    """Create a new receiver."""

    # Check if email already exists
    query = select(Receiver).where(Receiver.email == receiver.email)
    result = await session.exec(query)
    existing_receiver = result.first()

    if existing_receiver:
        raise HTTPException(status_code=400, detail="Email already registered")

    # Create new receiver
    db_receiver = Receiver(**receiver.model_dump())
    session.add(db_receiver)
    await session.commit()
    await session.refresh(db_receiver)

    return receiver_schema.Receiver.model_validate(db_receiver)


@router.put(
    "/{receiver_id}",
    summary="Update an existing receiver",
    description="Update an existing receiver with the provided details.",
    response_model=receiver_schema.Receiver,
)
async def update_receiver(
    receiver_id: int,
    receiver_update: receiver_schema.ReceiverUpdate,
    session: AsyncSession = Depends(get_session),
) -> receiver_schema.Receiver:
    """Update an existing receiver."""
    db_receiver = await session.get(Receiver, receiver_id)
    if not db_receiver:
        raise HTTPException(status_code=404, detail="Receiver not found")

    # Check if email is being updated and already exists
    if receiver_update.email:
        query = select(Receiver).where(
            Receiver.email == receiver_update.email, Receiver.id != receiver_id
        )
        result = await session.exec(query)
        existing_receiver = result.first()

        if existing_receiver:
            raise HTTPException(status_code=400, detail="Email already registered")

    # Update only provided fields
    update_data = receiver_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_receiver, field, value)  # Update timestamp

    db_receiver.updated_at = datetime.now()

    await session.commit()
    await session.refresh(db_receiver)

    return receiver_schema.Receiver.model_validate(db_receiver)


@router.patch(
    "/{receiver_id}",
    summary="Partially update a receiver",
    description="Partially update a receiver with the provided fields.",
    response_model=receiver_schema.Receiver,
)
async def patch_receiver(
    receiver_id: int,
    receiver_update: receiver_schema.ReceiverUpdate,
    session: AsyncSession = Depends(get_session),
) -> receiver_schema.Receiver:
    """Partially update a receiver (same as PUT in this implementation)."""
    return await update_receiver(receiver_id, receiver_update)


@router.delete(
    "/{receiver_id}",
    summary="Delete a receiver",
    description="Delete a receiver by ID.",
    status_code=204,
)
async def delete_receiver(
    receiver_id: int, session: AsyncSession = Depends(get_session)
):
    """Delete a receiver."""
    db_receiver = await session.get(Receiver, receiver_id)
    if not db_receiver:
        raise HTTPException(status_code=404, detail="Receiver not found")

    await session.delete(db_receiver)
    await session.commit()
    return None


@router.post(
    "/{receiver_id}/activate",
    summary="Activate a receiver",
    description="Activate a receiver by setting is_active to True.",
    response_model=receiver_schema.Receiver,
)
async def activate_receiver(
    receiver_id: int, session: AsyncSession = Depends(get_session)
) -> receiver_schema.Receiver:
    """Activate a receiver."""
    db_receiver = await session.get(Receiver, receiver_id)
    if not db_receiver:
        raise HTTPException(status_code=404, detail="Receiver not found")

    db_receiver.is_active = True

    db_receiver.updated_at = datetime.now()

    await session.commit()
    await session.refresh(db_receiver)

    return receiver_schema.Receiver.model_validate(db_receiver)


@router.post(
    "/{receiver_id}/deactivate",
    summary="Deactivate a receiver",
    description="Deactivate a receiver by setting is_active to False.",
    response_model=receiver_schema.Receiver,
)
async def deactivate_receiver(
    receiver_id: int, session: AsyncSession = Depends(get_session)
) -> receiver_schema.Receiver:
    """Deactivate a receiver."""
    db_receiver = await session.get(Receiver, receiver_id)
    if not db_receiver:
        raise HTTPException(status_code=404, detail="Receiver not found")

    db_receiver.is_active = False

    db_receiver.updated_at = datetime.now()

    await session.commit()
    await session.refresh(db_receiver)

    return receiver_schema.Receiver.model_validate(db_receiver)