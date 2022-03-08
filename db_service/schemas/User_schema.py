from pydantic import BaseModel
from typing import Sequence, List, Tuple
from db_service.schemas.Item_schema import Item


class UserBase(BaseModel):
    pass


class UserCreate(UserBase):
    id: int
    username: str
    is_active: bool = True
    discount_perc: str


class User(UserBase):
    id: int
    username: str
    is_active: bool = True
    discount_perc: str

    class Config:
        orm_mode = True


class UserGetItems(UserBase):
    results: Tuple[Item]

