with vaccination_weekly as (

    select
        state,
        mmwr_week,
        min(data_date) as week_start_date,
        max(data_date) as week_end_date,
        max(administered) as total_administered,
        max(distributed) as total_distributed

    from {{ ref('stg_covid_vaccination') }}

    group by state, mmwr_week

)

select * from vaccination_weekly