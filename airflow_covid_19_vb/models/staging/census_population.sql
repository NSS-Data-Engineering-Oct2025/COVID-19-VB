WITH source AS (
    SELECT * FROM {{ source('raw', 'CENSUS_POPULATION') }}
),

stg_census_population AS (
    SELECT
        TRIM((UPPER(STATE_NAME)))  AS state_name,
        POPULATION  AS population,
        STATE_CODE  AS state_fips
    FROM source
    WHERE STATE_NAME IS NOT NULL
      AND POPULATION > 0
)

SELECT * FROM stg_census_population