from typing import List, Optional, Sequence
from pydantic import BaseModel, HttpUrl
from datetime import date


class ItemBase(BaseModel):
    source: str
    title: str
    description: Optional[str] = None


class ItemCreate(ItemBase):
    id: int
    title: str
    description: Optional[str] = None
    source: str
    cato_id: str
    url: HttpUrl
    insert_date: date


class Item(ItemBase):
    id: int
    title: str
    description: Optional[str] = None
    source: str
    cato_id: str
    url: HttpUrl
    insert_date: date

    class Config:
        orm_mode = True

