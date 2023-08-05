from sqlalchemy import Column, String, Integer, Float, ForeignKey
from sqlalchemy.orm import Session
from .database import Base

from pydantic import BaseModel

class Ad(Base):
    __tablename__ = "ads"

    id = Column(Integer, primary_key = True, index = True)
    user_id =  Column(Integer, ForeignKey("users.id"))
    type = Column(String)
    price = Column(Integer)
    address = Column(String, unique = True)
    area = Column(Float)
    rooms_count = Column(Integer)
    description = Column(String)
    total_comments = Column(Integer, default = 0)

class CreateAd(BaseModel):
    type: str
    price: int
    address: str
    area: float
    rooms_count: int
    description: str

class GetAd(BaseModel):
    id: int
    type: str
    price: int
    address: str
    area: float
    rooms_count: int
    description: str
    total_comments: int

class GetAdsList(BaseModel):
    total: int
    objects: list[GetAd]
    
class AdsRepository:
    def get_by_id(self, db: Session, ad_id: int)-> Ad:
        return db.query(Ad).filter(Ad.id == ad_id).first()

    def get_by_address(self, db: Session, address: str)-> Ad:
        return db.query(Ad).filter(Ad.address == address).first()

    def save(self, db: Session, ad: CreateAd, usr_id: int):
        db_ad= Ad(user_id = usr_id, type = ad.type, price = ad.price, address = ad.address, area = ad.area, rooms_count = ad.rooms_count, description = ad.description )

        db.add(db_ad)
        db.commit()
        db.refresh(db_ad)
        return db_ad
    
    def get_list(self, lim: int, skip: int, price_until: int, price_from: int, type: str, rooms_count: int, db: Session) -> GetAdsList:
        db_ads = db.query(Ad)
        if price_from:
            db_ads = db_ads.filter(Ad.price >= price_from)
        if price_until:
            db_ads = db_ads.filter(Ad.price <= price_until)
        if rooms_count:
            db_ads = db_ads.filter(Ad.rooms_count == rooms_count)
        if type:
            db_ads = db_ads.filter(Ad.type == type)
        total = len(db_ads.all())
        return {"total": total, "objects": db_ads.offset(skip).limit(lim).all()}
    
    
    def update(self, db: Session, ad: Ad, new_inform: dict):
        
        db.query(Ad).filter(Ad.id == ad.id).update(new_inform, synchronize_session=False)

        db.commit()
        db.refresh(ad)
        return ad
    
    def delete(self, db: Session, ad: Ad):
        db.query(Ad).filter(Ad.id == ad.id).delete()

        db.commit()
        return True