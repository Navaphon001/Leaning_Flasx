from typing import Optional, List, TYPE_CHECKING
from datetime import datetime
from sqlmodel import SQLModel, Field, Relationship

if TYPE_CHECKING:
    from .parcel_model import Parcel


class VehicleBase(SQLModel):
    license_plate: str = Field(unique=True, index=True)
    type: str = Field(index=True)  # truck, van, motorcycle, etc.
    capacity: float  # in kg
    is_active: bool = Field(default=True)


class Vehicle(VehicleBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

    # Relationships
    parcels: List["Parcel"] = Relationship(back_populates="vehicle")