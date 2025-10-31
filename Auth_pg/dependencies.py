from fastapi import Depends, HTTPException, status
from jose import jwt, JWTError
from sqlalchemy.future import select
from db import get_async_session
from models import User
import os
from dotenv import load_dotenv
from fastapi.security import OAuth2PasswordBearer

SECRET_KEY=os.getenv("SECRET_KEY")
ALGORITHM="HS256"
ACCESS_TOKEN_EXPIRE_MINUTES=int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES","30"))
oauth2_scheme=OAuth2PasswordBearer(tokenUrl="token")


async def get_current_user(token:str=Depends(oauth2_scheme),session=Depends(get_async_session)):
    credentials_exception=HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Couldn not validate credentials",
        headers={"WWW-Authenticate":'Bearer'},
    )
    try:
        payload=jwt.decode(token,SECRET_KEY,algorithms=[ALGORITHM])
        email:str=payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    q=select(User).where(User.email==email)
    result=await session.execute(q)
    user=result.scalar_one_or_none()
    if not user:
        raise credentials_exception
    
    return user