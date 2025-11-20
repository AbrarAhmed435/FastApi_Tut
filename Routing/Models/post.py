from sqlalchemy import Column, Integer, String,Text,ForeignKey,DateTime,func
from sqlalchemy.orm import relationship
from database.connections import Base

class Post(Base):
    __tablename__="posts"
    
    id=Column(Integer,primary_key=True,index=True)
    title=Column(String(200),nullable=False)
    description=Column(Text,nullable=True)
    image_path=Column(String(255),nullable=True)
    created_at=Column(DateTime(timezone=True),server_default=func.now())
    
    user_id=Column(Integer,ForeignKey("users.id"))
    author=relationship("User",back_populates="posts")
    