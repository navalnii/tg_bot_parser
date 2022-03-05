from sqlalchemy import Boolean, Column, ForeignKey, Integer, Float, String, Date, Enum
from sqlalchemy.orm import relationship
from db_service.database import Base
import enum


class PercentDiscountType(enum.Enum):
    under_15 = 1
    from_15_to_25 = 2
    upper_25 = 3


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, index=True)
    is_active = Column(Boolean, default=True)
    discount_perc = Column(Enum(PercentDiscountType), index=True)

    subs = relationship("Subscription", back_populates="owner")


class Subscription(Base):
    __tablename__ = 'subscriptions'

    id = Column(String, primary_key=True)
    item_id = Column(Integer, ForeignKey("items.id"))
    user_id = Column(Integer, ForeignKey("users.id"))

    owner = relationship("User", back_populates="subs")
    owner_ = relationship("Item", back_populates="item")


class Item(Base):
    __tablename__ = 'items'

    id = Column(Integer, primary_key=True)
    source = Column(String, index=True)
    title = Column(String, index=True)
    description = Column(String)
    url = Column(String, index=True)
    cato_id = Column(String, index=True)
    insert_date = Column(Date)

    item = relationship("Subscription", back_populates="owner_")
    item_price = relationship("Price", back_populates="price_id")


class Price(Base):
    __tablename__ = "prices"

    id = Column(String, primary_key=True)
    item_id = Column(Integer, ForeignKey("items.id"))
    price = Column(Float, index=True)
    insert_date = Column(Date)

    price_id = relationship("Item", back_populates="item_price", uselist=False)





