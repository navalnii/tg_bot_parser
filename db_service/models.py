from sqlalchemy import Boolean, Column, ForeignKey, Integer, Float, String, Date, Enum
from sqlalchemy.orm import relationship
from db_service.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    phone = Column(String, unique=True)
    is_active = Column(Boolean, default=True)
    discount_perc = Column(Enum(1, 15, 25), index=True)

    subs = relationship("Subscription", back_populates="owner")


class Subscription(Base):
    __tablename__ = 'subscriptions'

    id = Column(Integer, primary_key=True)
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

    item_id = Column(Integer, ForeignKey("items.id"), primary_key=True)
    price = Column(Float, index=True)
    insert_date = Column(Date)

    price_id = relationship("Item", back_populates="item_price", uselist=False)





