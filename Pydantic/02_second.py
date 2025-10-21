from fastapi import FastAPI
from pydantic import BaseModel,EmailStr,AnyUrl,Field
from typing import List,Dict,Optional,Annotated

app=FastAPI()

class Patient(BaseModel):
    # name:str=Field(max_length=50)
    name:str=Annotated[str,Field(max_length=50,title="Name of Patient",description="Give Name in less that 50 characters",examples=['Abrar ul Riyaz','Ali Baba'])]
    age:int=Field(ge=0,lt=150)
    linkedin_url:AnyUrl
    email:EmailStr
    weight:Annotated[float,Field(gt=0,lt=1000,strict=True)] #strict supressing type conversion meanns str("55") won't be changed to integer value
    married:Annotated[bool,Field(default=None,description="Is the patient married or not")]
    allergies: Annotated[str,Field(default=None,max_length=5)] #list of strings optional with default value None
    contact_details:Dict[str,str] #both key and value are string

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

patient_info={"name":"John","age":30,"email":"abc@gmail.com","linkedin_url":"http://linkedin.com/3434","weight":83,"contact_details":{"phone":"4444343"}}

#patient_info={"name":"John","age":"30"}

patient1=Patient(**patient_info) # **->dictionary unpacking operator
def insert_patient_data(patient:Patient):
    print(f"Name= {patient.name}")
    print(f"Married={patient.married}")
    print(f"Age= {patient.age}")
    print(f"Weight= {patient.weight}")
    print("Inserted")
    
insert_patient_data(patient1)


