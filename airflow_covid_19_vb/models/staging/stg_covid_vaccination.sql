select 
    DATE as data_date,
    MMWR_WEEK,
    upper(trim(LOCATION)) as location,
    ADMINISTERED,
    DISTRIBUTED
from (
    select *,
           row_number() over (
               partition by LOCATION, MMWR_WEEK
               order by DATE desc
           ) as rn
    from {{ source('raw', 'VACCINATION_STATE') }}
) t
where rn = 1
