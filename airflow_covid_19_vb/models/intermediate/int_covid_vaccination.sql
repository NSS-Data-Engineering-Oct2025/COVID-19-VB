with covid as (

    select  data_updated,
    state,
    week_start_date,
    week_end_date,
    total_cases,
    new_cases,
    total_deaths,
    new_deaths

    from {{ ref('stg_covid_data') }}

),

vaccination as (

    select state,
    mmwr_week ,
    week_start_date,
    week_end_date,
    total_administered,
    total_distributed
    from {{ ref('int_vaccination_weekly') }}

),

state_map as (

    select state_abbr, -- AL
    state_name,  -- Alabama
    state_fips,
    region,
    division 
    from {{ ref('state_mapping') }}

),
population as (

    select state, -- ALABAMA
    population,
    state_code 
    from {{ ref('stg_census_population') }}

),

final as (

    select
        s.state_abbr,
        s.state_name,
        s.region,
        s.division,

        c.week_start_date,
        c.week_end_date,

        c.new_cases,
        c.total_cases,
        c.new_deaths,
        c.total_deaths,

        v.total_administered,
        v.total_distributed,
        p.population

    from covid c

    join state_map s
        on c.state = s.state_abbr

    left join vaccination v
        on s.state_abbr = v.state
        and v.week_end_date between c.week_start_date and c.week_end_date
         
    left join population p
        on trim(lower(s.state_name)) = trim(lower(p.state))
)

select * from final