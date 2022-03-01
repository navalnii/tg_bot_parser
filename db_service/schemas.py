from typing import List, Optional, Sequence
from pydantic import BaseModel, HttpUrl
from datetime import date


class ItemBase(BaseModel):
    source: str
    title: str
    description: Optional[str] = None


class ItemCreate(ItemBase):
    id: int
    url: HttpUrl
    cato_id: str
    insert_date: date


class Item(ItemBase):
    id: int
    url: HttpUrl
    cato_id: str
    insert_date: date

    class Config:
        orm_mode = True


class UserBase(BaseModel):
    discount_perc: int


class UserCreate(UserBase):
    id: int
    phone: str
    is_active: bool


class User(UserBase):
    pass

    class Config:
        orm_mode = True


class UserGetItems(UserBase):
    results: Sequence(Item)


class SubscriptionBase(BaseModel):
    pass


class SubscriptionCreate(SubscriptionBase):
    id: int
    item_id: int
    user_id: int


class Subscription(SubscriptionBase):
    pass

    class Config:
        orm_mode = True


class PriceBase(BaseModel):
    price: float


class PriceCreate(PriceBase):
    item_id: int
    insert_date: date


class Price(PriceBase):
    pass

    class Config:
        orm_mode = True