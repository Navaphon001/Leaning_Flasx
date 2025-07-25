from decimal import Decimal
from typing import Optional, List, TYPE_CHECKING
from datetime import datetime
from sqlmodel import SQLModel, Field, Relationship

from ..schemas import receiver_schema

if TYPE_CHECKING:
    from .parcel_model import Parcel

class Receiver(SQLModel, receiver_schema.ReceiverBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

    parcels: List["Parcel"] = Relationship(back_populates="receiver")