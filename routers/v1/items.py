from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(prefix="/items", tags=["items"])


class Item(BaseModel):
    name: str
    price: float
    is_offer: bool = False


@router.get(
    "/{item_id}",
    summary="Get an item by ID",
    description="Retrieve an item using its unique identifier.",
)
async def read_item(item_id: int, page: int = 1, size_per_page: int = 50) -> Item:
    return Item(name="Sample Item", price=10.99, is_offer=False)


@router.get(
    "",
    summary="Get all items",
    description="Retrieve a list of all items.",
)
async def read_items() -> list[Item]:
    return [
        Item(name="Item 1", price=10.99, is_offer=False),
        Item(name="Item 2", price=20.99, is_offer=True),
        Item(name="Item 3", price=30.99, is_offer=False),
    ]


@router.post(
    "",
    summary="Create a new item",
    description="Create a new item with the provided details.",
)
async def create_item(item: Item) -> Item:
    return item


@router.put(
    "/{item_id}",
    summary="Update an existing item",
    description="Update an existing item with the provided details.",
)
async def update_item(item_id: int, item: Item) -> Item:
    return item


@router.delete(
    "/{item_id}",
    summary="Delete an item",
    description="Delete an item using its unique identifier.",
)
async def delete_item(item_id: int) -> dict:
    return {"message": f"Item with id {item_id} deleted successfully."}