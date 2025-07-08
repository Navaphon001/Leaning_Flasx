import decimal
import datetime
from typing import Optional
from pydantic import BaseModel, Field

from . import receiver_schema


class ItemBase(BaseModel):
    weight: float = 0.0
    service_price: decimal.Decimal = 0.0

class ItemCreate(ItemBase):
    receiver_id: Optional[int] = None


class ItemUpdate(BaseModel):
    weight: Optional[float] = None
    service_price: Optional[decimal.Decimal] = None
    receiver_id: Optional[int] = None


class Item(ItemBase):
    id: Optional[int] = None
    created_at: Optional[datetime.datetime] = None
    updated_at: Optional[datetime.datetime] = None
    receiver_id: Optional[int] = None

    class Config:
        from_attributes = True