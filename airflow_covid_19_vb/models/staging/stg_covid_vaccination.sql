select 
    DATE as data_date,
    MMWR_WEEK,
    upper(trim(LOCATION)) as state,
    ADMINISTERED,
    DISTRIBUTED
from {{ source('raw', 'VACCINATION_STATE') }}
where location is not null
and ADMINISTERED > 0
