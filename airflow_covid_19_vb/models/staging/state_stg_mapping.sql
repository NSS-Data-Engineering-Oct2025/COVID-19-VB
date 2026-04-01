WITH source AS (
    SELECT * FROM {{ source('raw', 'STATE_MAPPING') }}
),

stg_state_mapping AS (
    SELECT
        TRIM(UPPER(state_abbr))   AS state_abbr,
        TRIM(state_name)          AS state_name,
        LPAD(state_fips, 2, '0')  AS state_fips,
        TRIM(region)              AS region,
        TRIM(division)            AS division
    FROM source
    WHERE state_abbr IS NOT NULL
)

SELECT * FROM stg_state_mapping