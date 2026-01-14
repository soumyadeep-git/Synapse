from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

class Settings(BaseSettings):
    PROJECT_NAME: str = "Synapse Ops Agent"
    API_V1_STR: str = "/api/v1"
    
    # Infrastructure
    DATABASE_URL: str
    CELERY_BROKER_URL: str
    CELERY_RESULT_BACKEND: str
    
    # AI Keys
    ANTHROPIC_API_KEY: str
    
    # Composio (Handles Jira, Slack, Github Auth)
    COMPOSIO_API_KEY: str

    # Load from .env file
    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True)


settings = Settings()