from pydantic import BaseModel


class PriceBase(BaseModel):
    price: float


class PriceCreate(PriceBase):
    item_id: int


class Price(PriceBase):
    pass

    class Config:
        orm_mode = True
