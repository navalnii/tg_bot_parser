from typing import List, Optional, Sequence
from pydantic import BaseModel, HttpUrl
from datetime import date
from db_service.schemas import Item


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
