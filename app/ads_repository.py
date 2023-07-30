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
    
    def update(self, db: Session, ad: Ad, new_inform: dict):
        
        db.query(Ad).filter(Ad.id == ad.id).update(new_inform, synchronize_session=False)

        db.commit()
        db.refresh(ad)
        return ad
    
    def delete(self, db: Session, ad: Ad):
        db.query(Ad).filter(Ad.id == ad.id).delete()

        db.commit()
        return True