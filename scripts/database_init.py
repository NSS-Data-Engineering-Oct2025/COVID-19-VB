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
     total_cases NUMBER,
     new_cases NUMBER,
     total_deaths NUMBER,
     new_deaths NUMBER,
     new_historic_cases NUMBER,
     new_historic_deaths NUMBER
     )
     """)

    snowflake_conn.execute("""
     CREATE OR REPLACE TABLE covid_db.raw.us_daily_data (
     date DATE,
     states NUMBER,
     positive NUMBER,
     negative NUMBER,
     pending NUMBER,
     hospitalized_currently NUMBER,
     hospitalized_cumulative NUMBER,
     in_icu_currently NUMBER,
     in_icu_cumulative NUMBER,
     on_ventilator_currently NUMBER,
     on_ventilator_cumulative NUMBER,
     date_checked TIMESTAMP_NTZ,
     death NUMBER,
     hospitalized NUMBER,
     total_test_results NUMBER,
     last_modified TIMESTAMP_NTZ,
     recovered NUMBER,
     total NUMBER,
     pos_neg NUMBER,
     death_increase NUMBER,
     hospitalized_increase NUMBER,
     negative_increase NUMBER,
     positive_increase NUMBER,
     total_test_results_increase NUMBER,
     hash VARCHAR
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
