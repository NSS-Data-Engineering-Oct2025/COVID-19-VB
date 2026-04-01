from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime

from ingest.get_census import main as census_main
from ingest.get_covid_data import main as covid_main
from ingest.get_vaccine_data import main as vaccine_main

with DAG(
    dag_id="health_ingestion",
    start_date=datetime(2024, 1, 1),
    schedule_interval="@daily",
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

    task_census >> task_covid >> task_vaccine