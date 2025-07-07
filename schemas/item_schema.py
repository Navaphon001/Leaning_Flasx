import decimal
import datetime
from pydantic import BaseModel, Field

from . import receiver_schema


class Item(BaseModel):
    id: int | None = None
    created_at: datetime.datetime | None = Field(default_factory=datetime.datetime.now)
    updated_at: datetime.datetime | None = Field(default_factory=datetime.datetime.now)
    weight: float = 0.0
    service_price: decimal.Decimal = 0.0
    # receiver: receiver_schema.Receiver | None = None