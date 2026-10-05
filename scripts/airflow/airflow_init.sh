#!/bin/bash
# Initialise Airflow au démarrage :
# - crée les dossiers partagés (logs/dags/plugins/config) si absents
# - applique les migrations DB
# - crée l'utilisateur admin (idempotent : ne casse rien si déjà existant)

set -eu

echo "Creating missing opt dirs if missing:"
mkdir -v -p /opt/airflow/{logs,dags,plugins,config}

echo "Airflow version:"
/entrypoint airflow version

echo "Running airflow config list to create default config file if missing."
/entrypoint airflow config list >/dev/null

echo "Change ownership of files in /opt/airflow to ${AIRFLOW_UID:-50000}:0"
chown -R "${AIRFLOW_UID:-50000}:0" /opt/airflow/

echo "Running airflow db migrate"
/entrypoint airflow db migrate

echo "Creating admin user (skip if already exists)"
if /entrypoint airflow users list | grep -qw "${AIRFLOW_USER}"; then
  echo "User $AIRFLOW_USER already exists, skipping."
else
  /entrypoint airflow users create \
    --username "$AIRFLOW_USER" \
    --password "$AIRFLOW_PASSWORD" \
    --firstname Admin \
    --lastname Admin \
    --role Admin \
    --email "${AIRFLOW_ADMIN_EMAIL:-admin@example.com}"
fi

echo "Installing dbt packages"
cd /opt/dbt/football_dbt && /home/airflow/dbt-venv/bin/dbt deps

echo "Airflow init done."