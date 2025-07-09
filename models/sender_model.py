from typing import Optional, List, TYPE_CHECKING
from datetime import datetime
from sqlmodel import SQLModel, Field, Relationship

if TYPE_CHECKING:
    from .parcel_model import Parcel


class SenderBase(SQLModel):
    name: str = Field(index=True)
    email: str = Field(index=True)
    phone: Optional[str] = None
    address: Optional[str] = None
    is_active: bool = Field(default=True)


class Sender(SenderBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

    # Relationship
    parcels: List["Parcel"] = Relationship(back_populates="sender")