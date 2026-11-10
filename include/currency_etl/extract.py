"""Extract step: fetch the latest exchange rates from the Frankfurter API."""

import logging

import requests

from include.currency_etl import config

log = logging.getLogger(__name__)


def fetch_rates(base: str = config.BASE_CURRENCY, quotes: str = config.TARGET_CURRENCIES) -> list[dict]:
    """Call GET /v2/rates?base=EUR&quotes=USD,GBP,...

    The API returns a list such as:
        [{"date": "2026-11-10", "base": "EUR", "quote": "USD", "rate": 1.1185}, ...]
    """
    url = f"{config.API_BASE_URL}/v2/rates"
    params = {"base": base, "quotes": quotes}
    log.info("Requesting %s with params %s", url, params)

    response = requests.get(url, params=params, timeout=config.REQUEST_TIMEOUT)
    response.raise_for_status()  # fail the task (and trigger a retry) on HTTP errors
    data = response.json()

    if not isinstance(data, list) or not data:
        raise ValueError(f"Unexpected API response: {data!r}")

    log.info("Received %d rates", len(data))
    return data
