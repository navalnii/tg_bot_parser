import uuid
from sqlalchemy.orm import Session
from db_service import models


def get_subs(db: Session, user_id: int, item_id: int):
    return db.query(models.Subscription).filter((models.Subscription.user_id == user_id) &
                                                (models.Subscription.item_id == item_id)).first()


# def get_all_user_subs(db: Session, user_id: int):
#     return [i.item_id for i in db.query(models.Subscription.item_id).filter(models.Subscription.user_id == user_id).all()]


def create_subscription(db: Session, user_id: int, item_id: int):
    db_subs = models.Subscription(id=uuid.uuid4(), item_id=item_id, user_id=user_id)
    db.add(db_subs)
    db.commit()
    db.refresh(db_subs)
    return db_subs

