from fastapi import FastAPI
from pydantic import BaseModel,EmailStr,AnyUrl,Field,field_validator
from typing import List,Dict,Optional,Annotated

app=FastAPI()

class Patient(BaseModel):
    # name:str=Field(max_length=50)
    name:str
    age:int
    email:EmailStr
    weight:float
    married:bool
    allergies: List[str]
    contact_details:Dict[str,str] #both key and value are string
    
    @field_validator('email')
    @classmethod
    def email_validator(cls,value):
        valid_domains=['hdfc.com','icici.com']
        domain_name=value.split('@')[-1]
        if domain_name not in valid_domains:
            raise ValueError("Not a valid domain")
        return value
        
    @field_validator('name')
    @classmethod
    def transform_name(cls,value):
        return value.upper()
    
    @field_validator('age',mode='after') # after send value after type conversion(str to int) and before sends before conversion
    @classmethod
    def age_validator(cls,value): #we will receive int value if it is str
        if 0<value<1000:
            return
        else:
            raise ValueError("Age should between 0 and 100")
        
class Item(BaseModel):
    name:str
    price:float
    is_offer:bool=False

@app.get('/')
def home():
    return {"message":"This is home page"}

@app.post("/item/")
def create_item(item:Item):
    return {"name":item.name,"price":item.price,"is_offer":item.is_offer}


@app.post('/add_patient/')
def AddPatient(patient:Patient):
    return {"name":patient.name,"age":patient.age}

patient_info={"name":"John Doe","age":'100',"email":"abc@hdfc.com","weight":83,"married":True,"allergies":["kidneystone"],"contact_details":{"phone":"4444343"}}

#patient_info={"name":"John","age":"30"}

patient1=Patient(**patient_info) # **->dictionary unpacking operator
def insert_patient_data(patient:Patient):
    print(f"Name= {patient.name}")
    print(f"Married={patient.married}")
    print(f"Age= {patient.age}")
    print(f"Weight= {patient.weight}")
    print("Inserted")
    
insert_patient_data(patient1)


