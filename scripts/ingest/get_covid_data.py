import os
import io
import requests
import polars as pl
import pandas as pd
from snowflake.connector.pandas_tools import write_pandas
import snowflake.connector
from dotenv import load_dotenv
from loguru import logger

load_dotenv()

SNOWFLAKE_USER = os.getenv("SNOWFLAKE_USER")
SNOWFLAKE_PASSWORD = os.getenv("SNOWFLAKE_PASSWORD")
SNOWFLAKE_ACCOUNT = os.getenv("SNOWFLAKE_ACCOUNT")
SNOWFLAKE_WAREHOUSE = os.getenv("SNOWFLAKE_WAREHOUSE")
SNOWFLAKE_DATABASE = os.getenv("SNOWFLAKE_DATABASE")
SNOWFLAKE_SCHEMA_RAW = os.getenv("SNOWFLAKE_SCHEMA_RAW")

API_URL = os.getenv("API_URL")
TARGET_TABLE_NAME = os.getenv("TARGET_TABLE_NAME")


CHUNK_SIZE = 5000

def fetch_api_to_pandas(url):
    response = requests.get(url)
    response.raise_for_status()
    data = response.json()
    covid_data = pd.DataFrame(data)
    covid_data.columns = [col.upper() for col in covid_data.columns]
    return covid_data

def load_to_snowflake(data: pd.DataFrame, conn, table_name: str):
    result = write_pandas(conn, data, table_name)
    success, nchunks, nrows = result[:3]
    logger.info("data loaded to snowflake")

def main():
    # Connect to Snowflake
    conn = snowflake.connector.connect(
        user=SNOWFLAKE_USER,
        password=SNOWFLAKE_PASSWORD,
        account=SNOWFLAKE_ACCOUNT,
        warehouse=SNOWFLAKE_WAREHOUSE,
        database=SNOWFLAKE_DATABASE
    )
    cs = conn.cursor()
    cs.execute(f"USE DATABASE {SNOWFLAKE_DATABASE}")
    cs.execute(f"USE SCHEMA {SNOWFLAKE_SCHEMA_RAW}")  # <-- IMPORTANT
    cs.close()
    # Fetch API
    covid_data_final = fetch_api_to_pandas(API_URL)
    # covid_data_final.columns = [col.upper() for col in covid_data_final.columns]
    # Load into Snowflake
    load_to_snowflake(covid_data_final, conn, TARGET_TABLE_NAME)

    conn.close()
    logger.info(f"API data loaded into {TARGET_TABLE_NAME} successfully.")

if __name__ == "__main__":
    main()