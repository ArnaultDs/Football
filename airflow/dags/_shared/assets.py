from airflow.sdk import dag, task, Asset

raw_updated = Asset("football_raw")