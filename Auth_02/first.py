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

app=FastAPI()

pwd_context=CryptContext(schemes=["bcrypt"],deprecated="auto")
USER_FILE=Path("db.json")
SECRET_KEY="e3406c4cc5747a186ab73592cdef8df8c9eaa32278635c80a3cbc3fe459b8b63" #openssl rand -hex 32
ALGORITHM="HS256"
ACCESS_TOKEN_EXPIRE_MINUTES=30

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
    hashed=pwd_context.hash(_truncate_password(user.password))
    # user.hash_password()
    user_dict=user.dict()
    user_dict['password']=hashed
    
    users=load_users()
    users.append(user_dict)
    save_users(users)
    
    return JSONResponse(status_code=201,content={
        "message":"User Registration Successful",
        "email":user.email
    })
    
    
    
@app.post('/login')
def login(login_in:LoginIn):
    user=get_user_by_email(login_in.email)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Invalid credentials")
    
    hashed=user.get("password") or user.get("hashed_password")
    if not hashed:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail="user record malformed")
    
    if not verify_password(login_in.password,hashed):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    
    
    access_token=create_access_token({"sub":login_in.email})
    return JSONResponse(status_code=200,content={
        "access_token":access_token, 
        "token_type":"bearer"
    })
    

from fastapi.security import OAuth2PasswordBearer
oauth2_scheme=OAuth2PasswordBearer(tokenUrl="token")

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
    