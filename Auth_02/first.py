from fastapi import FastAPI,HTTPException,Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel,EmailStr,Field,field_validator
from typing import Annotated
from passlib.context import CryptContext
import json
from pathlib import Path
import time
from logger_config import logger
import re

app=FastAPI()

@app.middleware('http')
async def log_request(request:Request,call_next):
    start_time=time.time()
    client_ip=request.client.host
    method=request.method
    url=request.url.path
    
    logger.info(f"Request :{method} {url} form {client_ip}")
    
    response=await call_next(request)
    
    duration=time.time()-start_time
    logger.info(f"Response: {method} {url} completed in {duration:.3f}")
    
    return response


pwd_context=CryptContext(schemes=["bcrypt"],deprecated="auto")
USER_FILE=Path("db.json")

class User(BaseModel):
    first_name:Annotated[str,Field(...,max_length=50,title="First Name")]
    last_name:Annotated[str,Field(...,max_length=50,title="First Name")]
    email:EmailStr
    phone:Annotated[str,Field(...,pattern=r"^\d+$")]
    password:Annotated[str,Field(...,min_length=8,title="Password (min 8)")]
    
    @field_validator('first_name')
    @classmethod
    def validate_first_name(cls,value):
        return value.upper()
    
    @field_validator('last_name')
    @classmethod
    def validate_last_name(cls,value):
        return value.upper()
    
    
    
    @field_validator('password')
    @classmethod
    def validate_password(cls,value):
        if not re.search(r"[A-Z]", value):
            raise ValueError("Password must contain at least one uppercase letter")
        if not re.search(r"[a-z]", value):
            raise ValueError("Password must contain at least one lowercase letter")
        if not re.search(r"\d", value):
            raise ValueError("Password must contain at least one digit")
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", value):
            raise ValueError("Password must contain at least one special character")
        return value
        
    
    def hash_passowrd(self):
        self.password=pwd_context.hash(self.password)
    
    
    
def load_users():
    if not USER_FILE.exists():
        return []
    with open(USER_FILE,'r') as f:
        return json.load(f)    
    
def get_user_by_email(email:str):
    users=load_users()
    
    for user in users:
        if user["email"]==email:
            return user
    return None
    
    
def save_users(users_list):
    with open(USER_FILE,'w') as f:
        json.dump(users_list,f,indent=4)

@app.post('/register')
def register(user:User):
    if get_user_by_email(user.email):
        raise HTTPException(status_code=409,detail="Email already registered")
    
    # hashed_password=pwd_context.hash(user.password)
    user.hash_passowrd()
    user_dict=user.dict()
    
    users=load_users()
    users.append(user_dict)
    save_users(users)
    
    return JSONResponse(status_code=201,content={
        "message":"User Registration Successful",
        "email":user.email
    })