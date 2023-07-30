from sqlalchemy import Column, String, Integer, Float, ForeignKey
from sqlalchemy.orm import Session
from .database import Base
from datetime import datetime

from pydantic import BaseModel

class Comment(Base):
    __tablename__ = "comments"

    id = Column(Integer, primary_key = True, index = True)
    author_id = Column(Integer, ForeignKey("users.id"))
    ad_id = Column(Integer, ForeignKey("ads.id"))
    content = Column(String)
    created_at = Column(String)

class CreateComment(BaseModel):
    content: str

class GetComment(BaseModel):
    id: int
    content: str
    created_at: str
    author_id: int

class CommentsRepository:
    def get_by_id(self, db: Session, comment_id: int)-> Comment:
        return db.query(Comment).filter(Comment.id == comment_id).first()
    
    def get_all(self, ad_id: int, db: Session, skip: int = 0, limit: int = 10)-> list[GetComment]:
        return db.query(Comment).limit(Comment.ad_id == ad_id).offset(skip).limit(limit).all()

    def save(self, db: Session, comment: CreateComment, author_id: int, ad_id: int):
        date = str(datetime.now())[0:19]
        db_comment = Comment(author_id = author_id, ad_id = ad_id, content = comment.content, created_at = date )

        db.add(db_comment)
        db.commit()
        db.refresh(db_comment)
        return db_comment
    
    def update(self, db: Session, comment: Comment, new_inform: dict):
        
        db.query(Comment).filter(Comment.id == comment.id).update(new_inform, synchronize_session=False)

        db.commit()
        db.refresh(comment)
        return comment
    
    def delete(self, db: Session, comment: Comment):
        db.query(Comment).filter(Comment.id == comment.id).delete()

        db.commit()
        return True