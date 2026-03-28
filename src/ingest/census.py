import os

import pandas as pd
import requests
import snowflake.connector
from dotenv import load_dotenv
from loguru import logger
from snowflake.connector.pandas_tools import write_pandas

load_dotenv()

SNOWFLAKE_ACCOUNT = os.getenv("SNOWFLAKE_ACCOUNT")
SNOWFLAKE_USER = os.getenv("SNOWFLAKE_USER")
SNOWFLAKE_PASSWORD = os.getenv("SNOWFLAKE_PASSWORD")

SNOWFLAKE_WAREHOUSE = os.getenv("SNOWFLAKE_WAREHOUSE")
SNOWFLAKE_DATABASE = os.getenv("SNOWFLAKE_DATABASE")
SNOWFLAKE_SCHEMA = os.getenv("SNOWFLAKE_SCHEMA")

API_CENSUS_POPULATION = os.getenv("API_CENSUS_POPULATION")
TARGET_TABLE_TWO = os.getenv("TARGET_TABLE_TWO")


def fetch_api_to_pandas(url):
    logger.info(f"Fetching Census data from {url}")
    response = requests.get(url)
    response.raise_for_status()

    data = response.json()      # Returns array of arrays
    headers = data[0]           # First row = column names
    rows = data[1:]             # Rest = actual data

    df = pd.DataFrame(rows, columns=headers)
    df.columns = [col.upper() for col in df.columns]

    # Rename to match Snowflake table columns EXACTLY
    df = df.rename(columns={
        "NAME":         "STATE_NAME",   # "Alabama", "Alaska" etc
        "B01003_001E":  "POPULATION",   # Total population count
        "STATE":        "STATE_CODE"    # FIPS code "01", "02" etc
    })

    logger.info(f"Total rows fetched: {len(df)}")
    return df

def load_to_snowflake(df: pd.DataFrame, conn, table_name: str):
    # truncate table first to avoid duplicates
    cursor = conn.cursor()
    cursor.execute(f"TRUNCATE TABLE {table_name}")
    cursor.close()

    # load data
    success, nchunks, nrows, _ = write_pandas(conn, df, table_name)
    logger.info(f"Loaded {nrows} rows into Snowflake")


def main():
    # Connect to Snowflake
    conn = snowflake.connector.connect(
        user=SNOWFLAKE_USER,
        password=SNOWFLAKE_PASSWORD,
        account=SNOWFLAKE_ACCOUNT,
        warehouse=SNOWFLAKE_WAREHOUSE,
        database=SNOWFLAKE_DATABASE,
        schema=SNOWFLAKE_SCHEMA
    )
    logger.info(f"Fetching data from {API_CENSUS_POPULATION}")

    cs = conn.cursor()
    cs.execute(f"USE DATABASE {SNOWFLAKE_DATABASE}")
    cs.execute(f"USE SCHEMA {SNOWFLAKE_SCHEMA}")
    cs.close()

    # Fetch API with pagination
    census_data_final = fetch_api_to_pandas(API_CENSUS_POPULATION)

    # Load into Snowflake
    load_to_snowflake(census_data_final, conn, TARGET_TABLE_TWO)

    conn.close()
    logger.info(f"API data loaded into {TARGET_TABLE_TWO} successfully.")


if __name__ == "__main__":
    main()