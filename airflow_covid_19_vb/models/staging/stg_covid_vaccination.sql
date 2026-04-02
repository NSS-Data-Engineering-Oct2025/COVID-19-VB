select 
DATE as data_date,
MMWR_WEEK,
LOCATION,
ADMINISTERED,
DISTRIBUTED
from {{ source('raw', 'VACCINATION_STATE') }}
