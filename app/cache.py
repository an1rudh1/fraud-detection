import json

import redis

from app.db import fetch_history_features

r = redis.Redis(host="localhost", port=6380, decode_responses=True)
TTL_SECONDS = 300


def get_history_features(card_id, ts):
    key = f"feat:{card_id}:{ts.isoformat()}"

    try:
        hit = r.get(key)
    except redis.RedisError:
        print("REDIS GET FAILED")
        hit = None
    if hit is not None:
        return json.loads(hit), True

    secs, count, avg = fetch_history_features(card_id, ts)
    values = [
        float(secs) if secs is not None else None,
        count,
        float(avg) if avg is not None else None,
    ]

    try:
        r.set(key, json.dumps(values), ex=TTL_SECONDS)
    except redis.RedisError as e:
        print("REDIS SET FAILED:", e)
    return values, False