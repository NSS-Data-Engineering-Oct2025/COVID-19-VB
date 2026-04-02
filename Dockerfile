FROM apache/airflow:latest

RUN pip install --no-cache-dir dbt-snowflake pandas pendulum requests snowflake-connector-python streamlit loguru pydantic-settings apache-airflow-providers-snowflake dbt-snowflake
