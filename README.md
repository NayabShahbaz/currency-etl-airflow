# Currency Exchange Rate ETL (Airflow + Astro CLI + MongoDB)

A daily Airflow pipeline that pulls exchange rates from the
[Frankfurter API](https://frankfurter.dev/), reshapes them, and upserts them into MongoDB.
Mongo Express provides a web UI over the database.

```
Frankfurter API ──► extract_exchange_rates ──► transform_exchange_rates ──► load_exchange_rates ──► MongoDB
                    (XCom: raw_exchange_rates)  (XCom: transformed_exchange_rates)  (XCom: load_summary)
```

## Project structure

```
.
├── dags/
│   └── currency_etl_dag.py        # DAG: 3 PythonOperator tasks wired with named XComs
├── include/currency_etl/
│   ├── config.py                  # API + Mongo settings (env-overridable)
│   ├── extract.py                 # GET /v2/rates
│   ├── transform.py               # raw record -> required document schema
│   └── load.py                    # bulk upsert into MongoDB
├── docker/
│   ├── mongo/Dockerfile           # mongo:7.0 + metadata labels
│   └── mongo-express/Dockerfile   # mongo-express + metadata labels
├── tests/dags/test_currency_etl.py
├── Dockerfile                     # Astro Runtime image + metadata labels
├── docker-compose.override.yml    # adds mongo + mongo-express, network, volume
├── requirements.txt               # pymongo, requests
├── .env.example                   # copy to .env
└── airflow_settings.yaml
```

## Document schema

```json
{
  "base_currency": "EUR",
  "target_currency": "USD",
  "exchange_rate": 1.15,
  "rate_date": "2026-11-04",
  "source": "Frankfurter API",
  "retrieved_at": "2026-11-05T07:15:00"
}
```

A unique index on `(base_currency, target_currency, rate_date)` plus upserts makes reruns idempotent.

## Run it

Requirements: Docker Desktop and the [Astro CLI](https://www.astronomer.io/docs/astro/cli/install-cli).

```bash
cp .env.example .env
# Astro does not build images listed in docker-compose.override.yml, so build these once:
docker build -t currency-etl/mongo:1.0.0 docker/mongo
docker build -t currency-etl/mongo-express:1.0.0 docker/mongo-express
astro dev start
```

| Service | URL | Login |
|---------|-----|-------|
| Airflow UI | http://localhost:8080 | none locally (`admin`/`admin` if prompted) |
| Mongo Express | http://localhost:8081 | `admin` / `admin123` |
| MongoDB | `mongodb://admin:admin123@localhost:27017` | |

Unpause and trigger `currency_exchange_etl` in the Airflow UI, then browse
`currency_db > exchange_rates` in Mongo Express.

Tests: `astro dev pytest`. Stop: `astro dev stop` (data stays in the `currency_etl_mongo_data` volume).

## Docker details

- **Metadata:** every image carries OCI `LABEL`s (title, description, version, authors, component).
  Check with `docker inspect --format "{{json .Config.Labels}}" currency-etl/mongo:1.0.0`.
- **Networking:** MongoDB and Mongo Express join Astro's `airflow` bridge network, so tasks reach
  the database at hostname `mongo` and Mongo Express reaches it the same way.
- **Persistent storage:** MongoDB's `/data/db` is mounted on the named volume `currency_etl_mongo_data`.
