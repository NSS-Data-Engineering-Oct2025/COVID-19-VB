WITH cases AS (
    SELECT * FROM {{ ref('int_cases_enriched') }}
),

vacc AS (
    SELECT * FROM {{ ref('int_vaccinations_enriched') }}
),

joined AS (
    SELECT
        c.week_start_date,
        c.state_abbr,
        c.state_name,
        c.state_fips,
        c.region,               
        c.division,          
        c.population,

        -- cases
        c.new_cases_cleaned    AS new_cases,
        c.new_deaths_cleaned   AS new_deaths,
        c.new_cases_per_100k,
        c.new_deaths_per_100k,
        c.case_fatality_rate,
        c.total_cases,
        c.total_deaths,
        c.rolling_4wk_avg_cases,    
        c.rolling_4wk_avg_deaths,   

        -- vaccinations
        v.series_complete_total,
        v.series_complete_pct,
        v.dose1_pop_pct,
        v.booster_doses,
        v.booster_vax_pct,          
        v.fully_vacc_per_100k,
        v.administered_per_100k,

        -- freshness
        c.latest_case_date,         
        v.latest_vacc_date        

  FROM cases c
  LEFT JOIN vacc v
    ON c.state_abbr = v.state_abbr
    AND CAST(v.week_start_date AS DATE) 
        BETWEEN DATEADD('day', -6, CAST(c.week_start_date AS DATE))
        AND     DATEADD('day',  6, CAST(c.week_start_date AS DATE))
)

SELECT * FROM joined