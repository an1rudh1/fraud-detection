import random
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta

import numpy as np
import requests

URL = "http://127.0.0.1:8000/score"
CARD = 60416207185
WORKERS = 16
TOTAL = 2000
BASE = datetime(2020, 5, 1) + timedelta(minutes=random.randint(0, 40000))

local = threading.local()


def one_call(i):
    if not hasattr(local, "session"):
        local.session = requests.Session()
    body = {
        "card_id": CARD,
        "trans_ts": (BASE + timedelta(seconds=i)).isoformat(),
        "amount": 50.0,
        "category": "grocery_pos",
    }
    start = time.perf_counter()
    r = local.session.post(URL, json=body)
    r.raise_for_status()
    return (time.perf_counter() - start) * 1000


start = time.perf_counter()
with ThreadPoolExecutor(WORKERS) as pool:
    ms = np.array(list(pool.map(one_call, range(TOTAL))))
elapsed = time.perf_counter() - start

print(f"{TOTAL} requests, {WORKERS} concurrent clients, all cache misses")
print(f"throughput {TOTAL / elapsed:.0f} req/s")
print(
    f"p50 {np.percentile(ms, 50):.1f} ms | "
    f"p95 {np.percentile(ms, 95):.1f} ms | "
    f"p99 {np.percentile(ms, 99):.1f} ms"
)