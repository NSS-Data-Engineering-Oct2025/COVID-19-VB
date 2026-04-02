{{ config(materialized='table') }}

WITH base AS (
    SELECT * FROM {{ ref('int_cases_vaccinations_joined') }}
),

corr AS (
    SELECT
        week_start_date,
        state_abbr,
        state_name,
        region,
        population,

        -- cases
        new_cases                                   AS new_cases,
        new_cases_per_100k,
        case_fatality_rate,

        -- vaccination
        series_complete_pct,
        dose1_pop_pct,
        booster_vax_pct,
        fully_vacc_per_100k,
        administered_per_100k,

        -- herd immunity progress (custom metric)
        -- CDC threshold ~70% fully vaccinated
        ROUND(series_complete_pct, 2)               AS vacc_coverage_pct,
        CASE
            WHEN series_complete_pct >= 70 THEN 'Achieved'
            WHEN series_complete_pct >= 50 THEN 'In Progress'
            WHEN series_complete_pct >= 30 THEN 'Early Stage'
            ELSE 'Minimal'
        END                                         AS herd_immunity_status,

        -- vaccination rate vs death rate (custom metric)
        ROUND(
            series_complete_pct / NULLIF(case_fatality_rate, 0), 4
        )                                           AS vacc_to_cfr_ratio,

        -- higher ratio = better outcome (more vacc, lower CFR)
        CASE
            WHEN series_complete_pct / NULLIF(case_fatality_rate, 0) > 20
                THEN 'Strong Positive'
            WHEN series_complete_pct / NULLIF(case_fatality_rate, 0) > 10
                THEN 'Moderate Positive'
            ELSE 'Weak/Negative'
        END                                         AS vacc_death_correlation,

        -- freshness
        latest_case_date,
        latest_vacc_date

    FROM base
    WHERE series_complete_pct IS NOT NULL
)

SELECT * FROM corr