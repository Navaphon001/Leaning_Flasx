from fastapi import APIRouter
from pydantic import BaseModel
import decimal

from ...schemas import receiver_schema

from ...schemas import item_schema
from ...models import item_model
from ... import models

router = APIRouter(prefix="/items", tags=["items"])


@router.get(
    "/{item_id}",
    summary="Get an item by ID",
    description="Retrieve an item using its unique identifier.",
)
async def read_item(
    item_id: int, page: int = 1, size_per_page: int = 50
) -> item_model.Item:
    db_item = models.session.get(item_model.Item, item_id)
    if not db_item:
        return None
    return db_item


@router.get(
    "",
    summary="Get all items",
    description="Retrieve a list of all items.",
)
async def read_items() -> list[item_schema.Item]:
    return [
        item_schema.Item(name="Item 1", price=10.99, is_offer=False),
        item_schema.Item(name="Item 2", price=20.99, is_offer=True),
        item_schema.Item(name="Item 3", price=30.99, is_offer=False),
    ]


@router.post(
    "",
    summary="Create a new item",
    description="Create a new item with the provided details.",
)
async def create_item(item: item_schema.Item) -> item_model.Item:
    print(f"Creating item: {item.model_dump()}")
    db_item = item_model.Item(**item.model_dump(exclude_unset=True))
    models.session.add(db_item)
    models.session.commit()
    return db_item


@router.put(
    "/{item_id}",
    summary="Update an existing item",
    description="Update an existing item with the provided details.",
)
async def update_item(item_id: int, item: item_schema.Item) -> item_schema.Item:
    return item


@router.delete(
    "/{item_id}",
    summary="Delete an item",
    description="Delete an item using its unique identifier.",
)
async def delete_item(item_id: int) -> dict:
    return {"message": f"Item with id {item_id} deleted successfully."}