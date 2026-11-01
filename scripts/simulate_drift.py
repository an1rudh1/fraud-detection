import os

import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine

from ml.drift import FEATURES, label, psi

load_dotenv()
url = (
    f"postgresql+psycopg2://{os.getenv('POSTGRES_USER')}:"
    f"{os.getenv('POSTGRES_PASSWORD')}@localhost:5432/{os.getenv('POSTGRES_DB')}"
)
df = pd.read_sql(
    "SELECT trans_ts, " + ", ".join(FEATURES) + " FROM txn_features",
    create_engine(url),
)
df[FEATURES] = df[FEATURES].apply(pd.to_numeric)

train = df[df["trans_ts"] < "2020-03-01"]
recent = df[df["trans_ts"] >= "2020-03-01"]

drifted = recent.copy()
drifted["amount"] *= 1.5
drifted["amount_ratio"] *= 1.5

print(f"{'feature':18s} {'normal':>8s} {'drifted':>8s}")
for f in FEATURES:
    a = psi(train[f], recent[f])
    b = psi(train[f], drifted[f])
    print(f"{f:18s} {a:8.4f} {b:8.4f}  {label(b)}")