from fastapi import FastAPI
from fastapi.responses import JSONResponse
from schema.user_input import UserInput
from model.predict import predict_output
from schema.prediction_response import PredictionResponse



  
#Added by ML/Flow  
MODEL_VERSION='1.0.0' 

app=FastAPI()

@app.get('/')
def home():
    return JSONResponse(status_code=200,content={"message":"Home page"})


@app.get('/health')
def health_check():
    return {"status":"OK","model":MODEL_VERSION,'model_loaded':model is not None}
        
@app.post('/predict',response_model=PredictionResponse)
def predict_premium(data:UserInput):
    user_input={
        'bmi':data.bmi,
        'age_group':data.age_group,
        'lifestyle_risk':data.lifestyle_risk,
        'city_tier':data.city_tier, 
        'income_lpa':data.income_lpa,
        'occupation':data.occupation
    }
    try:
        
        prediction_category=predict_output(user_input)
        return JSONResponse(status_code=200,content={"predicton_category":prediction_category})
    except Exception as e:
        return JSONResponse(status_code=500,content=str(e))
        
    