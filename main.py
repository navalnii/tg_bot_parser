from fastapi import Depends, FastAPI, HTTPException, Request, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from db_service.crud import item_crud, subscription_crud, user_crud, price_crud
from db_service.schemas import Item_schema, Price_schema, Subscription_schema, User_schema
from db_service import models
from db_service.database import SessionLocal, engine
import uvicorn

models.Base.metadata.create_all(bind=engine)

app = FastAPI()


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.post("/user/", response_model=User_schema.User)
def create_user(user: User_schema.UserCreate, db: Session = Depends(get_db)) -> object:
    db_user = user_crud.get_user(db, user_id=user.id)
    if db_user:
        raise HTTPException(status_code=400, detail="User already existed")
    return user_crud.create_user(db=db, user=user)


@app.post("/item/", response_model=Item_schema.Item)
def create_item(item: Item_schema.ItemCreate, db: Session = Depends(get_db)):
    db_item = item_crud.get_item(db, item_id=item.id)
    if db_item:
        raise HTTPException(status_code=400, detail="Item already existed")
    return item_crud.create_item(db=db, item=item)


@app.post("/subs/", response_model=Subscription_schema.Subscription)
def create_item_user(item: Item_schema.ItemCreate, user: User_schema.User, db: Session = Depends(get_db)):
    item_db = item_crud.get_item(db, item_id=item.id)
    user_db = user_crud.get_user(db, user_id=user.id)
    if item_db and user_db:
        raise HTTPException(status_code=400, detail="item_user already existed")
    return subscription_crud.create_subscription(db, user_id=user.id, item_id=item.id)


@app.post("/item_price/", response_model=Price_schema.Price)
def create_price(price: Price_schema.PriceCreate, db: Session = Depends(get_db)):
    return price_crud.create_price(db=db, price=price)


# Whitelisted IPs
WHITELISTED_IPS = ['2.75.134.93']

@app.middleware('http')
async def validate_ip(request: Request, call_next):
    # Get client IP
    ip = str(request.client.host)

    # Check if IP is allowed
    if ip not in WHITELISTED_IPS:
        data = {
            'message': f'IP {ip} is not allowed to access this resource.'
        }
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content=data)

    # Proceed if IP is allowed
    return await call_next(request)


if __name__ == '__main__':
    uvicorn.run(app, host="0.0.0.0", port=8080)




