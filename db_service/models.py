from sqlalchemy import Boolean, Column, ForeignKey, Integer, Float, String, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from db_service.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, index=True)
    is_active = Column(Boolean, default=True)
    discount_perc = Column(String, index=True)

    subs = relationship("Subscription", back_populates="owner")


class Subscription(Base):
    __tablename__ = 'subscriptions'

    id = Column(UUID(as_uuid=True), primary_key=True)
    item_id = Column(Integer, ForeignKey("items.id"))
    user_id = Column(Integer, ForeignKey("users.id"))

    owner = relationship("User", back_populates="subs")
    owner_ = relationship("Item", back_populates="item")


class Item(Base):
    __tablename__ = 'items'

    id = Column(Integer, primary_key=True)
    title = Column(String, index=True)
    description = Column(String)
    source = Column(String, index=True)
    cato_id = Column(String, index=True)
    url = Column(String, index=True)
    insert_date = Column(DateTime)

    item = relationship("Subscription", back_populates="owner_")
    item_price = relationship("Price", back_populates="price_id")


class Price(Base):
    __tablename__ = "prices"

    id = Column(String, primary_key=True)
    item_id = Column(Integer, ForeignKey("items.id"))
    seller = Column(String, primary_key=True)
    price = Column(Float, index=True)
    insert_date = Column(DateTime)

    price_id = relationship("Item", back_populates="item_price", uselist=False)





