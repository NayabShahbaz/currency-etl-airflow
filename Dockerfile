FROM astrocrpublic.azurecr.io/runtime:3.3-12

# ---- Image metadata (OCI labels) ----
LABEL org.opencontainers.image.title="currency-etl-airflow" \
      org.opencontainers.image.description="Airflow (Astro Runtime) image for the daily currency exchange-rate ETL pipeline" \
      org.opencontainers.image.version="1.0.0" \
      org.opencontainers.image.authors="Nayab Shahbaz <nayab.shahbaz003@gmail.com>" \
      org.opencontainers.image.source="https://github.com/NayabShahbaz/currency-etl-airflow" \
      project="Task 3 - Airflow ETL Pipeline" \
      component="orchestrator"
