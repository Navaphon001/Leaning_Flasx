from typing import Optional
from datetime import datetime
from pydantic import BaseModel


class DeliveryStaffBase(BaseModel):
    name: str
    email: str
    phone: str
    employee_id: str
    is_active: bool = True


class DeliveryStaffCreate(DeliveryStaffBase):
    pass


class DeliveryStaffUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    employee_id: Optional[str] = None
    is_active: Optional[bool] = None


class DeliveryStaff(DeliveryStaffBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True