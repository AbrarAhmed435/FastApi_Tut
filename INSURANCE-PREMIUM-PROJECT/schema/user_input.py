from pydantic import BaseModel,Field,computed_field,field_validator
from typing import Annotated,Literal
from config.city_tier import tier_1_cities,tier_2_cities

class UserInput(BaseModel):
    age:Annotated[int,Field(...,ge=0,le=200,description="Age of use")]
    weight:Annotated[float,Field(...,ge=0,le=1000,description="Weight of user")]
    height:Annotated[float,Field(...,gt=0,lt=4,description="Height in metres")]
    income_lpa:Annotated[float,Field(...,ge=0,description="Annual salary of User in Lpa")]
    smoker:Annotated[bool,Field(...,description="Is user a Smoker")]
    city:Annotated[str,Field(...,description="Place of Residence")]
    occupation:Annotated[Literal['retired', 'freelancer', 'student', 'government_job',
       'business_owner', 'unemployed', 'private_job'],Field(...,description="Occupatin of User")]
    
    @field_validator('city') # city in title case
    @classmethod
    def normalize_city(cls,v:str)->str:
        v=v.strip().title()
        return v
    
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
            return 1
        elif self.city in tier_2_cities:
            return 2
        else:
            return 3
        
