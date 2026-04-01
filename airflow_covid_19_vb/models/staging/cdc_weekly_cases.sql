
WITH source AS(
    SELECT * FROM {{ source('raw', 'CDC_WEEKLY_CASES') }}
),

cdc_stg_weekly_cases AS (
    SELECT
        DATE_UPDATED AS week_date,
        TRIM(UPPER(STATE)) AS state_abbr,
        START_DATE AS week_start_date,
        END_DATE AS week_end_date,
        TOT_CASES AS total_cases,
        GREATEST(COALESCE(NEW_CASES, 0), 0)  AS new_cases_cleaned,
        TOT_DEATHS AS total_deaths,
        GREATEST(COALESCE(NEW_DEATHS, 0), 0) AS new_deaths_cleaned,
        NEW_HISTORIC_CASES AS new_historic_cases,
        NEW_HISTORIC_DEATHS AS new_historic_deaths
    FROM source 
    WHERE STATE IS NOT NULL
)
SELECT * FROM cdc_stg_weekly_cases
