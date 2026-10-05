from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings): 
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # RapidApi
    rapid_api_base_url: str
    x_rapidapi_key: str
    x_rapidapi_host: str = "api-football-v1.p.rapidapi.com"

    # footballApi
    football_api_base_url: str
    x_apisports_key: str 

    # Postgres
    postgres_host: str = "localhost"
    postgres_port: int = 5432
    postgres_db: str = "football"
    postgres_user: str
    postgres_password: str 

    # Minio
    minio_pipeline_access_key: str
    minio_pipeline_secret_key: str 
    minio_bronze_bucket: str
    minio_silver_bucket: str
    minio_endpoint_url: str = "http://localhost:9000"

    @property
    def postgres_database_url(self) -> str: 
        return (
            f"postgresql+psycopg://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )



settings = Settings()  # pyright: ignore[reportCallIssue]