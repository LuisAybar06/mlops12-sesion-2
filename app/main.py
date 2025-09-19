import uvicorn
from fastapi import FastAPI, File, UploadFile
from io import StringIO
import pandas as pd
from joblib import load

app = FastAPI()



@app.get("/")
def read_root():
    return {"message": "Hello"}


@app.post("/predict")
async def predict_bancknote(file: UploadFile = File(...)):
    classifier = load("app/model/linear_regression.joblib")
    
    features_df = pd.read_csv('app/data/selected_features.csv')
    features = features_df['0'].to_list()

    contents = await file.read()
    df = pd.read_csv(StringIO(contents.decode('utf-8')))
    df = df[features]

    predictions = classifier.predict(df)
    
    return {
        "predictions": predictions.tolist()
    }
