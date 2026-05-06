"""Application configuration loaded from environment variables."""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # LLM provider — set LLM_PROVIDER to "openai", "azure", or "anthropic"
    llm_provider: str = "openai"

    # OpenAI
    openai_api_key: str = ""
    openai_model: str = "gpt-4o"

    # Azure OpenAI
    azure_openai_api_key: str = ""
    azure_openai_endpoint: str = ""
    azure_openai_deployment: str = ""
    azure_openai_api_version: str = "2024-02-01"

    # Anthropic
    anthropic_api_key: str = ""
    anthropic_model: str = "claude-3-5-sonnet-20241022"

    # Map API (Google Maps or compatible)
    map_api_key: str = ""
    map_api_base_url: str = "https://maps.googleapis.com/maps/api"

    # Weather API (OpenWeatherMap or compatible)
    weather_api_key: str = ""
    weather_api_base_url: str = "https://api.openweathermap.org/data/2.5"

    # Agent behaviour
    agent_max_iterations: int = 10
    agent_verbose: bool = True

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
