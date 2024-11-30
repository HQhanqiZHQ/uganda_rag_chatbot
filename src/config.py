from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    OPENAI_API_KEY: str
    LM_STUDIO_URL: str = "http://localhost:1234"
    CHROMA_HOST: str = "localhost"
    CHROMA_PORT: int = 8080
    DATA_PATH: str = "data/raw/combined_text.txt"
    RESET_COLLECTION: bool = False
    EMBEDDING_MODEL: str = "nomic-embed-text-v1.5"  # Add this line
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
# print(f"Loaded API key is: {settings.OPENAI_API_KEY}...")