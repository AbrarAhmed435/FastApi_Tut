from fastapi import FastAPI
from pydantic import BaseModel
from typing import List,Dict

app=FastAPI()

class Patient(BaseModel):
    name:str
    age:int
    weight:float
    married:bool
    allergies: List[str] #list of strings
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

patient_info={"name":"John","age":30,"weight":76.2,"married":True,"allergies":['pollen','Dust'],"contact_details":{"email":"example@gmail.com","phone":"4444343"}}

#patient_info={"name":"John","age":"30"}

patient1=Patient(**patient_info) # **->dictionary unpacking operator
def insert_patient_data(patient:Patient):
    print(patient.name)
    print(patient.age)
    print("Inserted")
    
insert_patient_data(patient1)


