WITH cases AS (
    SELECT * FROM {{ ref('cdc_weekly_cases') }}
),

state_map AS (
    SELECT * FROM {{ ref('state_stg_mapping') }}
),

population AS (
    SELECT * FROM {{ ref('census_population') }}
),

cases_enriched AS (
    SELECT
        c.week_date,
        c.week_start_date,
        c.week_end_date,
        c.state_abbr,
        sm.state_name,
        sm.state_fips,
        sm.region,
        sm.division,
        p.population,

        c.total_cases,
        c.new_cases_cleaned,
        c.total_deaths,
        c.new_deaths_cleaned,
        c.new_historic_cases,
        c.new_historic_deaths,

        -- cases per 100k
        ROUND((c.new_cases_cleaned / NULLIF(p.population, 0)) * 100000, 2) AS new_cases_per_100k,
        ROUND((c.new_deaths_cleaned / NULLIF(p.population, 0)) * 100000, 2) AS new_deaths_per_100k,

        -- case fatality rate
        ROUND(c.total_deaths / NULLIF(c.total_cases, 0) * 100, 4) AS case_fatality_rate,

        -- rolling 4 week average
        AVG(c.new_cases_cleaned) OVER (
            PARTITION BY c.state_abbr
            ORDER BY c.week_start_date
            ROWS BETWEEN 3 PRECEDING AND CURRENT ROW
        ) AS rolling_4wk_avg_cases,

        AVG(c.new_deaths_cleaned) OVER (
            PARTITION BY c.state_abbr
            ORDER BY c.week_start_date
            ROWS BETWEEN 3 PRECEDING AND CURRENT ROW
        ) AS rolling_4wk_avg_deaths,

        -- data freshness
        MAX(c.week_date) OVER (
            PARTITION BY c.state_abbr
        ) AS latest_case_date

    FROM cases c
    LEFT JOIN state_map sm ON c.state_abbr = sm.state_abbr
    LEFT JOIN population p ON UPPER(TRIM(sm.state_name)) = UPPER(TRIM(p.state_name))
)

SELECT * FROM cases_enriched