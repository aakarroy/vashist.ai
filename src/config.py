from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    jina_api_key : str = ""
    log_level : str = "INFO"
    max_retries : int = 5
    cache_ttl_seconds : int = 300
    log_file_name : str = "logs.log"

    model_config = {"env_file" : ".env", "extra":"ignore"}

@lru_cache
def get_settings():
    return Settings()