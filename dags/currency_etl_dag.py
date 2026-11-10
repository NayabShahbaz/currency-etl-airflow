"""
## Currency Exchange Rate ETL

Daily pipeline: **Frankfurter API -> transform -> MongoDB**.

| Task | What it does | XCom key pushed |
|------|--------------|-----------------|
| `extract_exchange_rates` | Calls `/v2/rates` for the base currency | `raw_exchange_rates` |
| `transform_exchange_rates` | Reshapes records into the required schema | `transformed_exchange_rates` |
| `load_exchange_rates` | Upserts documents into MongoDB | `load_summary` |

Data is passed between tasks with **named XComs** (explicit `key=` on push and pull).
"""

from datetime import timedelta

from airflow.providers.standard.operators.python import PythonOperator
from airflow.sdk import DAG
from pendulum import datetime

from include.currency_etl.extract import fetch_rates
from include.currency_etl.load import load_rates
from include.currency_etl.transform import transform_rates

# Named XCom keys - shared constants so push and pull can never drift apart
RAW_KEY = "raw_exchange_rates"
TRANSFORMED_KEY = "transformed_exchange_rates"
SUMMARY_KEY = "load_summary"


def extract_task(ti, **_):
    raw = fetch_rates()
    ti.xcom_push(key=RAW_KEY, value=raw)


def transform_task(ti, **_):
    raw = ti.xcom_pull(task_ids="extract_exchange_rates", key=RAW_KEY)
    documents = transform_rates(raw)
    ti.xcom_push(key=TRANSFORMED_KEY, value=documents)


def load_task(ti, **_):
    documents = ti.xcom_pull(task_ids="transform_exchange_rates", key=TRANSFORMED_KEY)
    summary = load_rates(documents)
    ti.xcom_push(key=SUMMARY_KEY, value=summary)


with DAG(
    dag_id="currency_exchange_etl",
    description="Daily EUR exchange rates from Frankfurter API into MongoDB",
    start_date=datetime(2026, 11, 1),
    schedule="@daily",
    catchup=False,
    doc_md=__doc__,
    default_args={
        "owner": "nayab",
        "retries": 2,
        "retry_delay": timedelta(minutes=2),
    },
    tags=["etl", "currency", "mongodb"],
) as dag:
    extract = PythonOperator(task_id="extract_exchange_rates", python_callable=extract_task)
    transform = PythonOperator(task_id="transform_exchange_rates", python_callable=transform_task)
    load = PythonOperator(task_id="load_exchange_rates", python_callable=load_task)

    extract >> transform >> load
