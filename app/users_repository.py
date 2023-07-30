from sqlalchemy import Column, String, Integer
from sqlalchemy.orm import Session
from .database import Base

from pydantic import BaseModel,Field

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, index = True, primary_key = True)
    name = Column(String)
    password = Column(String, unique = True)
    username = Column(String, unique = True)
    phone = Column(String, unique = True)
    city = Column(String)

class CreateUser(BaseModel):
    name: str
    username: str = Field(pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b')
    phone: str
    city: str
    password: str

class GetUser(BaseModel):
    id: int
    name: str
    username: str
    phone: str
    city: str

class UserRepository:
    def get_by_id(self, db: Session, user_id: int)-> User:
        return db.query(User).filter(User.id == user_id).first()

    def get_by_username(self, db: Session, username: str)->User:
        return db.query(User).filter(User.username == username).first()

    def get_by_phone(self, db: Session, phone: str)-> User:
        return db.query(User).filter(User.phone == phone).first()

    def get_all(self, db: Session, skip: int = 0, limit: int = 100)-> list[User]:
        return db.query(User).offset(skip).limit(limit).all()

    def get_by_name(self, db: Session, name: str)-> User:
        return db.query(User).filter(User.name == name).first()

    def save(self, db: Session, user: CreateUser):
        db_user = User(username = user.username, name = user.name, password = user.password, phone = user.phone, city = user.city )

        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user
    
    def update(self, db: Session, user: User, new_inform: dict):
        
        db.query(User).filter(User.id == user.id).update(new_inform, synchronize_session=False)

        db.commit()
        db.refresh(user)
        return user
        