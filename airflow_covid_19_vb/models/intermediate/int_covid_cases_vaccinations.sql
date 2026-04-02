select 
    c.state,
    c.week_start_date,
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
from {{ ref('stg_covid_data') }} c
left join {{ ref('stg_census_population') }} p
    on upper(trim(c.state)) = upper(trim(p.state))
left join {{ ref('stg_covid_vaccination') }} v
    on upper(trim(c.state)) = upper(trim(v.LOCATION))
left join {{ ref('state_mapping') }} m
    on upper(trim(c.state)) = upper(trim(m.STATE_ABBR))
where upper(trim(c.state)) in (
    select upper(trim(state_abbr)) from {{ ref('state_mapping') }}
)