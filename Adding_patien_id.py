import json

def AddingId():
    with open('02/patients.json','r') as f:
        data=json.load(f)
        
    for i, patient in enumerate(data,start=0):
        patient["id"]=i 
    
    with open("02/patients.json",'w') as f:
        json.dump(data,f,indent=4)
        
AddingId()