with base as (
    select
        state,
        week_start_date,
        total_cases,
        new_cases,
        administered,
        distributed,
        population
    from {{ ref('int_covid_cases_vaccinations') }}
),

vacc_metrics as (
    select
        state,
        week_start_date,
        total_cases,
        new_cases,
        administered,
        distributed,
        population,
        round(administered / population * 100, 2) as vaccination_coverage_pct,
        round(new_cases / nullif(population,0) * 100000, 2) as new_cases_per_100k
    from base
)

select * from vacc_metrics