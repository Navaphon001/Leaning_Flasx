from typing import Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr
from datetime import datetime

from schemas import receiver_schema

router = APIRouter(prefix="/receivers", tags=["receivers"])


receivers_db: dict[int, dict] = {}


@router.get(
    "",
    summary="Get all receivers",
    description="Retrieve a list of all receivers with optional filtering.",
    response_model=list[receiver_schema.Receiver],
)
async def get_receivers(
    skip: int = 0, limit: int = 100, is_active: Optional[bool] = None
) -> list[receiver_schema.Receiver]:
    """Get all receivers with optional pagination and filtering."""
    receivers = list(receivers_db.values())

    # Filter by is_active if provided
    if is_active is not None:
        receivers = [r for r in receivers if r["is_active"] == is_active]

    # Apply pagination
    receivers = receivers[skip : skip + limit]

    return [receiver_schema.Receiver(**receiver) for receiver in receivers]


@router.get(
    "/{receiver_id}",
    summary="Get a receiver by ID",
    description="Retrieve a specific receiver using its unique identifier.",
    response_model=receiver_schema.Receiver,
)
async def get_receiver(receiver_id: int) -> receiver_schema.Receiver:
    """Get a single receiver by ID."""
    if receiver_id not in receivers_db:
        raise HTTPException(
            status_code=404, detail="receiver_schema.Receiver not found"
        )

    return receiver_schema.Receiver(**receivers_db[receiver_id])


@router.post(
    "",
    summary="Create a new receiver",
    description="Create a new receiver with the provided details.",
    response_model=receiver_schema.Receiver,
    status_code=201,
)
async def create_receiver(
    receiver: receiver_schema.ReceiverCreate,
) -> receiver_schema.Receiver:
    """Create a new receiver."""
    global next_id

    # Check if email already exists
    for existing_receiver in receivers_db.values():
        if existing_receiver["email"] == receiver.email:
            raise HTTPException(status_code=400, detail="Email already registered")

    now = datetime.now()
    receiver_data = {
        "id": next_id,
        "created_at": now,
        "updated_at": now,
        **receiver.model_dump(),
    }

    receivers_db[next_id] = receiver_data
    result = receiver_schema.Receiver(**receiver_data)
    next_id += 1

    return result


@router.put(
    "/{receiver_id}",
    summary="Update an existing receiver",
    description="Update an existing receiver with the provided details.",
    response_model=receiver_schema.Receiver,
)
async def update_receiver(
    receiver_id: int, receiver_update: receiver_schema.ReceiverUpdate
) -> receiver_schema.Receiver:
    """Update an existing receiver."""
    if receiver_id not in receivers_db:
        raise HTTPException(
            status_code=404, detail="receiver_schema.Receiver not found"
        )

    existing_receiver = receivers_db[receiver_id]

    # Check if email is being updated and already exists
    if receiver_update.email:
        for rid, existing in receivers_db.items():
            if rid != receiver_id and existing["email"] == receiver_update.email:
                raise HTTPException(status_code=400, detail="Email already registered")

    # Update only provided fields
    update_data = receiver_update.model_dump(exclude_unset=True)
    if update_data:
        existing_receiver.update(update_data)
        existing_receiver["updated_at"] = datetime.now()

    return receiver_schema.Receiver(**existing_receiver)


@router.patch(
    "/{receiver_id}",
    summary="Partially update a receiver",
    description="Partially update a receiver with the provided fields.",
    response_model=receiver_schema.Receiver,
)
async def patch_receiver(
    receiver_id: int, receiver_update: receiver_schema.ReceiverUpdate
) -> receiver_schema.Receiver:
    """Partially update a receiver (same as PUT in this implementation)."""
    return await update_receiver(receiver_id, receiver_update)


@router.delete(
    "/{receiver_id}",
    summary="Delete a receiver",
    description="Delete a receiver by ID.",
    status_code=204,
)
async def delete_receiver(receiver_id: int):
    """Delete a receiver."""
    if receiver_id not in receivers_db:
        raise HTTPException(
            status_code=404, detail="receiver_schema.Receiver not found"
        )

    del receivers_db[receiver_id]
    return None


@router.post(
    "/{receiver_id}/activate",
    summary="Activate a receiver",
    description="Activate a receiver by setting is_active to True.",
    response_model=receiver_schema.Receiver,
)
async def activate_receiver(receiver_id: int) -> receiver_schema.Receiver:
    """Activate a receiver."""
    if receiver_id not in receivers_db:
        raise HTTPException(
            status_code=404, detail="receiver_schema.Receiver not found"
        )

    receivers_db[receiver_id]["is_active"] = True
    receivers_db[receiver_id]["updated_at"] = datetime.now()

    return receiver_schema.Receiver(**receivers_db[receiver_id])


@router.post(
    "/{receiver_id}/deactivate",
    summary="Deactivate a receiver",
    description="Deactivate a receiver by setting is_active to False.",
    response_model=receiver_schema.Receiver,
)
async def deactivate_receiver(receiver_id: int) -> receiver_schema.Receiver:
    """Deactivate a receiver."""
    if receiver_id not in receivers_db:
        raise HTTPException(
            status_code=404, detail="receiver_schema.Receiver not found"
        )

    receivers_db[receiver_id]["is_active"] = False
    receivers_db[receiver_id]["updated_at"] = datetime.now()

    return receiver_schema.Receiver(**receivers_db[receiver_id])