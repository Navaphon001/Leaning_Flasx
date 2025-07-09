from typing import Optional, List, TYPE_CHECKING
from datetime import datetime
from sqlmodel import SQLModel, Field, Relationship

if TYPE_CHECKING:
    from .parcel_model import Parcel


class DeliveryStaffBase(SQLModel):
    name: str = Field(index=True)
    email: str = Field(unique=True, index=True)
    phone: str
    employee_id: str = Field(unique=True, index=True)
    is_active: bool = Field(default=True)


class DeliveryStaff(DeliveryStaffBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

    # Relationships
    parcels: List["Parcel"] = Relationship(back_populates="delivery_staff")