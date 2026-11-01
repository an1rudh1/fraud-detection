CREATE INDEX IF NOT EXISTS idx_tx_card_ts
ON transactions (card_id, trans_ts);