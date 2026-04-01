{{ config(materialized='table') }}

WITH cases_freshness AS (
    SELECT
        'CDC Weekly Cases'          AS source_name,
        MAX(latest_case_date)       AS latest_date,
        COUNT(DISTINCT state_abbr)  AS states_covered,
        COUNT(*)                    AS total_records
    FROM {{ ref('int_cases_enriched') }}
),

vacc_freshness AS (
    SELECT
        'CDC Vaccination'           AS source_name,
        MAX(latest_vacc_date)       AS latest_date,
        COUNT(DISTINCT state_abbr)  AS states_covered,
        COUNT(*)                    AS total_records
    FROM {{ ref('int_vaccinations_enriched') }}
),

combined AS (
    SELECT * FROM cases_freshness
    UNION ALL
    SELECT * FROM vacc_freshness
)

SELECT
    source_name,
    latest_date,
    states_covered,
    total_records,
    DATEDIFF('day', latest_date, CURRENT_DATE())    AS days_since_update,
    CASE
        WHEN DATEDIFF('day', latest_date, CURRENT_DATE()) <= 7
            THEN 'Fresh'
        WHEN DATEDIFF('day', latest_date, CURRENT_DATE()) <= 30
            THEN 'Stale'
        ELSE 'Very Stale'
    END                                             AS freshness_status
FROM combined