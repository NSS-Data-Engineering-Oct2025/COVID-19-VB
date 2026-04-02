with covid as (
    select *
    from {{ ref('stg_covid_data') }}
),
vacc as (
    select *
    from {{ ref('stg_covid_vaccination') }}
),
pop as (
    select *
    from {{ ref('stg_census_population') }}
),
mapping as (
    select *
    from {{ ref('state_mapping') }}
)

select c.state,
c.week_start_date,
c.week_end_date,
c.total_cases,
c.new_cases,
c.total_deaths,
c.new_deaths,
v.administered,
v.distributed,
p.population,
m.state_fips,
m.region,
m.division

from covid c 
left join mapping m
    on upper(trim(c.state)) = upper(trim(m.STATE_ABBR))
left join pop p
    on upper(trim(m.STATE_NAME)) = p.state
left join vacc v
    on upper(trim(c.state)) = upper(trim(v.LOCATION))
    and date_trunc('week', c.week_start_date) = date_trunc('week', v.data_date)
where m.region is not null