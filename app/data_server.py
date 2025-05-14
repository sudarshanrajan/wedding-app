# web_app.py
from fastapi import FastAPI, Header, HTTPException
import pandas as pd
import os
import numpy as np

app = FastAPI()

DATA_SERVER_API_KEY = os.getenv("DATA_SERVER_API_KEY")


@app.get("/")
def get_data(authorization: str = Header(None)):
    if authorization != f"Bearer {DATA_SERVER_API_KEY}":
        raise HTTPException(status_code=401, detail="Unauthorized")

    try:
        df = pd.read_csv("data/users.csv")  # Adjust path if needed
        df = df.replace([np.inf, -np.inf, np.nan], None)
        df[pd.isna(df)] = None
        return df.to_dict(orient="records")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
