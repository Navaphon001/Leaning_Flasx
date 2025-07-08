from decimal import Decimal
from typing import Optional, TYPE_CHECKING
import datetime
from sqlmodel import SQLModel, Field, Relationship

from ..schemas import item_schema

if TYPE_CHECKING:
    from .receiver_model import Receiver


class Item(SQLModel, item_schema.ItemBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime.datetime = Field(default_factory=datetime.datetime.now)
    updated_at: datetime.datetime = Field(default_factory=datetime.datetime.now)

    # Foreign key and relationship
    receiver_id: Optional[int] = Field(default=None, foreign_key="receiver.id")
    receiver: Optional["Receiver"] = Relationship(back_populates="items")