"""Central configuration. Values can be overridden with environment variables (see .env)."""

import os

# Frankfurter API
API_BASE_URL = os.getenv("FRANKFURTER_API_URL", "https://api.frankfurter.dev")
BASE_CURRENCY = os.getenv("BASE_CURRENCY", "EUR")
TARGET_CURRENCIES = os.getenv("TARGET_CURRENCIES", "USD,GBP,JPY,CHF,AUD,CAD")
SOURCE_NAME = "Frankfurter API"
REQUEST_TIMEOUT = 30  # seconds

# MongoDB ("mongo" is the service name inside the Docker network)
MONGO_URI = os.getenv("MONGO_URI", "mongodb://admin:admin123@mongo:27017/?authSource=admin")
MONGO_DB = os.getenv("MONGO_DB", "currency_db")
MONGO_COLLECTION = os.getenv("MONGO_COLLECTION", "exchange_rates")
