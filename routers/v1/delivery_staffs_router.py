from typing import Optional
from fastapi import APIRouter, HTTPException, Depends
from datetime import datetime
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from schemas import delivery_staff_schema
from models import get_session, DeliveryStaff

router = APIRouter(prefix="/delivery-staff", tags=["delivery-staff"])


@router.get(
    "",
    summary="Get all delivery staff",
    description="Retrieve a list of all delivery staff with optional filtering.",
    response_model=list[delivery_staff_schema.DeliveryStaff],
)
async def get_delivery_staff(
    skip: int = 0,
    limit: int = 100,
    is_active: Optional[bool] = None,
    session: AsyncSession = Depends(get_session),
) -> list[delivery_staff_schema.DeliveryStaff]:
    """Get all delivery staff with optional pagination and filtering."""
    query = select(DeliveryStaff)

    # Filter by is_active if provided
    if is_active is not None:
        query = query.where(DeliveryStaff.is_active == is_active)

    # Apply pagination
    query = query.offset(skip).limit(limit)

    result = await session.exec(query)
    staff = result.all()

    return [delivery_staff_schema.DeliveryStaff.model_validate(s) for s in staff]


@router.get(
    "/{staff_id}",
    summary="Get delivery staff by ID",
    description="Retrieve a specific delivery staff member using their unique identifier.",
    response_model=delivery_staff_schema.DeliveryStaff,
)
async def get_delivery_staff_by_id(
    staff_id: int, session: AsyncSession = Depends(get_session)
) -> delivery_staff_schema.DeliveryStaff:
    """Get a single delivery staff member by ID."""
    staff = await session.get(DeliveryStaff, staff_id)
    if not staff:
        raise HTTPException(status_code=404, detail="Delivery staff not found")

    return delivery_staff_schema.DeliveryStaff.model_validate(staff)


@router.get(
    "/employee/{employee_id}",
    summary="Get delivery staff by employee ID",
    description="Retrieve a specific delivery staff member using their employee ID.",
    response_model=delivery_staff_schema.DeliveryStaff,
)
async def get_delivery_staff_by_employee_id(
    employee_id: str, session: AsyncSession = Depends(get_session)
) -> delivery_staff_schema.DeliveryStaff:
    """Get a single delivery staff member by employee ID."""
    query = select(DeliveryStaff).where(DeliveryStaff.employee_id == employee_id)
    result = await session.exec(query)
    staff = result.first()

    if not staff:
        raise HTTPException(status_code=404, detail="Delivery staff not found")

    return delivery_staff_schema.DeliveryStaff.model_validate(staff)


@router.post(
    "",
    summary="Create a new delivery staff",
    description="Create a new delivery staff member with the provided details.",
    response_model=delivery_staff_schema.DeliveryStaff,
    status_code=201,
)
async def create_delivery_staff(
    staff: delivery_staff_schema.DeliveryStaffCreate,
    session: AsyncSession = Depends(get_session),
) -> delivery_staff_schema.DeliveryStaff:
    """Create a new delivery staff member."""
    # Check if email already exists
    query = select(DeliveryStaff).where(DeliveryStaff.email == staff.email)
    result = await session.exec(query)
    existing_staff = result.first()

    if existing_staff:
        raise HTTPException(status_code=400, detail="Email already registered")

    # Check if employee_id already exists
    query = select(DeliveryStaff).where(DeliveryStaff.employee_id == staff.employee_id)
    result = await session.exec(query)
    existing_staff = result.first()

    if existing_staff:
        raise HTTPException(status_code=400, detail="Employee ID already exists")

    # Create new delivery staff
    db_staff = DeliveryStaff(**staff.model_dump())
    session.add(db_staff)
    await session.commit()
    await session.refresh(db_staff)

    return delivery_staff_schema.DeliveryStaff.model_validate(db_staff)


@router.put(
    "/{staff_id}",
    summary="Update an existing delivery staff",
    description="Update an existing delivery staff member with the provided details.",
    response_model=delivery_staff_schema.DeliveryStaff,
)
async def update_delivery_staff(
    staff_id: int,
    staff_update: delivery_staff_schema.DeliveryStaffUpdate,
    session: AsyncSession = Depends(get_session),
) -> delivery_staff_schema.DeliveryStaff:
    """Update an existing delivery staff member."""
    db_staff = await session.get(DeliveryStaff, staff_id)
    if not db_staff:
        raise HTTPException(status_code=404, detail="Delivery staff not found")

    # Check if email is being updated and already exists
    if staff_update.email:
        query = select(DeliveryStaff).where(
            DeliveryStaff.email == staff_update.email, DeliveryStaff.id != staff_id
        )
        result = await session.exec(query)
        existing_staff = result.first()

        if existing_staff:
            raise HTTPException(status_code=400, detail="Email already registered")

    # Check if employee_id is being updated and already exists
    if staff_update.employee_id:
        query = select(DeliveryStaff).where(
            DeliveryStaff.employee_id == staff_update.employee_id,
            DeliveryStaff.id != staff_id,
        )
        result = await session.exec(query)
        existing_staff = result.first()

        if existing_staff:
            raise HTTPException(status_code=400, detail="Employee ID already exists")

    # Update only provided fields
    update_data = staff_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_staff, field, value)

    # Update timestamp
    db_staff.updated_at = datetime.now()

    await session.commit()
    await session.refresh(db_staff)

    return delivery_staff_schema.DeliveryStaff.model_validate(db_staff)


@router.delete(
    "/{staff_id}",
    summary="Delete a delivery staff",
    description="Delete a delivery staff member by ID.",
    status_code=204,
)
async def delete_delivery_staff(
    staff_id: int, session: AsyncSession = Depends(get_session)
):
    """Delete a delivery staff member."""
    db_staff = await session.get(DeliveryStaff, staff_id)
    if not db_staff:
        raise HTTPException(status_code=404, detail="Delivery staff not found")

    await session.delete(db_staff)
    await session.commit()
    return None