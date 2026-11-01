import json
from pathlib import Path

import pandas as pd
from fastapi import FastAPI, HTTPException
from xgboost import XGBClassifier

from app.schemas import PredictionResponse, TransactionFeatures

ML_DIR = Path(__file__).resolve().parent.parent / "ml"

model = XGBClassifier()
model.load_model(str(ML_DIR / "model.json"))
meta = json.loads((ML_DIR / "model_meta.json").read_text())

CATEGORY_DTYPE = pd.CategoricalDtype(categories=meta["categories"])
NUMERIC = [f for f in meta["features"] if f != "category"]

app = FastAPI(title="Fraud Detection API")


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/predict", response_model=PredictionResponse)
def predict(txn: TransactionFeatures):
    if txn.category not in meta["categories"]:
        raise HTTPException(status_code=422, detail=f"Unknown category: {txn.category}")

    row = pd.DataFrame([txn.model_dump()])[meta["features"]]
    row = row.astype({c: "float64" for c in NUMERIC})
    row["category"] = row["category"].astype(CATEGORY_DTYPE)

    score = float(model.predict_proba(row)[0, 1])
    return PredictionResponse(
        fraud_score=score,
        is_fraud=score >= meta["threshold"],
        threshold=meta["threshold"],
    )