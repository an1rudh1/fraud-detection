import json
from pathlib import Path

import pandas as pd
from fastapi import FastAPI, HTTPException, Response
from xgboost import XGBClassifier

from app.cache import get_history_features
from app.schemas import PredictionResponse, TransactionFeatures, TransactionRequest

ML_DIR = Path(__file__).resolve().parent.parent / "ml"

model = XGBClassifier()
model.load_model(str(ML_DIR / "model.json"))
meta = json.loads((ML_DIR / "model_meta.json").read_text())

CATEGORY_DTYPE = pd.CategoricalDtype(categories=meta["categories"])
NUMERIC = [f for f in meta["features"] if f != "category"]

app = FastAPI(title="Fraud Detection API")


def score(features: dict) -> PredictionResponse:
    if features["category"] not in meta["categories"]:
        raise HTTPException(status_code=422, detail=f"Unknown category: {features['category']}")

    row = pd.DataFrame([features])[meta["features"]]
    row = row.astype({c: "float64" for c in NUMERIC})
    row["category"] = row["category"].astype(CATEGORY_DTYPE)

    fraud_score = float(model.predict_proba(row)[0, 1])
    return PredictionResponse(
        fraud_score=fraud_score,
        is_fraud=fraud_score >= meta["threshold"],
        threshold=meta["threshold"],
    )


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/predict", response_model=PredictionResponse)
def predict(txn: TransactionFeatures):
    return score(txn.model_dump())


@app.post("/score", response_model=PredictionResponse)
@app.post("/score", response_model=PredictionResponse)
def score_transaction(req: TransactionRequest, response: Response):
    (secs, count, avg), cache_hit = get_history_features(req.card_id, req.trans_ts)
    response.headers["X-Cache"] = "HIT" if cache_hit else "MISS"
    features = {
        "amount": req.amount,
        "hour_of_day": req.trans_ts.hour,
        "secs_since_last": secs,
        "txn_count_1h": count,
        "avg_amount_prior": avg,
        "amount_ratio": req.amount / avg if avg else None,
        "category": req.category,
    }
    return score(features)