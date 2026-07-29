from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str

    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1800

    OPENAI_API_KEY: str = ""
    OPENAI_BASE_URL: str = "https://api.openai.com/v1"
    OLLAMA_BASE_URL: str = "http://localhost:11434"

    LLM_PROVIDER: str = "ollama"
    LLM_MODEL: str = "llama3"

    EMBEDDING_PROVIDER: str = "openai-proxy"
    EMBEDDING_MODEL: str = "kgpt-text-embedding"
    EMBEDDING_BASE_URL: str = "https://llm-proxy.kpit.com/v1/embeddings"
    EMBEDDING_VECTOR_SIZE: int = 1536

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()