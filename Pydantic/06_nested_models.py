from pydantic import BaseModel


class Address(BaseModel):
    city:str
    state:str
    pin:str
    

class Patient(BaseModel):
    name:str
    gender:str
    age:int
    address:Address

address_dict={"city":"Srinagar","state":"Jammu and Kashmir","pin":"19006"}

address1=Address(**address_dict)

patient_dict={"name":"john","gender":"shemale","age":"40","address":address1}

patient1=Patient(**patient_dict)
print(patient1.address.pin)