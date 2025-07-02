from typing import Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr
from datetime import datetime

router = APIRouter(prefix="/senders", tags=["senders"])


# Pydantic Models
class SenderBase(BaseModel):
    name: str
    email: EmailStr
    phone: Optional[str] = None
    address: Optional[str] = None
    is_active: bool = True


class SenderCreate(SenderBase):
    pass


class SenderUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    is_active: Optional[bool] = None


class Sender(SenderBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# In-memory storage for demo purposes
senders_db: dict[int, dict] = {}
next_id = 1


@router.get(
    "",
    summary="Get all senders",
    description="Retrieve a list of all senders with optional filtering.",
    response_model=list[Sender]
)
async def get_senders(
    skip: int = 0,
    limit: int = 100,
    is_active: Optional[bool] = None
) -> list[Sender]:
    """Get all senders with optional pagination and filtering."""
    senders = list(senders_db.values())
    
    # Filter by is_active if provided
    if is_active is not None:
        senders = [s for s in senders if s["is_active"] == is_active]
    
    # Apply pagination
    senders = senders[skip:skip + limit]
    
    return [Sender(**sender) for sender in senders]


@router.get(
    "/{sender_id}",
    summary="Get a sender by ID",
    description="Retrieve a specific sender using its unique identifier.",
    response_model=Sender
)
async def get_sender(sender_id: int) -> Sender:
    """Get a single sender by ID."""
    if sender_id not in senders_db:
        raise HTTPException(status_code=404, detail="Sender not found")
    
    return Sender(**senders_db[sender_id])


@router.post(
    "",
    summary="Create a new sender",
    description="Create a new sender with the provided details.",
    response_model=Sender,
    status_code=201
)
async def create_sender(sender: SenderCreate) -> Sender:
    """Create a new sender."""
    global next_id
    
    # Check if email already exists
    for existing_sender in senders_db.values():
        if existing_sender["email"] == sender.email:
            raise HTTPException(status_code=400, detail="Email already registered")
    
    now = datetime.now()
    sender_data = {
        "id": next_id,
        "created_at": now,
        "updated_at": now,
        **sender.model_dump()
    }
    
    senders_db[next_id] = sender_data
    result = Sender(**sender_data)
    next_id += 1
    
    return result


@router.put(
    "/{sender_id}",
    summary="Update an existing sender",
    description="Update an existing sender with the provided details.",
    response_model=Sender
)
async def update_sender(sender_id: int, sender_update: SenderUpdate) -> Sender:
    """Update an existing sender."""
    if sender_id not in senders_db:
        raise HTTPException(status_code=404, detail="Sender not found")
    
    existing_sender = senders_db[sender_id]
    
    # Check if email is being updated and already exists
    if sender_update.email:
        for sid, existing in senders_db.items():
            if sid != sender_id and existing["email"] == sender_update.email:
                raise HTTPException(status_code=400, detail="Email already registered")
    
    # Update only provided fields
    update_data = sender_update.model_dump(exclude_unset=True)
    if update_data:
        existing_sender.update(update_data)
        existing_sender["updated_at"] = datetime.now()
    
    return Sender(**existing_sender)


@router.patch(
    "/{sender_id}",
    summary="Partially update a sender",
    description="Partially update a sender with the provided fields.",
    response_model=Sender
)
async def patch_sender(sender_id: int, sender_update: SenderUpdate) -> Sender:
    """Partially update a sender (same as PUT in this implementation)."""
    return await update_sender(sender_id, sender_update)


@router.delete(
    "/{sender_id}",
    summary="Delete a sender",
    description="Delete a sender by ID.",
    status_code=204
)
async def delete_sender(sender_id: int):
    """Delete a sender."""
    if sender_id not in senders_db:
        raise HTTPException(status_code=404, detail="Sender not found")
    
    del senders_db[sender_id]
    return None


@router.post(
    "/{sender_id}/activate",
    summary="Activate a sender",
    description="Activate a sender by setting is_active to True.",
    response_model=Sender
)
async def activate_sender(sender_id: int) -> Sender:
    """Activate a sender."""
    if sender_id not in senders_db:
        raise HTTPException(status_code=404, detail="Sender not found")
    
    senders_db[sender_id]["is_active"] = True
    senders_db[sender_id]["updated_at"] = datetime.now()
    
    return Sender(**senders_db[sender_id])


@router.post(
    "/{sender_id}/deactivate",
    summary="Deactivate a sender",
    description="Deactivate a sender by setting is_active to False.",
    response_model=Sender
)
async def deactivate_sender(sender_id: int) -> Sender:
    """Deactivate a sender."""
    if sender_id not in senders_db:
        raise HTTPException(status_code=404, detail="Sender not found")
    
    senders_db[sender_id]["is_active"] = False
    senders_db[sender_id]["updated_at"] = datetime.now()
    
    return Sender(**senders_db[sender_id])