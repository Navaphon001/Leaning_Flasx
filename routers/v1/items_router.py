from fastapi import APIRouter, Depends, HTTPException
from datetime import datetime

from sqlmodel import select

from sqlmodel.ext.asyncio.session import AsyncSession


from ...schemas import item_schema
from ...models import get_session, Item

router = APIRouter(prefix="/items", tags=["items"])


@router.get(
    "/{item_id}",
    summary="Get an item by ID",
    description="Retrieve an item using its unique identifier.",
    response_model=item_schema.Item,
)
async def read_item(
    item_id: int, session: AsyncSession = Depends(get_session)
) -> item_schema.Item:
    """Get a single item by ID."""
    db_item = await session.get(Item, item_id)
    if not db_item:
        raise HTTPException(status_code=404, detail="Item not found")
    return item_schema.Item.model_validate(db_item)


@router.get(
    "",
    summary="Get all items",
    description="Retrieve a list of all items.",
    response_model=list[item_schema.Item],
)

async def read_items(
    page: int = 1,
    size_per_page: int = 50,
    session: AsyncSession = Depends(get_session),
) -> list[item_schema.Item]:
    """Get all items with pagination."""
    query = select(Item).offset((page - 1) * size_per_page).limit(size_per_page)
    result = await session.exec(query)
    db_items = result.all()
    return [item_schema.Item.model_validate(item) for item in db_items]


@router.post(
    "",
    summary="Create a new item",
    description="Create a new item with the provided details.",
    response_model=item_schema.Item,
    status_code=201,
)
async def create_item(
    item: item_schema.ItemCreate, session: AsyncSession = Depends(get_session)
) -> item_schema.Item:
    """Create a new item."""
    db_item = Item(**item.model_dump())
    session.add(db_item)
    await session.commit()
    await session.refresh(db_item)
    return item_schema.Item.model_validate(db_item)


@router.put(
    "/{item_id}",
    summary="Update an existing item",
    description="Update an existing item with the provided details.",
    response_model=item_schema.Item,
)
async def update_item(
    item_id: int,
    item_update: item_schema.ItemUpdate,
    session: AsyncSession = Depends(get_session),
) -> item_schema.Item:
    """Update an existing item."""
    db_item = await session.get(Item, item_id)
    if not db_item:
        raise HTTPException(status_code=404, detail="Item not found")

    # Update only provided fields
    update_data = item_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_item, field, value)

    # Update timestamp

    db_item.updated_at = datetime.now()

    await session.commit()
    await session.refresh(db_item)
    return item_schema.Item.model_validate(db_item)


@router.delete(
    "/{item_id}",
    summary="Delete an item",
    description="Delete an item using its unique identifier.",
    status_code=204,
)

async def delete_item(item_id: int, session: AsyncSession = Depends(get_session)):
    """Delete an item."""
    db_item = await session.get(Item, item_id)
    if not db_item:
        raise HTTPException(status_code=404, detail="Item not found")

    await session.delete(db_item)
    await session.commit()
    return None