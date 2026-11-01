from datetime import datetime

from typing import Optional

from pydantic import BaseModel, Field


class TransactionFeatures(BaseModel):
    amount: float = Field(gt=0)
    hour_of_day: int = Field(ge=0, le=23)
    secs_since_last: Optional[float] = None
    txn_count_1h: int = Field(ge=0)
    avg_amount_prior: Optional[float] = None
    amount_ratio: Optional[float] = None
    category: str


class PredictionResponse(BaseModel):
    fraud_score: float
    is_fraud: bool
    threshold: float

class TransactionRequest(BaseModel):
    card_id: int
    trans_ts: datetime
    amount: float = Field(gt=0)
    category: str