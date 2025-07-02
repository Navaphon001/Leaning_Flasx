from typing import Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr
from datetime import datetime

router = APIRouter(prefix="/delivery-staffs", tags=["delivery_staffs"])


# Pydantic Models
class DeliveryStaffBase(BaseModel):
    name: str
    email: EmailStr
    phone: Optional[str] = None
    address: Optional[str] = None
    is_active: bool = True


class DeliveryStaffCreate(DeliveryStaffBase):
    pass


class DeliveryStaffUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    is_active: Optional[bool] = None


class DeliveryStaff(DeliveryStaffBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# In-memory storage for demo purposes
delivery_staffs_db: dict[int, dict] = {}
next_id = 1


@router.get(
    "",
    summary="Get all delivery staffs",
    description="Retrieve a list of all delivery staffs with optional filtering.",
    response_model=list[DeliveryStaff]
)
async def get_delivery_staffs(
    skip: int = 0,
    limit: int = 100,
    is_active: Optional[bool] = None
) -> list[DeliveryStaff]:
    """Get all delivery staffs with optional pagination and filtering."""
    staffs = list(delivery_staffs_db.values())
    
    # Filter by is_active if provided
    if is_active is not None:
        staffs = [s for s in staffs if s["is_active"] == is_active]
    
    # Apply pagination
    staffs = staffs[skip:skip + limit]
    
    return [DeliveryStaff(**staff) for staff in staffs]


@router.get(
    "/{staff_id}",
    summary="Get a delivery staff by ID",
    description="Retrieve a specific delivery staff using its unique identifier.",
    response_model=DeliveryStaff
)
async def get_delivery_staff(staff_id: int) -> DeliveryStaff:
    """Get a single delivery staff by ID."""
    if staff_id not in delivery_staffs_db:
        raise HTTPException(status_code=404, detail="Delivery staff not found")
    
    return DeliveryStaff(**delivery_staffs_db[staff_id])


@router.post(
    "",
    summary="Create a new delivery staff",
    description="Create a new delivery staff with the provided details.",
    response_model=DeliveryStaff,
    status_code=201
)
async def create_delivery_staff(staff: DeliveryStaffCreate) -> DeliveryStaff:
    """Create a new delivery staff."""
    global next_id
    
    # Check if email already exists
    for existing_staff in delivery_staffs_db.values():
        if existing_staff["email"] == staff.email:
            raise HTTPException(status_code=400, detail="Email already registered")
    
    now = datetime.now()
    staff_data = {
        "id": next_id,
        "created_at": now,
        "updated_at": now,
        **staff.model_dump()
    }
    
    delivery_staffs_db[next_id] = staff_data
    result = DeliveryStaff(**staff_data)
    next_id += 1
    
    return result


@router.put(
    "/{staff_id}",
    summary="Update an existing delivery staff",
    description="Update an existing delivery staff with the provided details.",
    response_model=DeliveryStaff
)
async def update_delivery_staff(staff_id: int, staff_update: DeliveryStaffUpdate) -> DeliveryStaff:
    """Update an existing delivery staff."""
    if staff_id not in delivery_staffs_db:
        raise HTTPException(status_code=404, detail="Delivery staff not found")
    
    existing_staff = delivery_staffs_db[staff_id]
    
    # Check if email is being updated and already exists
    if staff_update.email:
        for sid, existing in delivery_staffs_db.items():
            if sid != staff_id and existing["email"] == staff_update.email:
                raise HTTPException(status_code=400, detail="Email already registered")
    
    # Update only provided fields
    update_data = staff_update.model_dump(exclude_unset=True)
    if update_data:
        existing_staff.update(update_data)
        existing_staff["updated_at"] = datetime.now()
    
    return DeliveryStaff(**existing_staff)


@router.patch(
    "/{staff_id}",
    summary="Partially update a delivery staff",
    description="Partially update a delivery staff with the provided fields.",
    response_model=DeliveryStaff
)
async def patch_delivery_staff(staff_id: int, staff_update: DeliveryStaffUpdate) -> DeliveryStaff:
    """Partially update a delivery staff (same as PUT in this implementation)."""
    return await update_delivery_staff(staff_id, staff_update)


@router.delete(
    "/{staff_id}",
    summary="Delete a delivery staff",
    description="Delete a delivery staff by ID.",
    status_code=204
)
async def delete_delivery_staff(staff_id: int):
    """Delete a delivery staff."""
    if staff_id not in delivery_staffs_db:
        raise HTTPException(status_code=404, detail="Delivery staff not found")
    
    del delivery_staffs_db[staff_id]
    return None


@router.post(
    "/{staff_id}/activate",
    summary="Activate a delivery staff",
    description="Activate a delivery staff by setting is_active to True.",
    response_model=DeliveryStaff
)
async def activate_delivery_staff(staff_id: int) -> DeliveryStaff:
    """Activate a delivery staff."""
    if staff_id not in delivery_staffs_db:
        raise HTTPException(status_code=404, detail="Delivery staff not found")
    
    delivery_staffs_db[staff_id]["is_active"] = True
    delivery_staffs_db[staff_id]["updated_at"] = datetime.now()
    
    return DeliveryStaff(**delivery_staffs_db[staff_id])


@router.post(
    "/{staff_id}/deactivate",
    summary="Deactivate a delivery staff",
    description="Deactivate a delivery staff by setting is_active to False.",
    response_model=DeliveryStaff
)
async def deactivate_delivery_staff(staff_id: int) -> DeliveryStaff:
    """Deactivate a delivery staff."""
    if staff_id not in delivery_staffs_db:
        raise HTTPException(status_code=404, detail="Delivery staff not found")
    
    delivery_staffs_db[staff_id]["is_active"] = False
    delivery_staffs_db[staff_id]["updated_at"] = datetime.now()
    
    return DeliveryStaff(**delivery_staffs_db[staff_id])