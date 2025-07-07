import decimal
import datetime
from pydantic import BaseModel, Field

from . import receiver_schema


class Item(BaseModel):
    weight: float = 0.0
    service_price: decimal.Decimal = 0.0
    # receiver: receiver_schema.Receiver | None = None