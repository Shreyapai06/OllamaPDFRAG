"""Application settings — sourced entirely from environment variables."""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # LLM provider — "groq" (default, used on Railway) or "ollama" (local dev)
    LLM_PROVIDER: str = "groq"

    # Groq — required when LLM_PROVIDER=groq
    GROQ_API_KEY: str = ""
    GROQ_CHAT_MODEL: str = "llama-3.3-70b-versatile"

    # Ollama — required when LLM_PROVIDER=ollama
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_CHAT_MODEL: str = "llama3.2"

    # Local embedding model (sentence-transformers, provider-independent)
    EMBEDDING_MODEL: str = "BAAI/bge-small-en-v1.5"

    # Agent
    MAX_AGENT_ITERATIONS: int = 1


settings = Settings()