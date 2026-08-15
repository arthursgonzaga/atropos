from functools import lru_cache
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    octoprint_url: str = Field(min_length=1)
    octoprint_api_key: str = Field(min_length=1)
    synapse_url: str = Field(min_length=1)
    telegram_chat_id: str = Field(min_length=1)

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


@lru_cache
def get_settings() -> Settings:
    return Settings()
