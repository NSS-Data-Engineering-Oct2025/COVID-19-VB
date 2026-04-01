{{ config(materialized='table') }}

WITH base AS (
    SELECT * FROM {{ ref('int_cases_vaccinations_joined') }}
),

regional AS (
    SELECT
        week_start_date,
        region,

        -- aggregate to region level
        SUM(new_cases)                              AS regional_new_cases,
        SUM(new_deaths)                             AS regional_new_deaths,
        SUM(total_cases)                            AS regional_total_cases,
        SUM(total_deaths)                           AS regional_total_deaths,
        SUM(population)                             AS regional_population,

        -- weighted case fatality rate by region
        ROUND(
            SUM(total_deaths) / NULLIF(SUM(total_cases), 0) * 100, 4
        )                                           AS regional_cfr,

        -- cases per 100k at region level
        ROUND(
            SUM(new_cases) / NULLIF(SUM(population), 0) * 100000, 2
        )                                           AS regional_cases_per_100k,

        -- booster adoption rate by region (custom metric)
        ROUND(
            SUM(booster_doses) / NULLIF(SUM(population), 0) * 100, 2
        )                                           AS booster_adoption_rate_pct,

        -- avg vaccination coverage in region
        ROUND(AVG(series_complete_pct), 2)          AS avg_vacc_coverage_pct

    FROM base
    WHERE region IS NOT NULL
    GROUP BY 1, 2
)

SELECT * FROM regional