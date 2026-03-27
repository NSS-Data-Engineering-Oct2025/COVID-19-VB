import os
import snowflake.connector
from dotenv import load_dotenv
from loguru import logger

load_dotenv()

snowflake_user = os.getenv("SNOWFLAKE_USER")
snowflake_password = os.getenv("SNOWFLAKE_PASSWORD") 
snowflake_account = os.getenv("SNOWFLAKE_ACCOUNT")
snowflake_warehouse = os.getenv("SNOWFLAKE_WAREHOUSE")
snowflake_database = os.getenv("SNOWFLAKE_DATABASE")

def main():
    conn = snowflake.connector.connect(
        user = snowflake_user,
        password = snowflake_password,
        account = snowflake_account,
        warehouse = snowflake_warehouse,
        database = snowflake_database
     )

    snowflake_conn = conn.cursor()
    snowflake_conn.execute("CREATE DATABASE IF NOT EXISTS covid_db")
    snowflake_conn.execute("USE DATABASE covid_db")
    schemas = ["raw", "staging", "intermediate", "marts"]
    for schema in schemas:
      snowflake_conn.execute(f"CREATE SCHEMA IF NOT EXISTS {schema}")

    snowflake_conn.execute("""
     CREATE OR REPLACE TABLE covid_db.raw.covid_data (
     date_updated TIMESTAMP_NTZ,
     state VARCHAR,
     start_date TIMESTAMP_NTZ,
     end_date TIMESTAMP_NTZ,
     tot_cases NUMBER,
     new_cases NUMBER,
     tot_deaths NUMBER,
     new_deaths NUMBER,
     new_historic_cases NUMBER,
     new_historic_deaths NUMBER
     )
     """)
    snowflake_conn.execute("""CREATE TABLE IF NOT EXISTS raw.covid_data_stage LIKE raw.covid_data""")

    snowflake_conn.execute("""
     CREATE OR REPLACE TABLE raw.vaccination_state (
     date TIMESTAMP_NTZ,
     mmwr_week VARCHAR,
     location VARCHAR,
     administered BIGINT,
     administered_5plus BIGINT,
     administered_12plus BIGINT,
     administered_18plus BIGINT,
     administered_65plus BIGINT,

     administered_janssen BIGINT,
     administered_moderna BIGINT,
     administered_pfizer BIGINT,
     administered_novavax BIGINT,
     administered_unk_manuf BIGINT,

     administered_bivalent BIGINT,
     admin_bivalent_mod BIGINT,
     admin_bivalent_pfr BIGINT,

     administered_dose1_recip BIGINT,
     administered_dose1_recip_5plus BIGINT,
     administered_dose1_recip_12plus BIGINT,
     administered_dose1_recip_18plus BIGINT,
     administered_dose1_recip_65plus BIGINT,

     administered_dose1_pop_pct FLOAT,
     administered_dose1_recip_5pluspop_pct FLOAT,
     administered_dose1_recip_12pluspop_pct FLOAT,
     administered_dose1_recip_18pluspop_pct FLOAT,
     administered_dose1_recip_65pluspop_pct FLOAT,

     series_complete_yes BIGINT,
     series_complete_pop_pct FLOAT,

     series_complete_5plus BIGINT,
     series_complete_12plus BIGINT,
     series_complete_18plus BIGINT,
     series_complete_65plus BIGINT,

     series_complete_5pluspop_pct FLOAT,
     series_complete_12pluspop FLOAT,
     series_complete_18pluspop FLOAT,
     series_complete_65pluspop FLOAT,

     series_complete_janssen BIGINT,
     series_complete_janssen_12plus BIGINT,
     series_complete_janssen_18plus BIGINT,
     series_complete_janssen_5plus BIGINT,
     series_complete_janssen_65plus BIGINT,
                                                        
     series_complete_moderna BIGINT,
     series_complete_moderna_12plus BIGINT,
     series_complete_moderna_18plus BIGINT,
      series_complete_moderna_5plus BIGINT,
      series_complete_moderna_65plus BIGINT,
     series_complete_pfizer BIGINT,
      series_complete_pfizer_12plus BIGINT,
      series_complete_pfizer_18plus BIGINT,
      series_complete_pfizer_5plus BIGINT,
      series_complete_pfizer_65plus BIGINT,
     series_complete_novavax BIGINT,
     series_complete_unk_manuf BIGINT,
      series_complete_unk_manuf_1 BIGINT,
      series_complete_unk_manuf_2 BIGINT,
      series_complete_unk_manuf_3 BIGINT,
      series_complete_unk_manuf_5 BIGINT,
      series_complete_unk_manuf_5plus BIGINT,

     additional_doses BIGINT,
     additional_doses_vax_pct FLOAT,

     additional_doses_5plus BIGINT,
     additional_doses_12plus BIGINT,
     additional_doses_18plus BIGINT,
     additional_doses_50plus BIGINT,
     additional_doses_65plus BIGINT,

     additional_doses_5plus_vax_pct FLOAT,
     additional_doses_12plus_vax_pct FLOAT,
     additional_doses_18plus_vax_pct FLOAT,
     additional_doses_50plus_vax_pct FLOAT,
     additional_doses_65plus_vax_pct FLOAT,

     additional_doses_pfizer BIGINT,
     additional_doses_moderna BIGINT,
     additional_doses_janssen BIGINT,
     additional_doses_unk_manuf BIGINT,

     second_booster BIGINT,
     second_booster_50plus BIGINT,
     second_booster_65plus BIGINT,

     second_booster_50plus_vax_pct FLOAT,
     second_booster_65plus_vax_pct FLOAT,

     second_booster_pfizer BIGINT,
     second_booster_moderna BIGINT,
     second_booster_janssen BIGINT,
     second_booster_unk_manuf BIGINT,

     bivalent_booster_5plus BIGINT,
     bivalent_booster_12plus BIGINT,
     bivalent_booster_18plus BIGINT,
     bivalent_booster_65plus BIGINT,

     bivalent_booster_5plus_pop_pct FLOAT,
     bivalent_booster_12plus_pop_pct FLOAT,
     bivalent_booster_18plus_pop_pct FLOAT,
     bivalent_booster_65plus_pop_pct FLOAT,

     distributed BIGINT,
     distributed_janssen BIGINT,
     distributed_moderna BIGINT,
     distributed_pfizer BIGINT,
     distributed_novavax BIGINT,
     distributed_unk_manuf BIGINT,

     dist_bivalent_mod BIGINT,
     dist_bivalent_pfr BIGINT,

     dist_per_100k FLOAT,
     distributed_per_100k_5plus FLOAT,
     distributed_per_100k_12plus FLOAT,
     distributed_per_100k_18plus FLOAT,
     distributed_per_100k_65plus FLOAT,

     admin_per_100k FLOAT,
     admin_per_100k_5plus FLOAT,
     admin_per_100k_12plus FLOAT,
     admin_per_100k_18plus FLOAT,
     admin_per_100k_65plus FLOAT,

     recip_administered BIGINT
     )
      """)
    snowflake_conn.execute("""CREATE TABLE IF NOT EXISTS raw.vaccination_state_stage LIKE raw.vaccination_state""")

    snowflake_conn.execute("""
       CREATE OR REPLACE TABLE covid_db.raw.census_population (
     state_name VARCHAR,
     population NUMBER,
     state_code VARCHAR
      )
     """)
    snowflake_conn.execute("""CREATE TABLE IF NOT EXISTS raw.census_population_stage LIKE raw.census_population""")
    
    logger.info("Database and tables created successfully.")

if __name__ == "__main__":
    main()
