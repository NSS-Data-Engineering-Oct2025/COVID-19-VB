import os
import time
import pandas as pd
import requests
import snowflake.connector
from dotenv import load_dotenv
from loguru import logger
from snowflake.connector.pandas_tools import write_pandas
import random

from ingest.get_covid_data import TARGET_TABLE_NAME

load_dotenv()

SNOWFLAKE_USER = os.getenv("SNOWFLAKE_USER")
SNOWFLAKE_PASSWORD = os.getenv("SNOWFLAKE_PASSWORD")
SNOWFLAKE_ACCOUNT = os.getenv("SNOWFLAKE_ACCOUNT")
SNOWFLAKE_WAREHOUSE = os.getenv("SNOWFLAKE_WAREHOUSE")
SNOWFLAKE_DATABASE = os.getenv("SNOWFLAKE_DATABASE")
SNOWFLAKE_SCHEMA_RAW = os.getenv("SNOWFLAKE_SCHEMA_RAW")

API_URL_Vaccine = os.getenv("API_URL_Vaccine") #Naming is inconsistent
TARGET_TABLE_NAME_VACCINE = os.getenv("TARGET_TABLE_NAME_VACCINE")
STG_VACCINE_TABLE = os.getenv("STG_VACCINE_TABLE")

base_dir = os.path.dirname(os.path.abspath(__file__))
sql_path = os.path.join(base_dir, "..", "sql", "ingest_vaccine_data.sql")
sql_file_path = os.path.normpath(sql_path)

def fetch_api_to_pandas(url, max_retries=5, base_delay=1):
    """Fetch API data with pagination, exponential backoff, and max retries."""
    all_data = []
    offset = 0
    limit = 5000

    while True:
        for attempt in range(max_retries):
            try:
                response = requests.get(
                    url,
                    params={"$offset": offset, "$limit": limit},
                    timeout=30
                )
                response.raise_for_status()
                data = response.json()
                break  # Success, exit retry loop

            except requests.exceptions.RequestException as e:
                wait_time = base_delay * (2 ** attempt) + random.uniform(0, 1)
                logger.warning(
                    f"Attempt {attempt + 1} failed: {e}. Retrying in {wait_time:.2f}s..."
                )
                time.sleep(wait_time)
        else:
            # All retries failed
            logger.error(f"Max retries exceeded for offset {offset}. Skipping batch.")
            return pd.DataFrame()

        if not data:
            break

        all_data.extend(data)
        offset += limit
        time.sleep(1)  # Avoid hitting API rate limits

    df = pd.DataFrame(all_data)
    df.columns = [col.upper() for col in df.columns]
    logger.info(f"Fetched {len(df)} records from API.")
    return df


def load_to_snowflake(data: pd.DataFrame, conn, table_name: str):
    result = write_pandas(conn, data, table_name)
    success, nchunks, nrows = result[:3] #variables unpacked but not used, consider removing if not needed for logging or error handling
    logger.info("data loaded to snowflake")

def read_sql(file_path: str, **kwargs):
    with open(file_path, "r") as f:
        merge_sql = f.read()
    return merge_sql.format(**kwargs)


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
    cs.execute(f"USE SCHEMA {SNOWFLAKE_SCHEMA_RAW}")
    cs.execute(f"TRUNCATE TABLE {STG_VACCINE_TABLE}")
    covid_data_final = fetch_api_to_pandas(API_URL_Vaccine)
    load_to_snowflake(covid_data_final, conn, STG_VACCINE_TABLE)
    merge_sql = read_sql(
     sql_file_path,
     FINAL_TABLE=TARGET_TABLE_NAME_VACCINE,
     STAGE_TABLE=STG_VACCINE_TABLE
     )
    cs.execute(merge_sql)
    logger.info("merge completed successfully")
    #dead code remove the commented out code and the logger statement if we are not truncating the staging table
    #cs.execute(f"TRUNCATE TABLE {STAGE_TABLE}")
    logger.info("staging table truncated")
    cs.close()

    conn.close()
    logger.info("pipeline execution completed successfully")

if __name__ == "__main__":
    main()