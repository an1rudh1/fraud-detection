import io
import os

import pandas as pd
import psycopg2
from dotenv import load_dotenv

load_dotenv()

COLS = {
    "trans_date_trans_time": "trans_ts",
    "cc_num": "card_id",
    "merchant": "merchant",
    "category": "category",
    "amt": "amount",
    "lat": "lat",
    "long": "long",
    "city_pop": "city_pop",
    "merch_lat": "merch_lat",
    "merch_long": "merch_long",
    "is_fraud": "is_fraud",
}

df = pd.read_csv("data/fraudTrain.csv", usecols=list(COLS))
df = df.rename(columns=COLS)[list(COLS.values())]
print("rows:", len(df))

conn = psycopg2.connect(
    host="localhost",
    port=5432,
    dbname=os.getenv("POSTGRES_DB"),
    user=os.getenv("POSTGRES_USER"),
    password=os.getenv("POSTGRES_PASSWORD"),
)

buf = io.StringIO()
df.to_csv(buf, index=False, header=False)
buf.seek(0)

with conn, conn.cursor() as cur:
    cur.copy_expert(
        f"COPY transactions ({', '.join(df.columns)}) FROM STDIN WITH CSV", buf
    )
conn.close()
print("loaded")