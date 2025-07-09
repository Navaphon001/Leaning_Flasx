from fastapi import APIRouter
from . import (
    item_router,
    receiver_router,
    sender_router,
    station_router,
    vehicle_router,
    delivery_staff_router,
    parcel_router,
)

router = APIRouter(prefix="/v1")
router.include_router(item_router.router)
router.include_router(receiver_router.router)
router.include_router(sender_router.router)
router.include_router(station_router.router)
router.include_router(vehicle_router.router)
router.include_router(delivery_staff_router.router)
router.include_router(parcel_router.router)