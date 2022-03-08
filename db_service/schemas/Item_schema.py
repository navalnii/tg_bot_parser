from typing import Optional
from pydantic import BaseModel, HttpUrl
from datetime import datetime


class ItemBase(BaseModel):
    pass


class ItemCreate(ItemBase):
    id: int
    title: str
    description: Optional[str] = None
    source: str
    cato_id: str
    url: HttpUrl
    insert_date: datetime


class Item(ItemBase):
    id: int
    title: str
    description: Optional[str] = None
    source: str
    cato_id: str
    url: HttpUrl
    insert_date: datetime

    class Config:
        orm_mode = True

