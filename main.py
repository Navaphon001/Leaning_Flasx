from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.get(
    "/items/{item_id}",
    tags=["items"],
    summary="Get an item by ID",
    description="Retrieve an item using its unique identifier.",
)
def read_item(item_id: int, q: str | None = None):
    return {"item_id": item_id, "q": q}

@app.get(
    "/items",
    tags=["items"],
    summary="Get all items",
    description="Retrieve a list of all items.",
)
async def read_items() -> dict:
    return {"items": ["item1", "item2", "item3"]}


@app.post(
    "/items",
    tags=["items"],
    summary="Create a new item",
    description="Create a new item with the provided details.",
)
async def create_item(item: dict) -> dict:
    return {"item": item}


@app.put(
    "/items/{item_id}",
    tags=["items"],
    summary="Update an existing item",
    description="Update an existing item with the provided details.",
)
async def update_item(item_id: int, item: dict) -> dict:
    return {"item_id": item_id, "item": item}


@app.delete(
    "/items/{item_id}",
    tags=["items"],
    summary="Delete an item",
    description="Delete an item using its unique identifier.",
)
async def delete_item(item_id: int) -> dict:
    return {"message": f"Item with id {item_id} deleted successfully."}


