from typing import Optional, List, TYPE_CHECKING
from datetime import datetime
from sqlmodel import SQLModel, Field, Relationship

if TYPE_CHECKING:
    from .parcel_model import Parcel


class StationBase(SQLModel):
    name: str = Field(index=True)
    code: str = Field(unique=True, index=True)
    address: str
    city: str = Field(index=True)
    state: str = Field(index=True)
    postal_code: str
    phone: Optional[str] = None
    is_active: bool = Field(default=True)


class Station(StationBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

    # Relationships
    parcels_sent: List["Parcel"] = Relationship(
        back_populates="origin_station",
        sa_relationship_kwargs={"foreign_keys": "Parcel.origin_station_id"},
    )
    parcels_received: List["Parcel"] = Relationship(
        back_populates="destination_station",
        sa_relationship_kwargs={"foreign_keys": "Parcel.destination_station_id"},
    )