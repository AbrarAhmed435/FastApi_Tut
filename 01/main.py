from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def hello():
    return {'message':'Hello world'}
# You’re returning a Python dictionary, and FastAPI automatically:

# Converts it to JSON

# Adds content-type headers

# Returns it as a proper HTTP response

# No need for JsonResponse or HttpResponse as in Django.

@app.get("/about")
def about():
    return {'message':'I am learning fast api'}