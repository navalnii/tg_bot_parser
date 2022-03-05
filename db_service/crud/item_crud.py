from sqlalchemy.orm import Session
from db_service.schemas import Item_schema
from db_service import models


def get_item(db: Session, item_id):
    return db.query(models.Item).filter(models.Item.id == item_id).first()


def create_item(db: Session, item: Item_schema.ItemCreate):
    db_item = models.Item(**item)
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item
