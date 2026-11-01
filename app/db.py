import os
from contextlib import contextmanager

from dotenv import load_dotenv
from psycopg2.pool import SimpleConnectionPool

load_dotenv()

pool = SimpleConnectionPool(
    1,
    5,
    host="localhost",
    port=5432,
    dbname=os.getenv("POSTGRES_DB"),
    user=os.getenv("POSTGRES_USER"),
    password=os.getenv("POSTGRES_PASSWORD"),
)

FEATURE_SQL = """
SELECT
    EXTRACT(EPOCH FROM (%(ts)s - MAX(trans_ts))) AS secs_since_last,
    COUNT(*) FILTER (WHERE trans_ts >= %(ts)s - INTERVAL '1 hour') AS txn_count_1h,
    AVG(amount) AS avg_amount_prior
FROM transactions
WHERE card_id = %(card_id)s AND trans_ts < %(ts)s
"""


@contextmanager
def get_conn():
    conn = pool.getconn()
    try:
        yield conn
    finally:
        pool.putconn(conn)


def fetch_history_features(card_id, ts):
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(FEATURE_SQL, {"card_id": card_id, "ts": ts})
        return cur.fetchone()