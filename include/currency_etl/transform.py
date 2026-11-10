"""Transform step: reshape raw API records into the required document format."""

from datetime import datetime, timezone

from include.currency_etl import config


def transform_rates(raw_rates: list[dict], retrieved_at: str | None = None) -> list[dict]:
    """Convert raw API records into documents like:

    {
      "base_currency": "EUR",
      "target_currency": "USD",
      "exchange_rate": 1.15,
      "rate_date": "2026-11-04",
      "source": "Frankfurter API",
      "retrieved_at": "2026-11-05T07:15:00"
    }
    """
    if retrieved_at is None:
        retrieved_at = datetime.now(timezone.utc).replace(microsecond=0, tzinfo=None).isoformat()

    documents = []
    for record in raw_rates:
        rate = record.get("rate")
        if rate is None or record.get("quote") is None:
            continue  # skip incomplete records

        documents.append(
            {
                "base_currency": str(record["base"]).upper(),
                "target_currency": str(record["quote"]).upper(),
                "exchange_rate": round(float(rate), 6),
                "rate_date": str(record["date"]),
                "source": config.SOURCE_NAME,
                "retrieved_at": retrieved_at,
            }
        )

    if not documents:
        raise ValueError("Transformation produced no documents")
    return documents
