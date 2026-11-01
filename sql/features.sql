CREATE OR REPLACE VIEW txn_features AS
SELECT
    trans_id,
    trans_ts,
    card_id,
    category,
    amount,
    is_fraud,
    EXTRACT(HOUR FROM trans_ts)::int AS hour_of_day,
    EXTRACT(EPOCH FROM (trans_ts - LAG(trans_ts) OVER w)) AS secs_since_last,
    COUNT(*) OVER w_1h - 1 AS txn_count_1h,
    AVG(amount) OVER w_prior AS avg_amount_prior,
    amount / NULLIF(AVG(amount) OVER w_prior, 0) AS amount_ratio
FROM transactions
WINDOW
    w       AS (PARTITION BY card_id ORDER BY trans_ts),
    w_prior AS (w ROWS BETWEEN UNBOUNDED PRECEDING AND 1 PRECEDING),
    w_1h    AS (w RANGE BETWEEN INTERVAL '1 hour' PRECEDING AND CURRENT ROW);