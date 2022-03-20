from sqlalchemy.orm import Session
from db_service.schemas import user_schema
from db_service import models


def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()


def get_users(db: Session, skip: int = 0, limit: int = 1000):
    return db.query(models.User).offset(skip).limit(limit).all()


def get_user_items(db: Session, user_id: int):
    return db.query(models.Item).join(models.Subscription).join(models.User).filter(models.User.id == user_id).all()


def create_user(db: Session, user: user_schema.UserCreate):
    db_user = models.User(**user.dict())
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def update_user(db: Session, user: user_schema.UserCreate):
    db_user = db.query(models.User).filter(models.User.id == user.id).first()
    db_user.is_active = user.is_active
    db_user.discount_perc = user.discount_perc
    db.commit()
    db.refresh(db_user)
    return db_user

