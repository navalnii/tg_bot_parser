from pydantic import BaseModel
from datetime import date


class PriceBase(BaseModel):
    price: float


class PriceCreate(PriceBase):
    id: int
    item_id: int
    insert_date: date


class Price(PriceBase):
    pass

    class Config:
        orm_mode = True
