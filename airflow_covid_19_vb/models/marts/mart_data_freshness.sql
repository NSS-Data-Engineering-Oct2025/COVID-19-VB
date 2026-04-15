with sources as (
    select
        'COVID_DATA' as source_name,
        max(data_updated) as last_updated
    from {{ ref('stg_covid_data') }}
    
    union all
    
    select
        'VACCINATION_STATE' as source_name,
        max(data_date) as last_updated
    from {{ ref('stg_covid_vaccination') }}
    
    union all
    
    select
        'CENSUS_POPULATION' as source_name,
        null::timestamp as last_updated  -- no date column
)
select
    source_name,
    last_updated,
    case
        when last_updated is null then null
        else datediff('day', last_updated, current_date)
    end as days_since_last_update
from sources