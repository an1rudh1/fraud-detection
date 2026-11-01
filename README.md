# Real-Time Fraud Detection System

A fraud-scoring service for card transactions. Given a card, timestamp, amount and category, it computes the card's behavioral features from PostgreSQL, scores the transaction with XGBoost, and returns a fraud score in milliseconds.

**Dataset:** public simulated card transactions (Kaggle, 1.30M rows, 0.58% fraud). Results are on simulated data, not production traffic.

## Architecture

```
Client / Streamlit
        |
     FastAPI  (/score)
        |-- Redis (feature cache, 5 min TTL, fail-open)
        |-- PostgreSQL (transactions, indexed on card_id + trans_ts)
        '-- XGBoost model (loaded once at startup)
```

## Results

| Area                                     | Result                                                    |
| ---------------------------------------- | --------------------------------------------------------- |
| Model (time-based split, 272k test rows) | PR-AUC 0.90, ROC-AUC 0.998                                |
| At threshold 0.95                        | precision 0.80, recall 0.84                               |
| SQL index on (card_id, trans_ts)         | lookup 36.7 ms to 4.1 ms (~9x)                            |
| Latency, 1 client                        | miss p50 3.9 / p99 7.1 ms; Redis hit p50 2.2 / p99 3.0 ms |
| Load, 16 clients, all cache misses       | 213 req/s (1 worker) to 651 req/s (4 workers)             |
| Train/serve skew check                   | 0 mismatches in 200 sampled transactions                  |
| Drift monitor (PSI)                      | injected 50% spend increase: amount PSI 0.0001 to 0.24    |

## Design decisions

- **Features in SQL** (window functions: time since last transaction, rolling 1-hour count, expanding average spend, spend ratio), so training and serving share one definition.
- **Time-based split**, not random, to avoid leaking future patterns.
- **PR-AUC**, not accuracy: always predicting "not fraud" is 99.4% accurate.
- **Class imbalance** handled with `scale_pos_weight` (~173).
- **Model loaded once** at startup; **connection pool** for PostgreSQL.
- **Redis fails open**: if the cache is down, the API falls back to PostgreSQL.
- **Parameterized SQL** to prevent injection.

## Run it

```bash
cp .env.example .env            # then set the three POSTGRES_ values
docker compose up -d --build    # Postgres, Redis, API
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
python scripts/load_data.py     # needs data/fraudTrain.csv from Kaggle
docker exec -i fraud_postgres psql -U fraud -d frauddb < sql/features.sql
docker exec -i fraud_postgres psql -U fraud -d frauddb < sql/indexes.sql
streamlit run frontend/app.py
```

API docs: http://127.0.0.1:8000/docs

## Project layout

`app/` FastAPI service | `ml/` model files and drift monitor | `sql/` schema, feature view, indexes | `scripts/` data loader, skew check, drift simulation | `benchmarks/` latency and load tests | `frontend/` Streamlit demo | `notebooks/` exploration and training

## Limitations

- Simulated dataset, so fraud patterns are cleaner than real life.
- The threshold was chosen on the test set; a separate validation slice would be cleaner.
- Benchmarks run on one laptop with client and servers sharing the CPU, using one card.
- The cache helps repeated requests only, because a new transaction has a new timestamp.
- Training currently lives in a notebook, not a script.
![Demo](docs/demo.png)
