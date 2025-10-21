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


temp1=patient1.model_dump()
temp2=patient1.model_dump(include=['name','gender']) #exclude as well exclude=[name,gender]
temp3=patient1.model_dump(exclude={'address':['state']}) #exclude as well exclude=[name,gender]
temp4=patient1.model_dump_json()

#exclude unset


print(temp3)
print(type(temp2))