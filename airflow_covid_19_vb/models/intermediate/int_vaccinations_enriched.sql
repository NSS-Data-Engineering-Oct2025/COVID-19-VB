WITH vacc AS (
    SELECT * FROM {{ ref('covid_vaccination') }}
),

state_map AS (
    SELECT * FROM {{ ref('state_stg_mapping') }}
),

population AS (
    SELECT * FROM {{ ref('census_population') }}
),

weekly_vacc AS (
    SELECT
        DATE_TRUNC('week', vaccination_date)    AS week_start_date,
        state_abbr,
        MAX(series_complete_total)              AS series_complete_total,
        MAX(series_complete_pct)                AS series_complete_pct,
        MAX(dose1_recipients)                   AS dose1_recipients,
        MAX(dose1_pop_pct)                      AS dose1_pop_pct,
        MAX(booster_doses)                      AS booster_doses,
        MAX(booster_vax_pct)                    AS booster_vax_pct,
        MAX(total_administered)                 AS total_administered,
        MAX(administered_per_100k)              AS administered_per_100k,
        MAX(total_distributed)                  AS total_distributed,
        MAX(distributed_per_100k)               AS distributed_per_100k,
        MAX(vaccination_date)                   AS latest_vacc_date
    FROM vacc
    GROUP BY week_start_date, state_abbr
),

vacc_enriched AS (
    SELECT
        wv.week_start_date,
        wv.state_abbr,
        sm.state_name,
        sm.state_fips,
        sm.region,                  -- ← added
        sm.division,                -- ← added
        p.population,

        wv.series_complete_total,
        wv.series_complete_pct,
        wv.dose1_recipients,
        wv.dose1_pop_pct,
        wv.booster_doses,
        wv.booster_vax_pct,         -- ← added
        wv.total_administered,
        wv.administered_per_100k,
        wv.total_distributed,       -- ← added
        wv.distributed_per_100k,    -- ← added

        -- vaccination coverage per 100k
        ROUND(
            (wv.series_complete_total / NULLIF(p.population, 0)) * 100000, 2
        ) AS fully_vacc_per_100k,

        wv.latest_vacc_date         -- ← added

    FROM weekly_vacc wv
    LEFT JOIN state_map sm ON wv.state_abbr = sm.state_abbr
    LEFT JOIN population p ON UPPER(TRIM(sm.state_name)) = UPPER(TRIM(p.state_name))
    -- ← fixed join from state_fips to state_name
)

SELECT * FROM vacc_enriched