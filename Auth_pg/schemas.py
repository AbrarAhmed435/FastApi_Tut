from pydantic import BaseModel, EmailStr,Field,field_validator
from typing import Annotated

class UserCreate(BaseModel):
    first_name:Annotated[str,Field(...,max_length=50)]
    last_name:Annotated[str,Field(...,max_length=50)]
    email:EmailStr
    phone:Annotated[str,Field(...,pattern=r"^\d+$")]
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
    def validate_password(clas,v):
        import re 
        if not re.search(r"[A-Z]",v):
            raise ValueError("Password must contain at least one upper case letter")
        if not re.search(r"[a-z]", v):
            raise ValueError("Password must contain at least one lowercase letter")
        if not re.search(r"\d", v):
            raise ValueError("Password must contain at least one digit")
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", v):
            raise ValueError("Password must contain at least one special character")
        return v
    
    

class LoginIn(BaseModel):
    email:EmailStr
    password:str
    
    
    
    
# ==============================================================
# 📤 3. Schema for User Response (Output)
# ==============================================================    

class UserOut(BaseModel):
    """
    This schema defines how a user object will be returned
    in API responses (for example, after successful signup or login).
    """
    id: int
    first_name: str
    last_name: str
    email: EmailStr
    phone: str
    
    
    # -----------------------------------------------
    # Model configuration (Pydantic v2)
    # -----------------------------------------------
    # Allows this Pydantic model to be created directly
        # from a SQLAlchemy ORM object (not just a dict).
        #
        # Without this, FastAPI would throw a validation error
        # when you try to return ORM models directly.
    model_config={"from_attributes":True}
    
    
    """ 
    When you fetch a user from the database using SQLAlchemy (like db_user = User(...)), you get a SQLAlchemy model instance, not a dictionary.
    print(db_user)
     Output: <User id=1 first_name='ABRAR' email='abrar@email.com'>
     Now, Pydantic models (like UserOut) usually expect dict-like data:
    Pydantic v2 added a feature that lets you load data from class attributes (not just dicts).

You enable that by adding:
model_config = {"from_attributes": True}

    
    """
    
    



