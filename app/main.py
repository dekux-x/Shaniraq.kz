import json

from fastapi import Cookie, FastAPI, Form, Response, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from jose import jwt

from .database import Base, SessionLocal, engine
from .users_repository import User, CreateUser, UserRepository, GetUser
from .ads_repository import CreateAd, GetAd, Ad, AdsRepository
from .comments_repository import CreateComment, GetComment, CommentsRepository



app = FastAPI()
oauth2_cheme = OAuth2PasswordBearer(tokenUrl="auth/users/login")

users_repository = UserRepository()
ads_repository = AdsRepository()
comments_repository = CommentsRepository()

Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def encode_jwt(user_id: int):
    body = {"user_id": user_id}
    token = jwt.encode(body, "saidshabekov")
    return token

def decode_jwt(token: str):
    body = jwt.decode(token, "saidshabekov")
    return body["user_id"]

@app.post("/auth/users/")
def post_signup(user: CreateUser, db: Session = Depends(get_db)):
    db_user = users_repository.get_by_username(db, user.username)
    if db_user:
        raise HTTPException(status_code = 400, detail = "There is already exist such User")
    users_repository.save(db, user)
    return Response(status_code = 200)

@app.post("/auth/users/login")
def post_login(username: str = Form(), password: str = Form(), db: Session = Depends(get_db)):
    user = users_repository.get_by_username(db, username)
    if not user is None and user.password == password:
        token = encode_jwt(user.id)
        return {"access_token": token}
    raise HTTPException(status_code = 400, detail = "There is no such User")

@app.patch("/auth/users/me")
def update_profile(new_inform: dict, token: str = Depends(oauth2_cheme), db: Session = Depends(get_db)):
    if "id" in new_inform:
        return HTTPException(status_code = 400, detail = "You can't update user_id")
    user_id = decode_jwt(token)
    user = users_repository.get_by_id(db,user_id)
    if user:
        update = users_repository.update(db, user, new_inform)
        if update:
            return Response(status_code = 200)
    return Response(status_code = 400)

@app.get("/auth/users/me", response_model = GetUser)
def get_profile(token: str = Depends(oauth2_cheme),db: Session = Depends(get_db)):
    user_id = decode_jwt(token)
    user = users_repository.get_by_id(db, user_id)
    if user:
        return user
    raise HTTPException(status_code = 400, detail = "There is no such user")

@app.post("/shanyraks/")
def post_ad(ad: CreateAd, token: str = Depends(oauth2_cheme), db: Session = Depends(get_db)):
    usr_id = decode_jwt(token)
    ad_exist = ads_repository.get_by_address(db, ad.address)
    if ad_exist:
        raise HTTPException(status_code = 400, detail = "There is already exist Ad with this address")
    ads_repository.save(db, ad, usr_id)
    id = ads_repository.get_by_address(db, ad.address).id
    return {"id": id}

@app.get("/shanyraks/{id}", response_model = GetAd)
def get_ad(id: int, db: Session = Depends(get_db)):
    ad = ads_repository.get_by_id(db, id)
    if ad:
        return {"id": ad.id, "type": ad.type, "price": ad.price, "address": ad.address, "area": ad.area, 
                "rooms_count": ad.rooms_count, "description": ad.description, "total_comments": len(comments_repository.get_all(id, db))}
    raise HTTPException(status_code = 400, detail = "There is no Ad with such ID")

@app.patch("/shanyraks/{id}")
def update_ad(id: int, new_inform: dict, db: Session = Depends(get_db), token: str = Depends(oauth2_cheme)):
    if "id" in new_inform or "user_id" in new_inform:
        raise HTTPException(status_code = 400, detail = "You can't change id or user_id")
    usr_id = decode_jwt(token)
    ad = ads_repository.get_by_id(db, id)
    if not ad:
        raise HTTPException(status_code = 400, detail = "There is no such Ad")
    if usr_id != ad.user_id:
        raise HTTPException(status_code = 403)
    update = ads_repository.update(db, ad, new_inform)
    if update:
        return Response(status_code = 200)
    return Response(status_code = 500)

@app.delete("/shanyraks/{id}")
def delete_ad(id: int, token: str = Depends(oauth2_cheme), db: Session = Depends(get_db)):
    usr_id = decode_jwt(token)
    ad = ads_repository.get_by_id(db, id)
    if not ad:
        raise HTTPException(status_code = 400)
    if ad.user_id != usr_id:
        raise HTTPException(status_code = 403)
    ads_repository.delete(db, ad)
    return Response(status_code = 200)
    
@app.post("/shanyraks/{id}/comments")
def post_comment(id: int, comment: CreateComment, token: str = Depends(oauth2_cheme), db: Session = Depends(get_db)):
    user_id = decode_jwt(token)
    comments_repository.save(db, comment, user_id, id)
    return Response(status_code = 200)

@app.get("/shanyraks/{id}/comments")
def get_comments(id: int, db: Session = Depends(get_db)):
    ad = ads_repository.get_by_id(db, id)
    if not ad:
        raise HTTPException(status_code = 400, detail = "There is no such Ad")
    comments = comments_repository.get_all(id,db)
    return {"comments": comments}

@app.patch("/shanyraks/{id}/comments/{comment_id}")
def update_comment(id: int, comment_id: int, comment: CreateComment, token: str = Depends(oauth2_cheme), db: Session = Depends(get_db)):
    ad = ads_repository.get_by_id(db, id)
    if not ad:
        raise HTTPException(status_code = 400, detail = "There is no such Ad")
    user_id = decode_jwt(token)
    old_comment = comments_repository.get_by_id(db,comment_id)
    if not old_comment:
        raise HTTPException(status_code = 400, detail = "There is no such Comment")
    if user_id != old_comment.author_id:
        raise HTTPException(status_code = 403)
    comments_repository.update(db, old_comment, dict(comment))
    return Response(status_code = 200)

@app.delete("/shanyraks/{id}/comments/{comment_id}")
def delete_comment(id: int, comment_id: int, token: str = Depends(oauth2_cheme), db: Session = Depends(get_db)):
    ad = ads_repository.get_by_id(db, id)
    if not ad:
        raise HTTPException(status_code = 400, detail = "There is no such Ad")
    user_id = decode_jwt(token)
    comment = comments_repository.get_by_id(db,comment_id)
    if not comment:
        raise HTTPException(status_code = 400, detail = "There is no such Comment")
    if user_id != comment.author_id:
        raise HTTPException(status_code = 403)
    comments_repository.delete(db, comment)
    return Response(status_code = 200)
    

    
