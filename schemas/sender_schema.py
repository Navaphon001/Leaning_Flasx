from typing import Optional
from datetime import datetime
from pydantic import BaseModel, EmailStr


class SenderBase(BaseModel):
    name: str
    email: str
    phone: Optional[str] = None
    address: Optional[str] = None
    is_active: bool = True


class SenderCreate(SenderBase):
    pass


class SenderUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    is_active: Optional[bool] = None


class Sender(SenderBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True