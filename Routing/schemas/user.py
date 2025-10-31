from pydantic import BaseModel, EmailStr,Field,field_validator
from typing import Annotated

class UserCreate(BaseModel):
    first_name:Annotated[str,Field(...,max_length=50)]
    last_name:Annotated[str,Field(...,max_length=50)]
    email:EmailStr
    phone:Annotated[str,Field(...,pattern=r"^\d+$",min_length=10)]
    password:Annotated[str,Field(...,min_length=8)]
    
    @field_validator("first_name")
    @classmethod
    def u_first(cls,v):
        return v.upper()
    
    @field_validator("last_name")
    @classmethod
    def u_last(cls,v):
        return v.upper()
        
    @field_validator("password")
    @classmethod
    def validate_password(cls,v):
        import re
        if not re.search(r"[A-Z]",v):
            raise ValueError("Password must contain atleat one uppercase letter")
        if not re.search(r"[a-z]",v):
            raise ValueError("Password must contain atleat one lowercase letter")
        if not re.search(r"\d",v):
            raise ValueError("Password must contain atleast one digit")
        if not re.search(r"[!@#$%&^*(),.?\":{}|<>]",v):
            raise ValueError("Password must contain at least on special character")
        return v
    
class LoginIn(BaseModel):
    email:EmailStr
    password:str
    
    
class UserOut(BaseModel):
    id:int
    first_name:str
    last_name:str 
    email:EmailStr
    phone:str
    
    model_config={"from_attributes":True}