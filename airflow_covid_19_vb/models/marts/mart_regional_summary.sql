with base as (
    select
        region,
        week_start_date,
        new_cases,
        total_cases,
        total_deaths,
        population
    from {{ ref('int_covid_vaccination') }}
),

aggregates as (
    select
        region,
        week_start_date,
        sum(new_cases) as total_new_cases,
        sum(total_cases) as total_cases,
        sum(total_deaths) as total_deaths,
        sum(population) as total_population,
        avg(
            round(total_deaths / nullif(total_cases,0) * 100, 2)
        ) as avg_case_fatality_rate,
        round(
            coalesce(sum(total_cases) / nullif(sum(population), 0) * 100000, 0),
            2
        ) as cases_per_100k
    from base
    group by region, week_start_date
)

select * from aggregates