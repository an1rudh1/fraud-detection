import random
import time
from datetime import datetime, timedelta

import numpy as np
import requests

URL = "http://127.0.0.1:8000/score"
CARD = 60416207185
N = 300
BASE = datetime(2020, 5, 1) + timedelta(minutes=random.randint(0, 40000))

session = requests.Session()


def payload(ts):
    return {
        "card_id": CARD,
        "trans_ts": ts.isoformat(),
        "amount": 50.0,
        "category": "grocery_pos",
    }


def run(timestamps):
    times = []
    for ts in timestamps:
        start = time.perf_counter()
        r = session.post(URL, json=payload(ts))
        times.append((time.perf_counter() - start) * 1000)
        r.raise_for_status()
    return np.array(times)


def report(name, ms):
    print(
        f"{name:11s} p50 {np.percentile(ms, 50):6.1f} ms | "
        f"p95 {np.percentile(ms, 95):6.1f} ms | "
        f"p99 {np.percentile(ms, 99):6.1f} ms"
    )


run([BASE - timedelta(days=1)] * 5)  # warm-up, not measured

timestamps = [BASE + timedelta(seconds=i) for i in range(N)]
report("cache MISS", run(timestamps))
report("cache HIT", run(timestamps))