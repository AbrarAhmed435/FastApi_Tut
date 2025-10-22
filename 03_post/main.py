from fastapi import FastAPI,Path,HTTPException,Query
from fastapi.responses import JSONResponse
import json
from pydantic import BaseModel,Field,computed_field
from typing import Annotated,Literal


app=FastAPI()

class Patient(BaseModel):
    
    name:Annotated[str,Field(...,description='Name of Patient')]
    city:Annotated[str,Field(...,description="City")] 
    age:Annotated[int,Field(...,gt=0,le=150,description="Age of Patient")]
    gender:Annotated[str,Literal['male','female','others',Field(...,description="Gender of Patient")]]
    height_cm:Annotated[float,Field(...,gt=0,description="Height of Patient")]
    weight_kg:Annotated[float,Field(...,gt=0,description="Weight of Patient")] 
    
    @computed_field
    @property
    def bmi(self)->float:
        bmi=round(self.weight_kg/((self.height_cm/100)**2),2)
        return bmi 

    @computed_field
    @property
    def verdict(self)->str:
        if self.bmi<18.5:
            return "underweight"
        elif self.bmi>30:
            return "Overweight"
        elif self.bmi>26:
            return "Overweight"
        else:
            return "Normal"


def load_data():
    with open('../patients.json','r') as f:
        data=json.load(f)
    return data
        
        
def get_new_id(patients_list):
    if not patients_list:
        return 0
    existing_ids=[p['id'] for p in patients_list]
    return max(existing_ids)+1

def save_data(patient_list):
    with open('../patients.json','w') as f:
        json.dump(patient_list,f,indent=4)

@app.post('/create/')
def create_patient(patient:Patient):
    #load existing data
    
    data=load_data()
    
    patient_dict=patient.model_dump()
    
    data.append(patient_dict)
    
    save_data(data);
    return JSONResponse(status_code=201,content={"message":"Patient created Successfully"})
    
    
    