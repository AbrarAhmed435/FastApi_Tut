import pandas as pd
import pickle

with open('model/model.pkl','rb') as f:
    model=pickle.load(f)
    
MODEL_VERSION='1.1.0'


class_labels=model.classes_.tolist() #ouput classes name (high,medium,low)

def predict_output(user_input:dict):
    
    df=pd.DataFrame([user_input])
    predicted_class=model.predict(df)[0]
    
    probabilities=model.predict_proba(df)[0]
    confidence=max(probabilities)    
    class_probs=dict(zip(class_labels,map(lambda p:round(p,4),probabilities)))
    
    return {
        "predicted_category":predicted_class,
        "confidence":round(confidence,4),
        "class_probabilites":class_probs
            
    }