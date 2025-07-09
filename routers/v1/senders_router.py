from typing import Optional
from fastapi import APIRouter, HTTPException, Depends
from datetime import datetime
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from flasx.schemas import sender_schema
from flasx.models import get_session, Sender

router = APIRouter(prefix="/senders", tags=["senders"])


@router.get(
    "",
    summary="Get all senders",
    description="Retrieve a list of all senders with optional filtering.",
    response_model=list[sender_schema.Sender],
)
async def get_senders(
    skip: int = 0,
    limit: int = 100,
    is_active: Optional[bool] = None,
    session: AsyncSession = Depends(get_session),
) -> list[sender_schema.Sender]:
    """Get all senders with optional pagination and filtering."""
    query = select(Sender)

    # Filter by is_active if provided
    if is_active is not None:
        query = query.where(Sender.is_active == is_active)

    # Apply pagination
    query = query.offset(skip).limit(limit)

    result = await session.exec(query)
    senders = result.all()

    return [sender_schema.Sender.model_validate(sender) for sender in senders]


@router.get(
    "/{sender_id}",
    summary="Get a sender by ID",
    description="Retrieve a specific sender using its unique identifier.",
    response_model=sender_schema.Sender,
)
async def get_sender(
    sender_id: int, session: AsyncSession = Depends(get_session)
) -> sender_schema.Sender:
    """Get a single sender by ID."""
    sender = await session.get(Sender, sender_id)
    if not sender:
        raise HTTPException(status_code=404, detail="Sender not found")

    return sender_schema.Sender.model_validate(sender)


@router.post(
    "",
    summary="Create a new sender",
    description="Create a new sender with the provided details.",
    response_model=sender_schema.Sender,
    status_code=201,
)
async def create_sender(
    sender: sender_schema.SenderCreate,
    session: AsyncSession = Depends(get_session),
) -> sender_schema.Sender:
    """Create a new sender."""
    # Check if email already exists
    query = select(Sender).where(Sender.email == sender.email)
    result = await session.exec(query)
    existing_sender = result.first()

    if existing_sender:
        raise HTTPException(status_code=400, detail="Email already registered")

    # Create new sender
    db_sender = Sender(**sender.model_dump())
    session.add(db_sender)
    await session.commit()
    await session.refresh(db_sender)

    return sender_schema.Sender.model_validate(db_sender)


@router.put(
    "/{sender_id}",
    summary="Update an existing sender",
    description="Update an existing sender with the provided details.",
    response_model=sender_schema.Sender,
)
async def update_sender(
    sender_id: int,
    sender_update: sender_schema.SenderUpdate,
    session: AsyncSession = Depends(get_session),
) -> sender_schema.Sender:
    """Update an existing sender."""
    db_sender = await session.get(Sender, sender_id)
    if not db_sender:
        raise HTTPException(status_code=404, detail="Sender not found")

    # Check if email is being updated and already exists
    if sender_update.email:
        query = select(Sender).where(
            Sender.email == sender_update.email, Sender.id != sender_id
        )
        result = await session.exec(query)
        existing_sender = result.first()

        if existing_sender:
            raise HTTPException(status_code=400, detail="Email already registered")

    # Update only provided fields
    update_data = sender_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_sender, field, value)

    # Update timestamp
    db_sender.updated_at = datetime.now()

    await session.commit()
    await session.refresh(db_sender)

    return sender_schema.Sender.model_validate(db_sender)


@router.delete(
    "/{sender_id}",
    summary="Delete a sender",
    description="Delete a sender by ID.",
    status_code=204,
)
async def delete_sender(sender_id: int, session: AsyncSession = Depends(get_session)):
    """Delete a sender."""
    db_sender = await session.get(Sender, sender_id)
    if not db_sender:
        raise HTTPException(status_code=404, detail="Sender not found")

    await session.delete(db_sender)
    await session.commit()
    return None