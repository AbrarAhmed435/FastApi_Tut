from fastapi import FastAPI,Path,HTTPException,Query
import json


app=FastAPI()

def load_data():
    with open('patients.json','r') as f:
        data= json.load(f)
    return data
        
def LoadPatient(id):
    with open('../patients.json','r') as f:
        data=json.load(f)
        
    for patient in data:
        if patient["id"]==id:
            return patient
    raise HTTPException(status_code=404,detail="Patient not found")

@app.get("/")
def PatientData():
    return {"Message":"Patient Management System-API"}


@app.get("/view")
def viewData():
    data=load_data()
    return data



@app.get("/view/patient/{id}")
def GetPatient(id:int=Path(...,description="id of patient(interger)",ge=0,le=100)):
    data=LoadPatient(id)
    return data


@app.get('/sort')
def sort_patient(sort_by:str=Query(...,description="Sort on the basis of height,weight,bmi"),order:str=Query('asc',description="Sort in asc or desc order")):
    valid_fields=['height_cm','weight_kg','bmi']
    if sort_by not  in valid_fields:
        raise HTTPException(status_code=400,detail=f"Invalid field select from {valid_fields}")
    if order not in ['asc','desc']:
        raise HTTPException(status_code=400,detail="Invalid order select between asc and desc")
    data=load_data()
    sort_order=True if order=='desc' else False
    sorted_data=sorted(data,key=lambda x:x.get(sort_by,0),reverse=sort_order)
    
    return {"sorted_data":sorted_data}

