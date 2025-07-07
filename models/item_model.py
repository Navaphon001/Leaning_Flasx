from decimal import Decimal
from typing import Optional
import datetime
from sqlmodel import SQLModel, Field, Relationship

from ..schemas import item_schema
from . import receiver_model


class Item(item_schema.Item, SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime.datetime = Field(default_factory=datetime.datetime.now)
    updated_at: datetime.datetime = Field(default_factory=datetime.datetime.now)