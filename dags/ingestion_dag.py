from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
from datetime import datetime

from ingest.census import main as census_main
from ingest.cdc_ingest import main as covid_main
from ingest.vaccination import main as vaccine_main

DBT = "/home/airflow/.local/bin/dbt"
DIR = "/opt/airflow/workspace/airflow_covid_19_vb"
PROFILES = "--profiles-dir /opt/airflow/workspace/airflow_covid_19_vb"

with DAG(
    dag_id="covid_19_dbt_pipeline",
    start_date=datetime(2024, 1, 1),
    schedule=None,
    catchup=False,
) as dag:

    task_census = PythonOperator(
        task_id="census_ingestion",
        python_callable=census_main
    )

    task_covid = PythonOperator(
        task_id="covid_ingestion",
        python_callable=covid_main
    )

    task_vaccine = PythonOperator(
        task_id="vaccine_ingestion",
        python_callable=vaccine_main
    )

    dbt_run = BashOperator(
        task_id="dbt_run",
        bash_command=f"cd {DIR} && {DBT} run {PROFILES}",
    )

    dbt_test = BashOperator(
        task_id="dbt_test",
        bash_command=f"cd {DIR} && {DBT} test {PROFILES}",
    )

    [task_census >> task_covid >> task_vaccine] >> dbt_run >> dbt_test