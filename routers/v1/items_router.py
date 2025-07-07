from select import select
from fastapi import APIRouter, Depends
from pydantic import BaseModel
import decimal

from typing import Optional, Annotated

from sqlmodel import Field, SQLModel, Session, select, func
from sqlmodel.ext.asyncio.session import AsyncSession

from ...schemas import receiver_schema

from ...schemas import item_schema
from ...models import item_model
from ... import models
from fastapi import HTTPException

router = APIRouter(prefix="/items", tags=["items"])


@router.get(
    "/{item_id}",
    summary="Get an item by ID",
    description="Retrieve an item using its unique identifier.",
)
async def read_item(
    item_id: int, session: Annotated[AsyncSession, Depends(models.get_session)]
) -> item_model.Item | None:
    db_item = await session.get(item_model.Item, item_id)
    print(f"Fetching item with ID {item_id}: {db_item}")
    if not db_item:
        raise HTTPException(status_code=404, detail="Item not found")
    return db_item


@router.get(
    "",
    summary="Get all items",
    description="Retrieve a list of all items.",
)
async def read_items(page=1, size_per_page=50) -> list[item_schema.Item]:
    session = models.get_session()
    db_items = (
        await session.exec(
            select(item_model.Item)
            .offset((page - 1) * size_per_page)
            .limit(size_per_page)
        )
        .scalars()
        .all()
    )
    return db_items


@router.post(
    "",
    summary="Create a new item",
    description="Create a new item with the provided details.",
)
async def create_item(item: item_schema.Item) -> item_model.Item:
    print(f"Creating item: {item.model_dump()}")
    db_item = item_model.Item(**item.model_dump(exclude_unset=True))
    session = models.get_session()
    await session.add(db_item)
    await session.commit()
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