"""Service settings, read from the environment (and a local .env file)."""

from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    backend_url: str = "http://localhost:8000"
    # Shared with the backend. Empty means every request to POST /runs is refused.
    discovery_service_token: str = ""
    backend_timeout_seconds: float = 10.0

    mistral_api_key: str = ""
    # get_chat_model(purpose): "small" classifies pages and picks links, "large" extracts.
    mistral_small_model: str = "mistral-small-latest"
    mistral_large_model: str = "mistral-medium-latest"
    # Model behind the web_search tool (tools/search.py).
    mistral_search_model: str = "mistral-medium-latest"
    llm_timeout_seconds: float = 60.0

    # Page fetching (tools/fetch.py).
    cache_dir: str = "./cache"
    cache_ttl_days: int = Field(default=30, ge=0)
    fetch_timeout_seconds: float = 15.0
    max_page_bytes: int = Field(default=3_000_000, ge=1)
    # Seconds between two requests to the same domain.
    per_domain_interval_seconds: float = Field(default=1.0, ge=0)
    user_agent: str = "clapp-discovery/0.1 (festival and venue research)"

    # Per-run limits.
    max_llm_calls: int = Field(default=80, ge=1)
    max_pages: int = Field(default=60, ge=1)
    max_searches: int = Field(default=15, ge=0)
    max_leads: int = Field(default=25, ge=0)
    max_hops_per_site: int = Field(default=3, ge=0)

    # LangSmith reads its own LANGSMITH_* variables; these are here so they show up in one place.
    langsmith_tracing: bool = False
    langsmith_api_key: str = ""
    langsmith_project: str = "clapp-discovery"


@lru_cache
def get_settings() -> Settings:
    return Settings()
