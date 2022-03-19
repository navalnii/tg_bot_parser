from pydantic import BaseModel
from typing import Sequence
from db_service.schemas.item_schema import Item


class PriceBase(BaseModel):
    price: float
    seller: str


class PriceCreate(PriceBase):
    item_id: int


class Price(PriceBase):
    pass

    class Config:
        orm_mode = True


