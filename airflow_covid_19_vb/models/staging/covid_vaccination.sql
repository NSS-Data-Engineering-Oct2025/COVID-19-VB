WITH source AS (
    SELECT * FROM {{ source('raw', 'COVID_VACCINATION') }}
),

stg_covid_vaccination AS (
    SELECT
        DATE                                    AS vaccination_date,
        MMWR_WEEK                               AS mmwr_week,
        TRIM(UPPER(LOCATION))                   AS state_abbr,

        -- total administered
        ADMINISTERED                            AS total_administered,
        ADMINISTERED_5PLUS                      AS administered_5plus,
        ADMINISTERED_12PLUS                     AS administered_12plus,
        ADMINISTERED_18PLUS                     AS administered_18plus,
        ADMINISTERED_65PLUS                     AS administered_65plus,

        -- by manufacturer
        ADMINISTERED_JANSSEN                    AS administered_janssen,
        ADMINISTERED_MODERNA                    AS administered_moderna,
        ADMINISTERED_PFIZER                     AS administered_pfizer,
        ADMINISTERED_NOVAVAX                    AS administered_novavax,

        -- series complete (fully vaccinated)
        SERIES_COMPLETE_YES                     AS series_complete_total,
        SERIES_COMPLETE_POP_PCT                 AS series_complete_pct,
        SERIES_COMPLETE_5PLUS                   AS series_complete_5plus,
        SERIES_COMPLETE_12PLUS                  AS series_complete_12plus,
        SERIES_COMPLETE_18PLUS                  AS series_complete_18plus,
        SERIES_COMPLETE_65PLUS                  AS series_complete_65plus,

        -- dose 1
        ADMINISTERED_DOSE1_RECIP                AS dose1_recipients,
        ADMINISTERED_DOSE1_POP_PCT              AS dose1_pop_pct,

        -- boosters
        ADDITIONAL_DOSES                        AS booster_doses,
        ADDITIONAL_DOSES_VAX_PCT                AS booster_vax_pct,
        SECOND_BOOSTER                          AS second_booster,
        SECOND_BOOSTER_50PLUS                   AS second_booster_50plus,
        SECOND_BOOSTER_65PLUS                   AS second_booster_65plus,

        -- bivalent booster
        BIVALENT_BOOSTER_5PLUS                  AS bivalent_booster_5plus,
        BIVALENT_BOOSTER_12PLUS                 AS bivalent_booster_12plus,
        BIVALENT_BOOSTER_18PLUS                 AS bivalent_booster_18plus,
        BIVALENT_BOOSTER_65PLUS                 AS bivalent_booster_65plus,

        -- distribution
        DISTRIBUTED                             AS total_distributed,
        DIST_PER_100K                           AS distributed_per_100k,
        ADMIN_PER_100K                          AS administered_per_100k

    FROM source
    WHERE LOCATION IS NOT NULL
      AND DATE IS NOT NULL
)

SELECT * FROM stg_covid_vaccination