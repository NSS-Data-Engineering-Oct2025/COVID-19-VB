select *
from {{ ref('stg_census_population') }}
where population < 0