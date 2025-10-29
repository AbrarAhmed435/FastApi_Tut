import os
import re
from datetime import datetime, timedelta
from dotenv import load_dotenv

from fastapi import FastAPI,Depends,HTTPException,status
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordBearer
from contextlib import asynccontextmanager

from passlib.context import CryptContext
from jose import jwt,JWTError
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from db import engine,get_async_session
from models import Base, User
from schemas import UserCreate,LoginIn,UserOut

load_dotenv()

SECRET_KEY=os.getenv("SECRET_KEY")
ALGORITHM="HS256"
ACCESS_TOKEN_EXPIRE_MINUTES=int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES","30"))

pwd_context=CryptContext(schemes=["bcrypt"],deprecated="auto")

oauth2_scheme=OAuth2PasswordBearer(tokenUrl="token")
""" 
It’s a FastAPI dependency class that tells your app:

“I expect the client to send a Bearer Token in the Authorization header of the HTTP request.”
e.g.,  Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

"""

app=FastAPI()


def _truncate_password(pw:str)->str:
    return pw[:72]
"""  This is because the bcrypt algorithm  only processes the first 72 bytes of a password — anything longer is ignored by the algorithm. 
That means:
->If two passwords are identical in the first 72 characters but differ after that, bcrypt treats them as the same password.
"""

def verify_password(plain_password:str,hashed_password:str)->bool:
    return pwd_context.verify(_truncate_password(plain_password),hashed_password)

def create_access_token(data:dict,expires_delta:timedelta|None=None)->str:
    to_encode=data.copy()
    expire=datetime.utcnow()+(expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    token=jwt.encode(to_encode,SECRET_KEY,algorithm=ALGORITHM)
    return token

@asynccontextmanager
async def lifespan(app:FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    await engine.dispose()

app=FastAPI(lifespan=lifespan)

""" session=Depends(get_async_session):
Injects an asynchronous SQLAlchemy session (database connection) using FastAPI’s dependency injection system.
→ This is how FastAPI gives you a ready-to-use database session per request. """
@app.post("/register",response_model=UserOut,status_code=201)

# ------------------------------------------------------------
# The function is declared `async` because:
#   1. Database operations are asynchronous (using async SQLAlchemy)
#   2. It allows FastAPI to handle multiple requests efficiently
# ------------------------------------------------------------
async def register(user_in: UserCreate, session=Depends(get_async_session)):
    """
    Registers a new user:
      - Hashes the password
      - Validates data (Pydantic already does this)
      - Inserts user into PostgreSQL via SQLAlchemy
      - Handles unique constraint errors (like duplicate email)
    """

    # --------------------------------------------------------
    # Step 1️⃣ : Hash the plain password securely using bcrypt
    # --------------------------------------------------------
    # The `_truncate_password()` ensures password length ≤ 72 bytes
    # (bcrypt only supports passwords up to 72 bytes)
    # The CryptContext automatically salts and hashes it.
    hashed = pwd_context.hash(_truncate_password(user_in.password))

    # --------------------------------------------------------
    # Step 2️⃣ : Create a new `User` ORM instance
    # --------------------------------------------------------
    # This object represents a single row in the `users` table.
    user = User(                        #User is database user in models.py
        first_name=user_in.first_name,
        last_name=user_in.last_name,
        email=user_in.email,
        phone=user_in.phone,
        hashed_password=hashed,
    )

    # --------------------------------------------------------
    # Step 3️⃣ : Add the new user object to the database session
    # --------------------------------------------------------
    # This *stages* the user for insertion — it does NOT yet
    # write anything to the database.
    session.add(user)

    # --------------------------------------------------------
    # Step 4️⃣ : Commit and handle possible database errors
    # --------------------------------------------------------
    try:
        # Commit actually sends the INSERT query to PostgreSQL
        await session.commit()

        # Refresh reloads the object with latest DB values
        # (e.g., autoincremented ID, timestamps, etc.)
        await session.refresh(user)

    # --------------------------------------------------------
    # Step 5️⃣ : Rollback if commit fails (e.g., duplicate email)
    # --------------------------------------------------------
    except IntegrityError as e:
        # Undo the transaction so no partial data remains
        await session.rollback()

        # Return an HTTP 409 Conflict response to the API user
        raise HTTPException(
            status_code=409,
            detail="Email already registered"
        )

    # --------------------------------------------------------
    # Step 6️⃣ : Return the successfully created user
    # --------------------------------------------------------
    # FastAPI will automatically serialize this to JSON.
    return user


@app.post("/login")
async def login(login_in:LoginIn,session=Depends(get_async_session)):
    q=select(User).where(User.email==login_in.email)
    result=await session.execute(q)
    user=result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Invalid Credentials")
    if not verify_password(login_in.password,user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Invalid Credentials")
    access_token=create_access_token({"sub":user.email})
    return {
        "access_token":access_token,
        "token_type":"bearer"
    }
