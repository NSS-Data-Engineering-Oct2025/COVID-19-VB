import snowflake.connector
import pandas as pd
import os
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

def get_snowflake_connection():
    """Create a Snowflake connection using env variables"""
    conn = snowflake.connector.connect(
        user=os.getenv("SNOWFLAKE_USER"),
        password=os.getenv("SNOWFLAKE_PASSWORD"),
        account=os.getenv("SNOWFLAKE_ACCOUNT"),
        warehouse=os.getenv("SNOWFLAKE_WAREHOUSE"),
        database=os.getenv("SNOWFLAKE_DATABASE"),
        schema=os.getenv("SNOWFLAKE_SCHEMA_DASHBOARD")
    )
    return conn

def query_snowflake(sql: str) -> pd.DataFrame:
    """Execute a query and return a Pandas DataFrame"""
    conn = get_snowflake_connection()
    try:
        data = pd.read_sql(sql, conn)
        return data
    finally:
        conn.close()

# import snowflake.connector

# conn = snowflake.connector.connect(
#     user="PV",               # exact username
#     password="Admin@123DE1de2",  # exact password
#     account="onzkokh-jm43762",    # account locator
#     warehouse="COMPUTE_WH",
#     database="covid_db",
#     schema="MARTS"
# )

# cs = conn.cursor()
# try:
#     cs.execute("SELECT CURRENT_USER(), CURRENT_DATABASE(), CURRENT_SCHEMA()")
#     print(cs.fetchone())
# finally:
#     cs.close()
#     conn.close()