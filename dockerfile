FROM apache/airflow:3.3.0-python3.12

COPY --chown=airflow:root pyproject.toml README.md ./
COPY --chown=airflow:root src/ ./src/

RUN pip install --no-cache-dir \
      "apache-airflow==${AIRFLOW_VERSION}" . \
      --constraint "https://raw.githubusercontent.com/apache/airflow/constraints-${AIRFLOW_VERSION}/constraints-3.12.txt"

RUN python -m venv /home/airflow/dbt-venv \
 && /home/airflow/dbt-venv/bin/pip install --no-cache-dir "dbt-core<1.12" dbt-postgres