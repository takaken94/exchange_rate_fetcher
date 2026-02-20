CREATE EXTERNAL TABLE IF NOT EXISTS exchange_rates (
  base_date date,
  base string,
  currency string,
  rate double,
  fetched_at timestamp
)
PARTITIONED BY (year string, month string)
ROW FORMAT SERDE 'org.openx.data.jsonserde.JsonSerDe'
LOCATION 's3://takaken94-exchange-rate/rate-data/';