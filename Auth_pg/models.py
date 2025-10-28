from sqlalchemy import column, Integer, String,DateTime
from sqlalchemy.sql import func
from db import Base

class User(Base):
    __tablename__="users"