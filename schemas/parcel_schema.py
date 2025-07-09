from typing import Optional
from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel
from enum import Enum


class ParcelStatus(str, Enum):
    CREATED = "created"
    PICKED_UP = "picked_up"
    IN_TRANSIT = "in_transit"
    AT_DESTINATION = "at_destination"
    OUT_FOR_DELIVERY = "out_for_delivery"
    DELIVERED = "delivered"
    FAILED_DELIVERY = "failed_delivery"
    RETURNED = "returned"


class ParcelBase(BaseModel):
    tracking_number: str
    weight: float
    length: float
    width: float
    height: float
    service_price: Decimal
    status: ParcelStatus = ParcelStatus.CREATED
    description: Optional[str] = None
    special_instructions: Optional[str] = None
    sender_id: int
    receiver_id: int


class ParcelCreate(ParcelBase):
    origin_station_id: Optional[int] = None
    destination_station_id: Optional[int] = None


class ParcelUpdate(BaseModel):
    weight: Optional[float] = None
    length: Optional[float] = None
    width: Optional[float] = None
    height: Optional[float] = None
    service_price: Optional[Decimal] = None
    status: Optional[ParcelStatus] = None
    description: Optional[str] = None
    special_instructions: Optional[str] = None
    origin_station_id: Optional[int] = None
    destination_station_id: Optional[int] = None
    vehicle_id: Optional[int] = None
    delivery_staff_id: Optional[int] = None


class Parcel(ParcelBase):
    id: int
    created_at: datetime
    updated_at: datetime
    origin_station_id: Optional[int] = None
    destination_station_id: Optional[int] = None
    vehicle_id: Optional[int] = None
    delivery_staff_id: Optional[int] = None

    class Config:
        from_attributes = True


class ParcelTracking(BaseModel):
    """Simplified tracking response for public API"""

    tracking_number: str
    status: ParcelStatus
    created_at: datetime
    updated_at: datetime
    origin_station_name: Optional[str] = None
    destination_station_name: Optional[str] = None

    class Config:
        from_attributes = True