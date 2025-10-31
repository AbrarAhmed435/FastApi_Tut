import os
import re
from datetime import datetime,timedelta
from dotenv import load_dotenv


from fastapi import APIRouter,Depends,HTTPException,status
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordBearer
from contextlib import asynccontextmanager

from passlib.context import CryptContext
from jose import jwt,JWTError
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from database.connections import engine,get_async_session
from Models.user import User
from schemas.user import UserCreate,LoginIn,UserOut

router=APIRouter(prefix="/auth",tags=["Auth"])

load_dotenv()

SECRET_KEY=os.getenv('SECRET_KEY')
ALGORITHM="HS256"
ACCESS_TOKEN_EXPIRE_MINUTES=int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES","30"))

pwd_context=CryptContext(schemes=['bcrypt'],deprecated="auto")
oauth2_scheme=OAuth2PasswordBearer(tokenUrl="token")




def _truncate_password(pw:str)->str:
    return pw[:72]


def verify_password(plain_password:str,hashed_password:str)->bool:
    return pwd_context.verify(_truncate_password(plain_password),hashed_password)


def create_access_token(data:dict,expire_delta:timedelta|None=None)->str:
    to_encode=data.copy()
    expire=datetime.utcnow()+(expire_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp":expire})
    token=jwt.encode(to_encode,SECRET_KEY,algorithm=ALGORITHM)
    return token 


@router.post('/register',response_model=UserOut,status_code=status.HTTP_201_CREATED)
async def register(user_in:UserCreate,session=Depends(get_async_session)):
    hashed=pwd_context.hash(_truncate_password(user_in.password))
    
    user=User(
        first_name=user_in.first_name,
        last_name=user_in.last_name,
        email=user_in.email,
        phone=user_in.phone,
        hashed_password=hashed
    )
    
    
    session.add(user)
    
    try:
        await session.commit()
        await session.refresh(user)
    except IntegrityError as e:
        await session.rollback()
        # print(str(e))
        raise HTTPException(
            status_code=409,
            detail="Email Already Exists"
        )
        # user.pop("hashed_password")
    return user



@router.post('/login')
async def login(login_in:LoginIn,session=Depends(get_async_session)):
    q=select(User).where(User.email==login_in.email)
    result=await session.execute(q)
    user=result.scalar_one_or_none()
    
    if not user or not verify_password(login_in.password,user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Invalid Credentials")
    # if not verify_password(login_in.password,user.hashed_password):
    #     raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,)
    
    access_token=create_access_token({
        "sub":user.email
    })
    
    refresh_token=create_access_token({
        "sub":user.email, "type":"refresh"
    },expire_delta=timedelta(days=7))
    
    return {
        "access_token":access_token,
        "refresh_token":refresh_token,
        "token_type":"bearer"
    }
    
    
@router.post("/refresh")
async def refresh_token(token:str=Depends(oauth2_scheme)):
    try:
        payload=jwt.decode(token,SECRET_KEY,algorithms=[ALGORITHM])
        if payload.get("type")!="refresh":
            raise HTTPException(status_code=401,detail="Invalid token")
        
        new_access_token=create_access_token({"sub":payload.get("sub")},expire_delta=timedelta(minutes=30))
        
        return {
            "access_token":new_access_token,
            "token_type":"bearer"
        }
    except JWTError:
        raise HTTPException(status_code=402,detail="Invlid or expired token")

# @router.post("/login")
# def login():
#     return {
#         "msg":"User Logged in"
#     }

# @router.post("/register")
# def register():
#     return {
#         "msg":"User register"
#     }
