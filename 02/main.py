from fastapi import FastAPI

app=FastAPI()

#1️⃣ Path Parameters

@app.get("/items/{item_id}")
def read_item(item_id:int):
    return {"item_id": item_id, "message":f"You requested item {item_id}"}

# 2️⃣Query Parameters
@app.get("/search/")
def search(q:str=None, limit: int=10):
    return {"query":q,"limit":limit}

# 3️⃣Request Body with Pydantic Models
from pydantic import BaseModel
class Item(BaseModel):
    name:str
    price:float 
    is_offer: bool=False
@app.post("/items/")
def create_item(item:Item):
    return {"message":"Item crated","item":item}


