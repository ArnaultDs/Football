CREATE DATABASE metabase;

CREATE DATABASE airflow;

CREATE USER airflow_user WITH PASSWORD 'airflowUser';
ALTER DATABASE airflow OWNER TO airflow_user;
GRANT ALL PRIVILEGES ON DATABASE airflow TO airflow_user;

\c airflow
GRANT ALL ON SCHEMA public TO airflow_user;