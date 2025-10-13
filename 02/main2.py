from fastapi import FastAPI
import json


app=FastAPI()

def load_data():
    with open('patients.json','r') as f:
        data= json.load(f)
    return data
        


@app.get("/")
def PatientData():
    return {"Message":"Patient Management System API"}


@app.get("/view")
def viewData():
    data=load_data()
    return data