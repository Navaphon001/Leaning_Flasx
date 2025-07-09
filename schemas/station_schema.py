from typing import Optional
from datetime import datetime
from pydantic import BaseModel


class StationBase(BaseModel):
    name: str
    code: str
    address: str
    city: str
    state: str
    postal_code: str
    phone: Optional[str] = None
    is_active: bool = True


class StationCreate(StationBase):
    pass


class StationUpdate(BaseModel):
    name: Optional[str] = None
    code: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    postal_code: Optional[str] = None
    phone: Optional[str] = None
    is_active: Optional[bool] = None


class Station(StationBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True