"""Load step: upsert transformed documents into MongoDB."""

import logging

from pymongo import ASCENDING, MongoClient, UpdateOne

from include.currency_etl import config

log = logging.getLogger(__name__)


def load_rates(documents: list[dict]) -> dict:
    """Upsert one document per (base_currency, target_currency, rate_date).

    Upserting makes the task idempotent: re-running the DAG for the same day
    updates the existing rows instead of inserting duplicates.
    """
    client = MongoClient(config.MONGO_URI, serverSelectionTimeoutMS=10_000)
    try:
        collection = client[config.MONGO_DB][config.MONGO_COLLECTION]
        collection.create_index(
            [("base_currency", ASCENDING), ("target_currency", ASCENDING), ("rate_date", ASCENDING)],
            unique=True,
            name="uniq_pair_per_day",
        )

        operations = [
            UpdateOne(
                {
                    "base_currency": doc["base_currency"],
                    "target_currency": doc["target_currency"],
                    "rate_date": doc["rate_date"],
                },
                {"$set": doc},
                upsert=True,
            )
            for doc in documents
        ]
        result = collection.bulk_write(operations)

        summary = {
            "inserted": result.upserted_count,
            "updated": result.modified_count,
            "matched": result.matched_count,
            "total_in_collection": collection.count_documents({}),
        }
        log.info("Load summary: %s", summary)
        return summary
    finally:
        client.close()
