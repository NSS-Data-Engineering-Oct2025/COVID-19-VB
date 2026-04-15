with base as (
    select
        state_name,
        state_abbr,
        week_start_date,
        total_cases,
        new_cases,
        total_administered,
        total_distributed,
        population
    from {{ ref('int_covid_vaccination') }}
),

vacc_metrics as (
    select
        state_name,
        state_abbr,
        week_start_date,
        total_cases,
        new_cases,
        total_administered,
        total_distributed,
        population,
        round(total_administered / population * 100, 2) as vaccination_coverage_pct,
        round(new_cases / nullif(population,0) * 100000, 2) as new_cases_per_100k
    from base
)

select * from vacc_metrics