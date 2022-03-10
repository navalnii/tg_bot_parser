from typing import List, Optional, Sequence
from pydantic import BaseModel, HttpUrl


class SubscriptionBase(BaseModel):
    pass


class SubscriptionCreate(SubscriptionBase):
    item_id: int
    user_id: int


class Subscription(SubscriptionBase):
    pass

    class Config:
        orm_mode = True
