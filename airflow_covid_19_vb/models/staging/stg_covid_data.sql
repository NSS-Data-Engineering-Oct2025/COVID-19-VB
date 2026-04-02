select 
    DATE_UPDATED as data_updated,
    upper(trim(STATE)) as state,
    START_DATE as week_start_date,
    END_DATE as week_end_date,
    TOT_CASES as total_cases,
    NEW_CASES as new_cases,
    TOT_DEATHS as total_deaths,
    NEW_DEATHS as new_deaths,
    NEW_HISTORIC_CASES as new_historic_cases,
    NEW_HISTORIC_DEATHS as new_historic_deaths
from {{ source('raw', 'COVID_DATA') }}