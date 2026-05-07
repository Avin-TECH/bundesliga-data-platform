"""
Bundesliga daily refresh pipeline.

Runs daily at 06:00 UTC.
Tasks: fetch standings -> dbt run -> dbt test
"""
from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.bash import BashOperator

default_args = {
    "owner": "avin",
    "depends_on_past": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=2),
    "email_on_failure": False,
}

with DAG(
    dag_id="bundesliga_daily_refresh",
    description="Daily Bundesliga refresh: API to Postgres to dbt",
    default_args=default_args,
    start_date=datetime(2026, 5, 1),
    schedule_interval="0 6 * * *",
    catchup=False,
    tags=["bundesliga", "daily", "etl"],
) as dag:

    fetch_and_load = BashOperator(
        task_id="fetch_and_load_data",
        bash_command=(
            "pip install --quiet --root-user-action=ignore "
            "requests psycopg2-binary python-dotenv && "
            "python /opt/airflow/src/ingestion/load_standings_to_db.py"
        ),
        env={
            "FOOTBALL_DATA_API_KEY": "{{ var.value.football_data_api_key }}",
            "POSTGRES_HOST": "postgres",
            "POSTGRES_PORT": "5432",
            "POSTGRES_USER": "bundesliga",
            "POSTGRES_PASSWORD": "bundesliga_dev",
            "POSTGRES_DB": "bundesliga",
            "PYTHONPATH": "/opt/airflow",
        },
    )

    dbt_run = BashOperator(
        task_id="dbt_run",
        bash_command="docker exec bundesliga_dbt sh -c 'cd /usr/app/dbt/bundesliga_analytics && dbt run'",
    )

    dbt_test = BashOperator(
        task_id="dbt_test",
        bash_command="docker exec bundesliga_dbt sh -c 'cd /usr/app/dbt/bundesliga_analytics && dbt test'",
    )

    fetch_and_load >> dbt_run >> dbt_test
