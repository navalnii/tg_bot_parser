import uuid
from datetime import datetime
from sqlalchemy.orm import Session

from db_service import models
from db_service.schemas import price_schema


def get_item_prices(db: Session, item_id: int, limit: int):
    return db.query(models.Price).join(models.Item).\
        filter(models.Item.id == item_id).\
        order_by(models.Price.insert_date.desc()).limit(limit).all()


def create_price(db: Session, price: price_schema.PriceCreate):
    db_price = models.Price(**price.dict(), id=str(uuid.uuid4()), insert_date=datetime.now().isoformat())
    db.add(db_price)
    db.commit()
    db.refresh(db_price)
    return db_price
