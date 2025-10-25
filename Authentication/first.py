from fastapi import Depends,FastAPI,HTTPException,status
from fastapi.security import OAuth2PasswordBearer,OAuth2PasswordRequestForm
from pydantic import BaseModel
from typing import Optional
from datetime import datetime,timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext


SECRET_KEY="b78a5dfd813131cd71a1b334be13bef874507aae349e850e49b56677122e8f9c" #openssl rand -hex 32
ALGORITHM="HS256"
ACCESS_TOKEN_EXPIRE_MINUTES=30




fake_db={
    "abrar":{
        "username":"abrar",
        "full_name":"Abrar ul Riyaz",
        "email":"abrar@gmail.com",
        "hashed_password":"",
        "disable":False
    }
}


class Token(BaseModel):
    access_token:str
    token_type:str 
    
class TokenData(BaseModel):
    username:Optional[str] =None
    
class User(BaseModel):
    username:str
    email:Optional[str]=None
    full_name:Optional[str]=None
    disable:Optional[bool]= None
    
class UserInDB(User):
    hashed_password:str
    





pwd_context=CryptContext(schemes=['bcrypt'],deprecated='auto')
oauth_2_scheme=OAuth2PasswordBearer(tokenUrl="token")

app=FastAPI()


def verify_password(plain_password,hashed_password):
    return pwd_context.verify(plain_password,hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def get_user(db,username:str):
    if username in db:
        user_data=db[username]
        return UserInDB(**user_data)
    
def authenticate_user(db,username:str,password:str):
    user=get_user(db,username)
    if not user:
        return False
    if not verify_password(password,user.hashed_password):
        return False
    return user

def create_access_token(data:dict,expires_delta:Optional[timedelta]=None):
    to_encode=data.copy()
    if expires_delta:
        expire=datetime.utcnow()+expires_delta
    else:
        expire=datetime.utcnow()+timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp":expire})
    
    encoded_jwt=jwt.encode(to_encode,SECRET_KEY,algorithm=ALGORITHM)
    
    return encoded_jwt


async def get_current_user(token:str=Depends(oauth_2_scheme)):
    credentials_exception=HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Couldn not validate credentials",
        headers={"WWW-Authenticate":"Bearer"},
    )
    
    try:
        payload=jwt.decode(token,SECRET_KEY,algorithms=[ALGORITHM])
        username:str=payload.get("sub")
        if username is None:
            raise credentials_exception
        
    except JWTError:
        raise credentials_exception
    
    user=get_user(fake_db,username)
    if user is None:
        raise credentials_exception
    
    return user 
    

async def get_current_active_user(current_user,UserInDB=Depends(get_current_user)):
    if current_user.disabled:
        raise HTTPException(status_code=400,detail="Inactivate user")
    
    return current_user


# @app.post("/token",response_model=Token)
# async def login_for_access_token(form_data:OAuth2PasswordRequestForm=Depends()):
#     user=authenticate_user(db,form_data.username,form_data.password)
#     if not user:
#         return HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Incorrect username or password",headers={"WWW-Authenticate":"Bearer"})
#     access_token_expires=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
#     access_token=create_access_token(data={"sub":user.username},expires_delta=access_token_expires)
    
#     return {"access_token":access_token,"token_type":"bearer"}

@app.post("/register")
def register_user(username:str,password:str,email:Optional[str]=None,full_name:Optional[str]=None):
    if username in fake_db:
        raise HTTPException(status_code=400,detail="Username already exits")
    hashed_password=get_password_hash(password)
    fake_db[username]={"username":username,"hashed_password": hashed_password, "email": email, "full_name": full_name, "disabled": False}
    return {"msg":"User Registered Successfully"}


@app.post("/token",response_model=Token)
def login(form_data:OAuth2PasswordRequestForm=Depends()):
    user=authenticate_user(fake_db,form_data.username,form_data.password)
    if not user:
        raise HTTPException(status_code=401,detail="Incorrect username or password")
    access_token=create_access_token(data={"sub":user.username})
    return {"access_token":access_token,"token_type":"bearer"}


@app.get("/me")
def read_current_user(current_user:User=Depends(get_current_active_user)):
    return current_user