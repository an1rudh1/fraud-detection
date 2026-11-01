import os

import numpy as np
import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine

FEATURES = [
    "amount", "hour_of_day", "secs_since_last",
    "txn_count_1h", "avg_amount_prior", "amount_ratio",
]


def psi(expected, actual, bins=10):
    expected = pd.Series(expected).dropna()
    actual = pd.Series(actual).dropna()
    edges = np.unique(np.quantile(expected, np.linspace(0, 1, bins + 1)))
    edges[0], edges[-1] = -np.inf, np.inf
    e = np.histogram(expected, edges)[0] / len(expected)
    a = np.histogram(actual, edges)[0] / len(actual)
    e = np.clip(e, 1e-6, None)
    a = np.clip(a, 1e-6, None)
    return float(np.sum((a - e) * np.log(a / e)))


def label(value):
    if value < 0.1:
        return "stable"
    if value < 0.25:
        return "moderate shift"
    return "MAJOR shift"


if __name__ == "__main__":
    load_dotenv()
    url = (
        f"postgresql+psycopg2://{os.getenv('POSTGRES_USER')}:"
        f"{os.getenv('POSTGRES_PASSWORD')}@localhost:5432/{os.getenv('POSTGRES_DB')}"
    )
    df = pd.read_sql("SELECT trans_ts, " + ", ".join(FEATURES) + " FROM txn_features", create_engine(url))
    df[FEATURES] = df[FEATURES].apply(pd.to_numeric)

    train = df[df["trans_ts"] < "2020-03-01"]
    recent = df[df["trans_ts"] >= "2020-03-01"]

    for f in FEATURES:
        value = psi(train[f], recent[f])
        print(f"{f:18s} PSI {value:.4f}  {label(value)}")