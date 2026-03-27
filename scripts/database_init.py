import os
import snowflake.connector
from dotenv import load_dotenv
from loguru import logger

# Load Snowflake credentials from environment variables
load_dotenv()

SNOWFLAKE_USER = os.getenv("SNOWFLAKE_USER")
SNOWFLAKE_PASSWORD = os.getenv("SNOWFLAKE_PASSWORD")
SNOWFLAKE_ACCOUNT = os.getenv("SNOWFLAKE_ACCOUNT")
SNOWFLAKE_WAREHOUSE = os.getenv("SNOWFLAKE_WAREHOUSE")


def setup_snowflake_environment(conn):
    snowflake = conn.cursor()

    # Create Database & Schemas
    snowflake.execute("CREATE DATABASE IF NOT EXISTS COVID_DB")
    snowflake.execute("USE DATABASE COVID_DB")

    snowflake.execute("CREATE SCHEMA IF NOT EXISTS RAW")
    snowflake.execute("CREATE SCHEMA IF NOT EXISTS STAGING")
    snowflake.execute("CREATE SCHEMA IF NOT EXISTS INTERMEDIATE")


    snowflake.execute("""
    CREATE TABLE IF NOT EXISTS RAW.COVID_VACCINATION (
        DATE DATE,
        MMWR_WEEK INTEGER,
        LOCATION STRING,

        DISTRIBUTED INTEGER,
        DISTRIBUTED_JANSSEN INTEGER,
        DISTRIBUTED_MODERNA INTEGER,
        DISTRIBUTED_PFIZER INTEGER,
        DISTRIBUTED_UNK_MANUF INTEGER,

        DIST_PER_100K INTEGER,
        DISTRIBUTED_PER_100K_12PLUS INTEGER,
        DISTRIBUTED_PER_100K_18PLUS INTEGER,
        DISTRIBUTED_PER_100K_65PLUS INTEGER,

        ADMINISTERED INTEGER,
        ADMINISTERED_12PLUS INTEGER,
        ADMINISTERED_18PLUS INTEGER,
        ADMINISTERED_65PLUS INTEGER,

        ADMINISTERED_JANSSEN INTEGER,
        ADMINISTERED_MODERNA INTEGER,
        ADMINISTERED_PFIZER INTEGER,
        ADMINISTERED_UNK_MANUF INTEGER,

        ADMIN_PER_100K INTEGER,
        ADMIN_PER_100K_12PLUS INTEGER,
        ADMIN_PER_100K_18PLUS INTEGER,
        ADMIN_PER_100K_65PLUS INTEGER,

        RECIP_ADMINISTERED INTEGER,

        ADMINISTERED_DOSE1_RECIP INTEGER,
        ADMINISTERED_DOSE1_POP_PCT FLOAT,

        SERIES_COMPLETE_YES INTEGER,
        SERIES_COMPLETE_POP_PCT FLOAT,

        ADDITIONAL_DOSES INTEGER,
        ADDITIONAL_DOSES_VAX_PCT FLOAT
    )
    """)


    snowflake.execute("""
    CREATE TABLE IF NOT EXISTS RAW.CENSUS_POPULATION (
        POPULATION INTEGER,
        STATE_NAME STRING,
        STATE_CODE STRING
    )
    """)


    snowflake.execute("""
    CREATE TABLE IF NOT EXISTS RAW.CDC_WEEKLY_CASES (
        DATE_UPDATED DATE,
        STATE STRING,
        START_DATE DATE,
        END_DATE DATE,

        TOT_CASES FLOAT,
        NEW_CASES FLOAT,
        TOT_DEATHS FLOAT,
        NEW_DEATHS FLOAT,

        NEW_HISTORIC_CASES INTEGER,
        NEW_HISTORIC_DEATHS INTEGER
    )
    """)

    snowflake.close()
    logger.info("Snowflake environment setup complete!")


def main():
    conn = snowflake.connector.connect(
        user=SNOWFLAKE_USER,
        password=SNOWFLAKE_PASSWORD,
        account=SNOWFLAKE_ACCOUNT,
        warehouse=SNOWFLAKE_WAREHOUSE
    )
    setup_snowflake_environment(conn)

    conn.close()


if __name__ == "__main__":
    main()