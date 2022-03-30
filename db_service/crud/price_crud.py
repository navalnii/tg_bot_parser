import uuid
from datetime import datetime
from sqlalchemy.orm import Session

from db_service import models
from db_service.schemas import price_schema


def get_price(db: Session, item_id: int, price: float, seller: str):
    return db.query(models.Price).filter((models.Price.item_id == item_id)
                                         & (models.Price.price == price)
                                         & (models.Price.seller == seller)).\
                                    order_by(models.Price.insert_date.desc()).first()


def get_item_prices(db: Session, item_id: int, limit: int):
    return db.query(models.Price).join(models.Item).\
        filter(models.Item.id == item_id).\
        order_by(models.Price.insert_date.desc()).limit(limit).all()


def create_price_if_not_exist(db: Session, price: price_schema.PriceCreate):
    db_price = get_price(db, price.item_id, price.price, price.seller)
    if not db_price:
        db_price = models.Price(**price.dict(), id=str(uuid.uuid4()), insert_date=datetime.now().isoformat())
        db.add(db_price)
    else:
        db_price.insert_date = datetime.now().isoformat()
    db.commit()
    db.refresh(db_price)
    return db_price
