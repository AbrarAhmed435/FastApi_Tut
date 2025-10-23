from fastapi import FastAPI
from pydantic import BaseModel,Field,computed_field
from typing import Annotated,Literal
import pickle
import pandas as pd

with open('model.pkl','rb') as f:
    model=pickle.load(f)
    

app=FastAPI()

tier_1_cities = ["Mumbai", "Delhi", "Bangalore", "Chennai", "Kolkata", "Hyderabad", "Pune"]
tier_2_cities = [
    "Jaipur", "Srinagar","Chandigarh", "Indore", "Lucknow", "Patna", "Ranchi", "Visakhapatnam", "Coimbatore",
    "Bhopal", "Nagpur", "Vadodara", "Surat", "Rajkot", "Jodhpur", "Raipur", "Amritsar", "Varanasi",
    "Agra", "Dehradun", "Mysore", "Jabalpur", "Guwahati", "Thiruvananthapuram", "Ludhiana", "Nashik",
    "Allahabad", "Udaipur", "Aurangabad", "Hubli", "Belgaum", "Salem", "Vijayawada", "Tiruchirappalli",
    "Bhavnagar", "Gwalior", "Dhanbad", "Bareilly", "Aligarh", "Gaya", "Kozhikode", "Warangal",
    "Kolhapur", "Bilaspur", "Jalandhar", "Noida", "Guntur", "Asansol", "Siliguri"
]


class UserInput(BaseModel):
    age:Annotated[int,Field(...,ge=0,le=200,description="Age of use")]
    weight:Annotated[float,Field(...,ge=0,le=1000,description="Weight of user")]
    height:Annotated[float,Field(...,gt=0,lt=4,description="Height in metres")]
    income_lpa:Annotated[float,Field(...,ge=0,description="Annual salary of User in Lpa")]
    smoker:Annotated[bool,Field(...,description="Is user a Smoker")]
    city:Annotated[str,Field(...,description="Place of Residence")]
    occupation:Annotated[Literal['retired','freelancer','student','government_job','business_owner','unemployed','private_job'],Field(...,description="Occupatin of User")]
    
    @computed_field
    @property
    def bmi(self)->float:
        return round(self.weight/(self.height**2),2)
    
    @computed_field
    @property
    def lifestyle_risk(self)->str:
        if self.smoker and self.bmi>30:
            return 'high'
        elif self.smoker and self.bmi>27:
            return 'medium'
        else:
            return 'low'
        
    @computed_field
    @property
    def age_group(self)->str:
        if self.age<25:
            return 'young'
        elif self.age<45:
            return 'adult'
        elif self.age<60:
            return 'middle_age'
        else:
            return 'senior'
        
    @computed_field
    @property
    def city_tier(self)->int:
        if self.city in tier_1_cities:
            return '1'
        elif self.city in tier_2_cities:
            return '2'
        else:
            '3'
        
        
@app.post('/predict')
def predict_premium(data:UserInput):
    
