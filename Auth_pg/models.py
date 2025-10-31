from sqlalchemy import Column, Integer, String,DateTime,ForeignKey,Text
from sqlalchemy.sql import func

from sqlalchemy.orm import relationship

from db import Base

class User(Base):
    __tablename__="users"
    
    id=Column(Integer,primary_key=True,index=True)
    first_name=Column(String(50),nullable=False)
    last_name=Column(String(50),nullable=False)
    email=Column(String(255),unique=True,index=True,nullable=False)
    phone=Column(String(30),nullable=False)
    hashed_password=Column(String(255),nullable=False)
    created_at=Column(DateTime(timezone=True),server_default=func.now(),nullable=False)
    
    posts=relationship("Post",back_populates="user",cascade="all, delete")
    
    



class Post(Base):
    __tablename__="posts"
    
    id=Column(Integer,primary_key=True,index=True)
    title=Column(String(255),nullable=True)
    description=Column(Text,nullable=True)
    image_url=Column(String(255),nullable=True)
    
    created_at=Column(DateTime(timezone=True),server_default=func.now(),nullable=True)
    
    user_id=Column(Integer,ForeignKey("user.id",ondelete="CASCADE"),nullable=False)
    
    user=relationship("User",back_populates="posts")
    
     
    # back_populates    Each user has a list of all their posts, and each post has a user attribute linking back to this user.

    """ 
    # Fetch a user
user = await session.get(User, 1)

  Access all posts made by this user
print(user.posts)  
# 👉 [<Post title='First Post'>, <Post title='Another Post'>]

# Fetch a post
post = await session.get(Post, 5)

# Access the user who created it
print(post.user.first_name)
# 👉 "ABRAR"

    """

    
    
    
    