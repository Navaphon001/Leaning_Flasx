from decimal import Decimal
from typing import Optional, List
from datetime import datetime
from sqlmodel import SQLModel, Field, Relationship

# from .item_model import Item
from ..schemas import receiver_schema


class Receiver(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)