from enum import Enum
from pydantic import BaseModel
from typing import Sequence, List, Tuple
from db_service.schemas.Item_schema import Item


class PercentDiscountType(str, Enum):
    under_15 = 'under_15'
    from_15_to_25 = 'from_15_to_25'
    upper_25 = 'upper_25'


class UserBase(BaseModel):
    pass


class UserCreate(UserBase):
    id: int
    username: str
    is_active: bool = True
    discount_perc: List[PercentDiscountType]


class User(UserBase):
    id: int
    username: str
    is_active: bool = True
    discount_perc: str

    class Config:
        orm_mode = True


class UserGetItems(UserBase):
    results: Tuple[Item]

