import os

import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine

from app.db import fetch_history_features

load_dotenv()
url = (
    f"postgresql+psycopg2://{os.getenv('POSTGRES_USER')}:"
    f"{os.getenv('POSTGRES_PASSWORD')}@localhost:5432/{os.getenv('POSTGRES_DB')}"
)
engine = create_engine(url)

cards = pd.read_sql(
    "SELECT card_id FROM transactions GROUP BY card_id ORDER BY random() LIMIT 5",
    engine,
)["card_id"].tolist()
id_list = ",".join(str(c) for c in cards)

view = pd.read_sql(
    f"SELECT card_id, trans_ts, secs_since_last, txn_count_1h, avg_amount_prior "
    f"FROM txn_features WHERE card_id IN ({id_list})",
    engine,
)
sample = view.sample(200, random_state=1)


def same(a, b):
    a_missing = a is None or pd.isna(a)
    b_missing = b is None or pd.isna(b)
    if a_missing or b_missing:
        return a_missing and b_missing
    return abs(float(a) - float(b)) < 1e-6


bad = 0
for r in sample.itertuples():
    secs, cnt, avg = fetch_history_features(r.card_id, r.trans_ts.to_pydatetime())
    ok = (
        same(secs, r.secs_since_last)
        and same(cnt, r.txn_count_1h)
        and same(avg, r.avg_amount_prior)
    )
    if not ok:
        bad += 1
        print("MISMATCH", r.card_id, r.trans_ts)

print(f"checked {len(sample)} transactions, mismatches: {bad}")