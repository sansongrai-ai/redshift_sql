CREATE SCHEMA IF NOT EXISTS covid_gold;
CREATE TABLE IF NOT EXISTS covid_gold.dim_date (
  date_id int PRIMARY KEY,
  full_date date,
  year smallint,
  month smallint,
  day smallint,
  dow smallint,
  is_weekend boolean
)
SORTKEY(date_id);
CREATE TABLE IF NOT EXISTS covid_gold.dim_state (
  state_code varchar(2) PRIMARY KEY,
  state_name varchar(64)
)
DISTSTYLE ALL;

CREATE TABLE IF NOT EXISTS covid_gold.fact_cases_state_daily (
  date_id int NOT NULL,
  state_code varchar(2) NOT NULL,
  cases_cum bigint,
  deaths_cum bigint,
  new_cases int,
  new_deaths int
)
DISTKEY(state_code)
SORTKEY(date_id, state_code);

CREATE TABLE IF NOT EXISTS covid_gold.fact_testing_state_daily (
  date_id int NOT NULL,
  state_code varchar(2) NOT NULL,
  tests_total_cum bigint,
  tests_pos_cum bigint,
  tests_neg_cum bigint,
  new_tests int,
  positivity_rate double precision
)
DISTKEY(state_code)
SORTKEY(date_id, state_code);

COPY covid_gold.dim_date
FROM 's3://my-covid-data-lake/covid/gold/dim_date/'
IAM_ROLE 'arn:aws:iam::445448907072:role/redshift-role'
FORMAT AS PARQUET;


COPY covid_gold.dim_state
FROM 's3://my-covid-data-lake/covid/gold/dim_state/'
IAM_ROLE 'arn:aws:iam::445448907072:role/redshift-role'
FORMAT AS PARQUET;

SELECT COUNT(*) 
FROM covid_gold.dim_state;

COPY covid_gold.fact_cases_state_daily
FROM 's3://my-covid-data-lake/covid/gold/fact_cases_state_daily/'
IAM_ROLE 'arn:aws:iam::445448907072:role/redshift-role'
FORMAT AS PARQUET;

COPY covid_gold.fact_testing_state_daily
FROM 's3://my-covid-data-lake/covid/gold/fact_testing_state_daily/'
IAM_ROLE 'arn:aws:iam::445448907072:role/redshift-role'
FORMAT AS PARQUET;

SELECT s.state_name, f.new_cases
FROM covid_gold.fact_cases_state_daily f
JOIN covid_gold.dim_state s ON s.state_code = f.state_code
WHERE f.date_id = 20200515
ORDER BY f.new_cases DESC
LIMIT 5;

SELECT d.full_date,
       (t.tests_pos_cum::double precision / NULLIF(t.tests_total_cum, 0)) AS positivity_rate
FROM covid_gold.fact_testing_state_daily t
JOIN covid_gold.dim_date d   ON d.date_id = t.date_id
WHERE t.state_code = 'NY'
ORDER BY d.full_date;

SELECT d.full_date,
       c.new_cases,
       t.new_tests,
       (t.tests_pos_cum::double precision / NULLIF(t.tests_total_cum, 0)) AS positivity_rate
FROM covid_gold.fact_cases_state_daily   c
JOIN covid_gold.fact_testing_state_daily t
  ON t.date_id = c.date_id AND t.state_code = c.state_code
JOIN covid_gold.dim_date d ON d.date_id = c.date_id
WHERE c.state_code = 'CA'
ORDER BY d.full_date;