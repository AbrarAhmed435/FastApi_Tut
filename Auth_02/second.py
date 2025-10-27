from fastapi import FastAPI,HTTPException,Request,status,Depends
from fastapi.responses import JSONResponse
from pydantic import BaseModel,EmailStr,Field,field_validator
from typing import Annotated,Optional
from passlib.context import CryptContext
import json
from datetime import timedelta,datetime
from jose import JWTError,jwt
from pathlib import Path

import time
from logger_config import logger
import re
import os

from database import users_collection,client #motor collection

from dotenv import load_dotenv


app=FastAPI()

pwd_context=CryptContext(schemes=["bcrypt"],deprecated="auto")
USER_FILE=Path("db.json")
SECRET_KEY=os.getenv("SECRET_KEY") #openssl rand -hex 32
ALGORITHM="HS256"
ACCESS_TOKEN_EXPIRE_MINUTES=30

from fastapi.security import OAuth2PasswordBearer
oauth2_scheme=OAuth2PasswordBearer(tokenUrl="token")

def _truncate_password(pw:str)->str:
    return pw[:72]


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
        
    
    # def hash_password(self):
    #     self.password=pwd_context.hash(self.password)
    

class LoginIn(BaseModel):
    email:EmailStr
    password:str
    
    
def verify_password(plain_password:str,hashed_password:str)->bool:
    return pwd_context.verify(_truncate_password(plain_password),hashed_password)

def create_access_token(data:dict,expires_delta:Optional[timedelta]=None)->str:
    to_encode=data.copy()
    expire=datetime.utcnow()+(expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp":expire})
    token=jwt.encode(to_encode,SECRET_KEY,algorithm=ALGORITHM)
    return token
    
from contextlib import asynccontextmanager    
    
# @app.on_event("startup")
# asynccontextmanager
# async def startup_event():
#     #enuser unique index on email
#     await users_collection.create_index("email",unique=True)
#     #OPTIONAL: checking connection with DB
#     try:
#         await users_collection.database.client.server_info()
#     except Exception as e:
#         print("MongoDB connection error:",e)
        
        
asynccontextmanager
async def lifespan(app:FastAPI):
    
    await users_collection.create_index("email",unique=True)
    
    try:
        await users_collection.database.client.server.info()
    except Exception as e:
        print("MongoDB connection error",e)
        
    yield # this lien pauses here while app is running
    
    client.close()
    print("Mongo connection closed")

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
async def register(user:User):
    user_dict=user.model_dump()
    hashed=pwd_context.hash(_truncate_password(user.password))
    user_dict["password"]=hashed
    user_dict["created_at"]=datetime.utcnow()
    
    try:
        await users_collection.insert_one(user_dict)
    except Exception as e:
        # handle duplicate key error cleanly:
        # pymongo.errors.DuplicateKeyError is available from pymongo, but Motor raises same
        if "duplicate key" in str(e).lower():
            raise HTTPException(status_code=409,detail="Email already registered")
        raise HTTPException(status_code=500,detail="Database Error")
    return JSONResponse(status_code=201,content={
        "message":"User Registration Successfull"
    })
        
    
    
    
    
@app.post('/login')
async def login(login_in:LoginIn):
    user=await users_collection.find_one({"email":login_in.email})
    
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Invalid credentials")
    hashed=user.get("password")
    if not hashed or not verify_password(login_in.password,hashed):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Invalid Credentials")
    access_token=create_access_token({"sub":login_in.email})
    return {
        "Access_token":access_token,
        "token_type":"bearer"
    }
    



async def get_current_user(token:str=Depends(oauth2_scheme)):
    credentials_exception=HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate":"Bearer"},
        

    )
    
    try:
        payload=jwt.decode(token,SECRET_KEY,algorithms=[ALGORITHM])
        email:str=payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    user=get_user_by_email(email)
    if user is None:
        raise credentials_exception
    
    
    safe_user=dict(user)
    safe_user.pop("password",None)
    safe_user.pop("hashed_password",None)
    return safe_user


@app.get("/me")
def me(current_user=Depends(get_current_user)):
    return {
        "user":current_user
    }
    