"""Application settings — sourced entirely from environment variables."""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # Groq
    GROQ_API_KEY: str
    GROQ_CHAT_MODEL: str = "llama-3.3-70b-versatile"

    # Local embedding model (sentence-transformers)
    EMBEDDING_MODEL: str = "BAAI/bge-small-en-v1.5"

    # Agent
    MAX_AGENT_ITERATIONS: int = 1


settings = Settings()
