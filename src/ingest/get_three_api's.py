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


API_DATASETS = [
    {
        "url": os.getenv("API_COVID_VACCINATION"),
        "table": "COVID_VACCINATION"
    },
    {
        "url": os.getenv("API_CENSUS_POPULATION"),  # your census dataset URL
        "table": "CENSUS_POPULATION"
    },
    {
        "url": os.getenv("API_CDC_WEEKLY_CASES"),  # your CDC weekly cases URL
        "table": "CDC_WEEKLY_CASES"
    }
]



def fetch_api_to_pandas(url, limit=10000):
    """Fetch API data with pagination and return a Pandas DataFrame"""
    all_data = []
    offset = 0

    while True:
        paginated_url = f"{url}?$limit={limit}&$offset={offset}"
        logger.info(f"Fetching data from API with offset={offset}")
        response = requests.get(paginated_url)
        response.raise_for_status()
        data = response.json()
        if not data:
            break
        all_data.extend(data)
        offset += limit

    df = pd.DataFrame(all_data)
    df.columns = [col.upper() for col in df.columns]  # uppercase columns
    logger.info(f"Total rows fetched: {len(df)}")
    return df


def load_to_snowflake(df: pd.DataFrame, conn, table_name: str):
    """Truncate the target table first, then load DataFrame to Snowflake"""
    cursor = conn.cursor()
    cursor.execute(f"TRUNCATE TABLE IF EXISTS {table_name}")
    cursor.close()

    success, nchunks, nrows, _ = write_pandas(conn, df, table_name)
    logger.info(f"Loaded {nrows} rows into Snowflake table {table_name}")


def main():
    # Connect to Snowflake
    conn = snowflake.connector.connect(
        user=SNOWFLAKE_USER,
        password=SNOWFLAKE_PASSWORD,
        account=SNOWFLAKE_ACCOUNT,
        warehouse=SNOWFLAKE_WAREHOUSE,
        database=SNOWFLAKE_DATABASE
    )

    cursor = conn.cursor()
    cursor.execute(f"USE DATABASE {SNOWFLAKE_DATABASE}")
    cursor.execute(f"USE SCHEMA {SNOWFLAKE_SCHEMA}")
    cursor.close()

    # Loop through all datasets
    for dataset in API_DATASETS:
        df = fetch_api_to_pandas(dataset["url"])
        load_to_snowflake(df, conn, dataset["table"])

    conn.close()
    logger.info("All datasets have been loaded successfully!")


if __name__ == "__main__":
    main()