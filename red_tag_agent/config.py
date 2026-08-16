from functools import lru_cache
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_prefix="RED_TAG_", extra="ignore")

    environment: str = "local"
    service_role: Literal["all", "api", "worker"] = "all"
    repository_backend: Literal["memory", "firestore"] = "memory"
    dispatch_backend: Literal["inline", "pubsub"] = "inline"
    agent_mode: Literal["local", "adk"] = "local"
    model: str = "gemini-3.6-flash"
    google_cloud_project: str | None = None
    # Gemini 3.6 Flash is served from the global model endpoint. This is
    # intentionally independent from the Cloud Run deployment region.
    google_cloud_location: str = "global"
    incident_topic: str = "red-tag-incident-created"


@lru_cache
def get_settings() -> Settings:
    return Settings()
