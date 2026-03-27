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

API_URL = os.getenv("API_CENSUS_POPULATION")
TARGET_TABLE_TWO = os.getenv("TARGET_TABLE_TWO")


def fetch_api_to_pandas(url):
    all_data = []
    offset = 0
    limit = 10000  # maximum rows per API request

    while True:
        paginated_url = f"{url}?$limit={limit}&$offset={offset}"
        logger.info(f"Fetching data with offset={offset}")
        response = requests.get(paginated_url)
        response.raise_for_status()
        data = response.json()

        if not data:  # stop when no more rows
            break

        all_data.extend(data)
        offset += limit

    df = pd.DataFrame(all_data)
    df.columns = [col.upper() for col in df.columns]
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
        database=SNOWFLAKE_DATABASE
    )

    cs = conn.cursor()
    cs.execute(f"USE DATABASE {SNOWFLAKE_DATABASE}")
    cs.execute(f"USE SCHEMA {SNOWFLAKE_SCHEMA}")
    cs.close()

    # Fetch API with pagination
    covid_data_final = fetch_api_to_pandas(API_URL)

    # Load into Snowflake
    load_to_snowflake(covid_data_final, conn, TARGET_TABLE_TWO)

    conn.close()
    logger.info(f"API data loaded into {TARGET_TABLE_TWO} successfully.")


if __name__ == "__main__":
    main()