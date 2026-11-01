CREATE TABLE IF NOT EXISTS transactions (
    trans_id   BIGSERIAL PRIMARY KEY,
    trans_ts   TIMESTAMP NOT NULL,
    card_id    BIGINT NOT NULL,
    merchant   TEXT,
    category   TEXT,
    amount     NUMERIC(10,2) NOT NULL,
    lat        DOUBLE PRECISION,
    long       DOUBLE PRECISION,
    city_pop   INT,
    merch_lat  DOUBLE PRECISION,
    merch_long DOUBLE PRECISION,
    is_fraud   SMALLINT NOT NULL
);