"""Tests for the currency ETL DAG. Run with: astro dev pytest"""

from airflow.models import DagBag

from include.currency_etl.transform import transform_rates

DAG_ID = "currency_exchange_etl"


def test_dag_loads_without_errors():
    dag_bag = DagBag(include_examples=False)
    assert not dag_bag.import_errors, dag_bag.import_errors
    assert DAG_ID in dag_bag.dags


def test_dag_has_three_tasks_in_order():
    dag = DagBag(include_examples=False).dags[DAG_ID]
    assert {t.task_id for t in dag.tasks} == {
        "extract_exchange_rates",
        "transform_exchange_rates",
        "load_exchange_rates",
    }
    assert dag.get_task("extract_exchange_rates").downstream_task_ids == {"transform_exchange_rates"}
    assert dag.get_task("transform_exchange_rates").downstream_task_ids == {"load_exchange_rates"}


def test_transform_output_schema():
    raw = [
        {"date": "2026-11-04", "base": "EUR", "quote": "USD", "rate": 1.15},
        {"date": "2026-11-04", "base": "EUR", "quote": "GBP", "rate": None},  # dropped
    ]
    docs = transform_rates(raw, retrieved_at="2026-11-05T07:15:00")
    assert docs == [
        {
            "base_currency": "EUR",
            "target_currency": "USD",
            "exchange_rate": 1.15,
            "rate_date": "2026-11-04",
            "source": "Frankfurter API",
            "retrieved_at": "2026-11-05T07:15:00",
        }
    ]
