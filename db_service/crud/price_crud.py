import uuid
from datetime import datetime
from sqlalchemy.orm import Session

from db_service import models
from db_service.schemas import Price_schema


def get_price(db: Session, item_id: int):
    return db.query(models.Price).filter(models.Price.item_id == item_id).first()


def create_price(db: Session, price: Price_schema):
    db_price = models.Price(**price.dict(), id=str(uuid.uuid4()), insert_date=datetime.now())
    db.add(db_price)
    db.commit()
    db.refresh(db_price)
    return db_price
