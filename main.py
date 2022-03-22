from fastapi import Depends, FastAPI, HTTPException, Request, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from db_service.crud import item_crud, subscription_crud, user_crud, price_crud
from db_service.schemas import item_schema, price_schema, subscription_schema, user_schema
from db_service import models
from db_service.database import SessionLocal, engine
import logger
import uvicorn

models.Base.metadata.create_all(bind=engine)

app = FastAPI(debug=True)
logger = logger.logger_init('fastapi')


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/users", response_model=user_schema.UsersList)
def get_users(db: Session = Depends(get_db)) -> object:
    return {'results': list(user_crud.get_users(db))}


@app.post("/user/", response_model=user_schema.User)
def create_user(user: user_schema.UserCreate, db: Session = Depends(get_db)) -> object:
    db_user = user_crud.get_user(db, user_id=user.id)
    if db_user:
        return user_crud.update_user(db=db, user=user)
        # raise HTTPException(status_code=400, detail="User already existed")
    return user_crud.create_user(db=db, user=user)


@app.get("/items_user/", response_model=user_schema.UserGetItems)
def get_items_user(user_id: int, db: Session = Depends(get_db)) -> object:
    res = user_crud.get_user_items(db, user_id)
    return {'results': list(res)}


@app.get("/urls/", response_model=user_schema.UserGetItems)
def get_urls(db: Session = Depends(get_db)) -> object:
    res = item_crud.get_items(db)
    return {'results': list(res)}


# @app.post("/item/", response_model=item_schema.Item)
# def create_item(item: item_schema.ItemCreate, db: Session = Depends(get_db)):
#     db_item = item_crud.get_item(db, item_id=item.id)
#     if db_item:
#         raise HTTPException(status_code=400, detail="Item already existed")
#     return item_crud.create_item(db=db, item=item)


@app.post("/subs/", response_model=subscription_schema.Subscription)
def create_subs(item: item_schema.ItemCreate, user_id: int, db: Session = Depends(get_db)):
    item_db = item_crud.get_item(db, item_id=item.id)
    user_db = user_crud.get_user(db, user_id=user_id)
    if item_db and user_db:
        subs_db = subscription_crud.get_subs(db, item_id=item.id, user_id=user_id)
        if subs_db:
            raise HTTPException(status_code=406, detail="Item-User already existed")
        else:
            return subscription_crud.create_subscription(db, user_id=user_id, item_id=item.id)
    elif not item_db and user_db:
        created_item = item_crud.create_item(db=db, item=item)
        return subscription_crud.create_subscription(db, user_id=user_id, item_id=created_item.id)
    raise HTTPException(status_code=400, detail="User not existed, while subs was created")


@app.post("/item_price/", response_model=price_schema.Price)
def create_price(price: price_schema.PriceCreate, db: Session = Depends(get_db)):
    return price_crud.create_price(db=db, price=price)


@app.get("/get_item_price/")
def get_item_price(user_id: int, db: Session = Depends(get_db)):
    results = []
    user_info = user_crud.get_user(db, user_id)
    items_list = user_crud.get_user_items(db, user_id)
    for item in items_list:
        # 2 - limit sql for calculate discount between prev and curr prices
        prices = price_crud.get_item_prices(db, item.id, 2)
        if prices:
            diff_percent = (prices[1].price - prices[0].price) / prices[0].price
            if user_info.discount_perc == 'under_15' and 0 < diff_percent < 0.15:
                results.append({'item': item, 'price': prices})
            elif user_info.discount_perc == 'from_15_to_25' and 0.15 < diff_percent < 0.25:
                results.append({'item': item, 'price': prices})
            elif user_info.discount_perc == 'upper_25' and 0.25 < diff_percent:
                results.append({'item': item, 'price': prices})
    return results


# Whitelisted IPs
WHITELISTED_IPS = ['2.75', '127.0', '45.129']


@app.middleware('http')
async def validate_ip(request: Request, call_next):
    ip = '.'.join(str(request.client.host).split('.')[:2])
    if ip not in WHITELISTED_IPS:
        data = {
            'message': f'IP {ip} is not allowed to access this resource.'
        }
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content=data)
    # Proceed if IP is allowed
    return await call_next(request)


if __name__ == '__main__':
    uvicorn.run(app, host="0.0.0.0", port=8080)




