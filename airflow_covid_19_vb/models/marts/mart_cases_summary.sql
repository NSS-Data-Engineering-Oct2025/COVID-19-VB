{{ config(materialized='table') }}

WITH surge AS (
    SELECT * FROM {{ ref('int_cases_enriched') }}
)

SELECT
    week_start_date,
    week_end_date,
    state_abbr,
    state_name,
    region,
    division,
    population,

    new_cases_cleaned   AS new_cases,
    new_deaths_cleaned  AS new_deaths,
    total_cases,
    total_deaths,

    -- required metrics
    new_cases_per_100k,
    new_deaths_per_100k,
    case_fatality_rate,
    rolling_4wk_avg_cases,
    rolling_4wk_avg_deaths,

    -- week over week % change (custom metric 1)
    ROUND(
        (new_cases_cleaned - LAG(new_cases_cleaned) OVER (
            PARTITION BY state_abbr ORDER BY week_start_date
        )) / NULLIF(LAG(new_cases_cleaned) OVER (
            PARTITION BY state_abbr ORDER BY week_start_date
        ), 0) * 100, 2
    ) AS wow_case_change_pct,

    -- surge : >20% week over week increase
    CASE
        WHEN (new_cases_cleaned - LAG(new_cases_cleaned) OVER (
            PARTITION BY state_abbr ORDER BY week_start_date
        )) / NULLIF(LAG(new_cases_cleaned) OVER (
            PARTITION BY state_abbr ORDER BY week_start_date
        ), 0) * 100 > 20 THEN TRUE
        ELSE FALSE
    END AS is_surge_week,

    -- data freshness
    latest_case_date

FROM surge