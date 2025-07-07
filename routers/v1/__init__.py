from fastapi import APIRouter
from . import item_router, receiver_router

router = APIRouter(prefix="/v1")
router.include_router(item_router.router)
router.include_router(receiver_router.router)