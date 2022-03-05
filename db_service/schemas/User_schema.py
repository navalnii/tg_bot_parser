from pydantic import BaseModel


class UserBase(BaseModel):
    discount_perc: int


class UserCreate(UserBase):
    id: int
    username: str
    is_active: bool = True


class User(UserBase):
    pass

    class Config:
        orm_mode = True


# class UserGetItems(UserBase):
#     results: Sequence(Item)
