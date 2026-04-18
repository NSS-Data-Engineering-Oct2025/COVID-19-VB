FROM apache/airflow:2.8.1

USER airflow

RUN pip install --no-cache-dir pandas \
    requests \
    snowflake-connector-python \
    snowflake-sqlalchemy \
    python-dotenv \
    loguru \
    dbt-snowflake