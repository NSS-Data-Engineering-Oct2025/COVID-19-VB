import os

import pandas as pd
import requests
import snowflake.connector
from dotenv import load_dotenv
from loguru import logger
from snowflake.connector.pandas_tools import write_pandas

from ingest.get_covid_data import TARGET_TABLE_NAME

load_dotenv()

SNOWFLAKE_USER = os.getenv("SNOWFLAKE_USER")
SNOWFLAKE_PASSWORD = os.getenv("SNOWFLAKE_PASSWORD")
SNOWFLAKE_ACCOUNT = os.getenv("SNOWFLAKE_ACCOUNT")
SNOWFLAKE_WAREHOUSE = os.getenv("SNOWFLAKE_WAREHOUSE")
SNOWFLAKE_DATABASE = os.getenv("SNOWFLAKE_DATABASE")
SNOWFLAKE_SCHEMA_RAW = os.getenv("SNOWFLAKE_SCHEMA_RAW")

API_URL_Vaccine = os.getenv("API_URL_Vaccine")
TARGET_TABLE_NAME_VACCINE = os.getenv("TARGET_TABLE_NAME_VACCINE")
STG_VACCINE_TABLE = os.getenv("STG_VACCINE_TABLE")

base_dir = os.path.dirname(os.path.abspath(__file__))
sql_path = os.path.join(base_dir, "..", "sql", "ingest_vaccine_data.sql")
sql_file_path = os.path.normpath(sql_path)

def fetch_api_to_pandas(url):
        all_data = []
        offset = 0
        limit = 10000
        while True:
          response = requests.get(url, params={"$offset": offset, "$limit": limit})
          response.raise_for_status()
          data = response.json()
          if not data:
            break
          all_data.extend(data)
          offset += limit
        covid_data = pd.DataFrame(all_data)
        covid_data.columns = [col.upper() for col in covid_data.columns]
        return covid_data


def load_to_snowflake(data: pd.DataFrame, conn, table_name: str):
    result = write_pandas(conn, data, table_name)
    success, nchunks, nrows = result[:3]
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
    #cs.execute(f"TRUNCATE TABLE {STAGE_TABLE}")
    logger.info("staging table truncated")
    cs.close()

    conn.close()
    logger.info("pipeline execution completed successfully")

if __name__ == "__main__":
    main()