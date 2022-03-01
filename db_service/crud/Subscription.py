from sqlalchemy.orm import Session

from db_service import models


def create_subscription(db: Session, user_id: int, item_id: int):
    db_subs = models.Subscription(item_id=item_id, user_id=user_id)
    db.add(db_subs)
    db.commit()
    db.refresh(db_subs)
    return db_subs

