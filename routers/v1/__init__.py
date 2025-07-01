from fastapi import APIRouter
from . import items, receivers

router = APIRouter(prefix="/v1")
router.include_router(items.router)
router.include_router(receivers.router)