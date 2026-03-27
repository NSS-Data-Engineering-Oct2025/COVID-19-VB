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

    snowflake_conn.execute("""
     CREATE OR REPLACE TABLE raw.vaccination_state (
    date TIMESTAMP_NTZ,
    mmwr_week VARCHAR,
    location VARCHAR,
    distributed NUMBER,
    distributed_janssen NUMBER,
    distributed_moderna NUMBER,
    distributed_pfizer NUMBER,
    distributed_unk_manuf NUMBER,
    dist_per_100k NUMBER,
    distributed_per_100k_12plus NUMBER,
    distributed_per_100k_18plus NUMBER,
    distributed_per_100k_65plus NUMBER,
    administered NUMBER,
    administered_12plus NUMBER,
    administered_18plus NUMBER,
    administered_65plus NUMBER,
    administered_janssen NUMBER,
    administered_moderna NUMBER,
    administered_pfizer NUMBER,
    administered_unk_manuf NUMBER,
    admin_per_100k NUMBER,
    admin_per_100k_12plus NUMBER,
    admin_per_100k_18plus NUMBER,
    admin_per_100k_65plus NUMBER,
    recip_administered NUMBER,
    administered_dose1_recip NUMBER,
    administered_dose1_pop_pct NUMBER(5,2),
    administered_dose1_recip_12plus NUMBER,
    administered_dose1_recip_12pluspop_pct NUMBER(5,2),
    administered_dose1_recip_18plus NUMBER,
    administered_dose1_recip_18pluspop_pct NUMBER(5,2),
    administered_dose1_recip_65plus NUMBER,
    administered_dose1_recip_65pluspop_pct NUMBER(5,2),
    series_complete_yes NUMBER,
    series_complete_pop_pct NUMBER(5,2),
    series_complete_12plus NUMBER,
    series_complete_12pluspop NUMBER(5,2),
    series_complete_18plus NUMBER,
    series_complete_18pluspop NUMBER(5,2),
    series_complete_65plus NUMBER,
    series_complete_65pluspop NUMBER(5,2),
    series_complete_janssen NUMBER,
    series_complete_moderna NUMBER,
    series_complete_pfizer NUMBER,
    series_complete_unk_manuf NUMBER,
    series_complete_janssen_12plus NUMBER,
    series_complete_moderna_12plus NUMBER,
    series_complete_pfizer_12plus NUMBER,
    series_complete_unk_manuf_1 NUMBER,
    series_complete_janssen_18plus NUMBER,
    series_complete_moderna_18plus NUMBER,
    series_complete_pfizer_18plus NUMBER,
    series_complete_unk_manuf_2 NUMBER,
    series_complete_janssen_65plus NUMBER,
    series_complete_moderna_65plus NUMBER,
    series_complete_pfizer_65plus NUMBER,
    series_complete_unk_manuf_3 NUMBER,
    additional_doses NUMBER,
    additional_doses_vax_pct NUMBER(5,2),
    additional_doses_18plus NUMBER,
    additional_doses_18plus_vax_pct NUMBER(5,2),
    additional_doses_50plus NUMBER,
    additional_doses_50plus_vax_pct NUMBER(5,2),
    additional_doses_65plus NUMBER,
    additional_doses_65plus_vax_pct NUMBER(5,2),
    additional_doses_moderna NUMBER,
    additional_doses_pfizer NUMBER,
    additional_doses_janssen NUMBER,
    additional_doses_unk_manuf NUMBER
   )
      """)
    
    snowflake_conn.execute("""
       CREATE OR REPLACE TABLE covid_db.raw.census_population (
     state_name VARCHAR,
     population NUMBER,
     state_code VARCHAR
      )
     """)
    logger.info("Database and tables created successfully.")
if __name__ == "__main__":
    main()
