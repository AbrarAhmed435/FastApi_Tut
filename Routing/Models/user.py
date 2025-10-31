from sqlalchemy import Column, Integer, String,DateTime
from sqlalchemy.sql import func
from database.connections import Base


class User(Base):
    __tablename__="users"
    
    id=Column(Integer,primary_key=True,index=True)
    first_name=Column(String(50),nullable=False)
    last_name=Column(String(50),nullable=False)
    email=Column(String(255),nullable=False,index=True,unique=True)
    phone=Column(String(30),nullable=False)
    hashed_password=Column(String(255),nullable=False)
    created_at=Column(DateTime(timezone=True),server_default=func.now(),nullable=False)