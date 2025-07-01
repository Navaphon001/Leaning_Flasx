from typing import Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr
from datetime import datetime

router = APIRouter(prefix="/receivers", tags=["receivers"])


# Pydantic Models
class ReceiverBase(BaseModel):
    name: str
    email: EmailStr
    phone: Optional[str] = None
    address: Optional[str] = None
    is_active: bool = True


class ReceiverCreate(ReceiverBase):
    pass


class ReceiverUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    is_active: Optional[bool] = None


class Receiver(ReceiverBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# In-memory storage for demo purposes
receivers_db: dict[int, dict] = {}
next_id = 1


@router.get(
    "",
    summary="Get all receivers",
    description="Retrieve a list of all receivers with optional filtering.",
    response_model=list[Receiver]
)
async def get_receivers(
    skip: int = 0,
    limit: int = 100,
    is_active: Optional[bool] = None
) -> list[Receiver]:
    """Get all receivers with optional pagination and filtering."""
    receivers = list(receivers_db.values())
    
    # Filter by is_active if provided
    if is_active is not None:
        receivers = [r for r in receivers if r["is_active"] == is_active]
    
    # Apply pagination
    receivers = receivers[skip:skip + limit]
    
    return [Receiver(**receiver) for receiver in receivers]


@router.get(
    "/{receiver_id}",
    summary="Get a receiver by ID",
    description="Retrieve a specific receiver using its unique identifier.",
    response_model=Receiver
)
async def get_receiver(receiver_id: int) -> Receiver:
    """Get a single receiver by ID."""
    if receiver_id not in receivers_db:
        raise HTTPException(status_code=404, detail="Receiver not found")
    
    return Receiver(**receivers_db[receiver_id])


@router.post(
    "",
    summary="Create a new receiver",
    description="Create a new receiver with the provided details.",
    response_model=Receiver,
    status_code=201
)
async def create_receiver(receiver: ReceiverCreate) -> Receiver:
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
        **receiver.model_dump()
    }
    
    receivers_db[next_id] = receiver_data
    result = Receiver(**receiver_data)
    next_id += 1
    
    return result


@router.put(
    "/{receiver_id}",
    summary="Update an existing receiver",
    description="Update an existing receiver with the provided details.",
    response_model=Receiver
)
async def update_receiver(receiver_id: int, receiver_update: ReceiverUpdate) -> Receiver:
    """Update an existing receiver."""
    if receiver_id not in receivers_db:
        raise HTTPException(status_code=404, detail="Receiver not found")
    
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
    
    return Receiver(**existing_receiver)


@router.patch(
    "/{receiver_id}",
    summary="Partially update a receiver",
    description="Partially update a receiver with the provided fields.",
    response_model=Receiver
)
async def patch_receiver(receiver_id: int, receiver_update: ReceiverUpdate) -> Receiver:
    """Partially update a receiver (same as PUT in this implementation)."""
    return await update_receiver(receiver_id, receiver_update)


@router.delete(
    "/{receiver_id}",
    summary="Delete a receiver",
    description="Delete a receiver by ID.",
    status_code=204
)
async def delete_receiver(receiver_id: int):
    """Delete a receiver."""
    if receiver_id not in receivers_db:
        raise HTTPException(status_code=404, detail="Receiver not found")
    
    del receivers_db[receiver_id]
    return None


@router.post(
    "/{receiver_id}/activate",
    summary="Activate a receiver",
    description="Activate a receiver by setting is_active to True.",
    response_model=Receiver
)
async def activate_receiver(receiver_id: int) -> Receiver:
    """Activate a receiver."""
    if receiver_id not in receivers_db:
        raise HTTPException(status_code=404, detail="Receiver not found")
    
    receivers_db[receiver_id]["is_active"] = True
    receivers_db[receiver_id]["updated_at"] = datetime.now()
    
    return Receiver(**receivers_db[receiver_id])


@router.post(
    "/{receiver_id}/deactivate",
    summary="Deactivate a receiver",
    description="Deactivate a receiver by setting is_active to False.",
    response_model=Receiver
)
async def deactivate_receiver(receiver_id: int) -> Receiver:
    """Deactivate a receiver."""
    if receiver_id not in receivers_db:
        raise HTTPException(status_code=404, detail="Receiver not found")
    
    receivers_db[receiver_id]["is_active"] = False
    receivers_db[receiver_id]["updated_at"] = datetime.now()
    
    return Receiver(**receivers_db[receiver_id])