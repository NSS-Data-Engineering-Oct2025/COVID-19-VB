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

API_URL = os.getenv("API_CDC_WEEKLY_CASES")
TARGET_TABLE_THREE = os.getenv("TARGET_TABLE_THREE")

def sanitize_columns(df: pd.DataFrame):
    """Make column names safe for Snowflake"""
    df.columns = (
        df.columns
        .str.upper()
        .str.replace(" ", "_")
        .str.replace("-", "_")
        .str.replace("/", "_")
        .str.replace(r"[^A-Z0-9_]", "", regex=True)
    )
    return df

def fetch_api_to_pandas(url):
    all_data = []
    offset = 0
    limit = 10000

    while True:
        paginated_url = f"{url}?$limit={limit}&$offset={offset}"
        logger.info(f"Fetching data with offset={offset}")
        response = requests.get(paginated_url)
        response.raise_for_status()
        data = response.json()

        if not data:
            break

        all_data.extend(data)
        offset += limit

    df = pd.DataFrame(all_data)
    df = sanitize_columns(df)
    logger.info(f"Total rows fetched: {len(df)}")
    return df

def load_to_snowflake(df: pd.DataFrame, conn, table_name: str):
    cursor = conn.cursor()
    cursor.execute(f"TRUNCATE TABLE {table_name}")
    cursor.close()

    success, nchunks, nrows, _ = write_pandas(conn, df, table_name, quote_identifiers=True)
    logger.info(f"Loaded {nrows} rows into Snowflake table {table_name}")

def main():
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

    covid_data_final = fetch_api_to_pandas(API_URL)
    load_to_snowflake(covid_data_final, conn, TARGET_TABLE_THREE)

    conn.close()
    logger.info(f"API data loaded into {TARGET_TABLE_THREE} successfully.")

if __name__ == "__main__":
    main()