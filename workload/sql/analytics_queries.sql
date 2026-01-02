-- Analytics queries against the gold Delta table produced by the pipeline.
-- Adjust the LOCATION if you change the base path.

-- Create an external table reference for ad-hoc queries
CREATE TABLE IF NOT EXISTS guardrails_demo_gold
USING DELTA
LOCATION 'dbfs:/tmp/guardrails_demo/gold';

-- Daily revenue by event type
SELECT
  event_date,
  event_type,
  SUM(event_count) AS total_events,
  SUM(total_amount) AS total_amount,
  SUM(unique_users) AS unique_users
FROM guardrails_demo_gold
GROUP BY event_date, event_type
ORDER BY event_date, event_type;

-- Identify high refund ratios
SELECT
  event_date,
  SUM(CASE WHEN event_type = 'refund' THEN total_amount ELSE 0 END) AS refund_amount,
  SUM(total_amount) AS net_amount,
  ROUND(
    SUM(CASE WHEN event_type = 'refund' THEN total_amount ELSE 0 END) /
    NULLIF(SUM(total_amount), 0),
    4
  ) AS refund_ratio
FROM guardrails_demo_gold
GROUP BY event_date
ORDER BY event_date;

