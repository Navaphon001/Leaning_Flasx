from typing import Optional, TYPE_CHECKING
from datetime import datetime
from decimal import Decimal
from enum import Enum
from sqlmodel import SQLModel, Field, Relationship

if TYPE_CHECKING:
    from .sender_model import Sender
    from .receiver_model import Receiver
    from .station_model import Station
    from .vehicle_model import Vehicle
    from .delivery_staff_model import DeliveryStaff


class ParcelStatus(str, Enum):
    CREATED = "created"
    PICKED_UP = "picked_up"
    IN_TRANSIT = "in_transit"
    AT_DESTINATION = "at_destination"
    OUT_FOR_DELIVERY = "out_for_delivery"
    DELIVERED = "delivered"
    FAILED_DELIVERY = "failed_delivery"
    RETURNED = "returned"


class ParcelBase(SQLModel):
    tracking_number: str = Field(unique=True, index=True)
    weight: float
    length: float
    width: float
    height: float
    service_price: Decimal
    status: ParcelStatus = Field(default=ParcelStatus.CREATED)
    description: Optional[str] = None
    special_instructions: Optional[str] = None


class Parcel(ParcelBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

    # Foreign keys
    sender_id: int = Field(foreign_key="sender.id")
    receiver_id: int = Field(foreign_key="receiver.id")
    origin_station_id: Optional[int] = Field(default=None, foreign_key="station.id")
    destination_station_id: Optional[int] = Field(
        default=None, foreign_key="station.id"
    )
    vehicle_id: Optional[int] = Field(default=None, foreign_key="vehicle.id")
    delivery_staff_id: Optional[int] = Field(
        default=None, foreign_key="deliverystaff.id"
    )

    # Relationships
    sender: "Sender" = Relationship(back_populates="parcels")
    receiver: "Receiver" = Relationship(back_populates="parcels")
    origin_station: Optional["Station"] = Relationship(
        back_populates="parcels_sent",
        sa_relationship_kwargs={"foreign_keys": "Parcel.origin_station_id"},
    )
    destination_station: Optional["Station"] = Relationship(
        back_populates="parcels_received",
        sa_relationship_kwargs={"foreign_keys": "Parcel.destination_station_id"},
    )
    vehicle: Optional["Vehicle"] = Relationship(back_populates="parcels")
    delivery_staff: Optional["DeliveryStaff"] = Relationship(back_populates="parcels")