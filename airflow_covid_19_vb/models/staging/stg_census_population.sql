select 
upper(trim(NAME)) as state,
B01003_001E as population,
STATE as state_code
from {{ source('raw', 'CENSUS_POPULATION') }}