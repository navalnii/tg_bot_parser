from typing import List, Optional, Sequence
from pydantic import BaseModel, HttpUrl
from datetime import date


class PriceBase(BaseModel):
    price: float


class PriceCreate(PriceBase):
    item_id: int
    insert_date: date


class Price(PriceBase):
    pass

    class Config:
        orm_mode = True
