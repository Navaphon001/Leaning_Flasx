from typing import Optional
from datetime import datetime
from pydantic import BaseModel


class VehicleBase(BaseModel):
    license_plate: str
    type: str
    capacity: float
    is_active: bool = True


class VehicleCreate(VehicleBase):
    pass


class VehicleUpdate(BaseModel):
    license_plate: Optional[str] = None
    type: Optional[str] = None
    capacity: Optional[float] = None
    is_active: Optional[bool] = None


class Vehicle(VehicleBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True