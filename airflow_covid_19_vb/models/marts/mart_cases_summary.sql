with base as (
    select
        state_name,
        state_abbr,
        week_start_date,
        new_cases,
        new_deaths,
        total_cases,
        total_deaths,
        population
    from {{ ref('int_covid_vaccination') }}
),

metrics as (
    select
        state_name,
        state_abbr,
        week_start_date,
        new_cases,
        total_cases,
        total_deaths,
        -- 7-day rolling avg of new cases
        avg(new_cases) over (
            partition by state_name
            order by week_start_date
            rows between 6 preceding and current row
        ) as rolling_7d_avg_new_cases,
        -- cases per 100k
        round( (cast(total_cases as decimal) / nullif(population,0)) * 100000, 2) as cases_per_100k,
        -- case fatality rate
        case when total_cases > 0 then round(total_deaths / total_cases * 100,2) else 0 end as case_fatality_rate
    from base
)

select * from metrics