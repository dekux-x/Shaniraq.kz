from sqlalchemy import Column, String, Integer, ForeignKey, and_
from sqlalchemy.orm import Session
from .database import Base
from .ads_repository import Ad

from pydantic import BaseModel

class FavoriteAd(Base):
    __tablename__= "favorite_ads"

    row_id = Column(Integer, primary_key = True, index = True)
    id = Column(Integer, ForeignKey("ads.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    address = Column(String)

class GetFavoriteAd(BaseModel):
    id: int
    address: str

class GetListFavAds(BaseModel):
    shanyraks: list[GetFavoriteAd]

class FavoriteAdsRepository:
    def get_unique(self, db: Session, ad_id: int, user_id: int)-> FavoriteAd:
        return db.query(FavoriteAd).filter(and_(FavoriteAd.id == ad_id, FavoriteAd.user_id == user_id)).first()
    
    def number_of_likes(self, db: Session, address: str) -> FavoriteAd:
        return len(db.query(FavoriteAd).filter(FavoriteAd.address == address).all())
    
    def get_liked(self, db: Session, user_id: int)-> list[GetFavoriteAd]:
        return db.query(FavoriteAd).filter(FavoriteAd.user_id == user_id).all()
    
    def save(self, db: Session, ad: Ad, user_id: int):
        db_fav_ad = FavoriteAd(id = ad.id, user_id = user_id, address = ad.address)

        db.add(db_fav_ad)
        db.commit()
        db.refresh(db_fav_ad)
        return db_fav_ad
    
    def delete(self, db: Session, ad: FavoriteAd):
        db.query(FavoriteAd).filter(and_(FavoriteAd.id == ad.id, FavoriteAd.user_id == ad.user_id)).delete()

        db.commit()
        return True
    