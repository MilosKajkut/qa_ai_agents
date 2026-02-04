from pydantic import HttpUrl, SecretStr, Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from dotenv import load_dotenv

load_dotenv()


class OpenAISettings(BaseSettings):
    api_key: SecretStr = Field(validation_alias="OPENAI_API_KEY")
    model: str = Field(default="gpt-4.1-nano", validation_alias="LLM_MODEL")


class AtlassianSettings(BaseSettings):
    confluence_url: HttpUrl = Field(validation_alias="CONFLUENCE_URL")
    confluence_username: str = Field(validation_alias="CONFLUENCE_USERNAME")
    confluence_api_token: SecretStr = Field(validation_alias="CONFLUENCE_API_TOKEN")

    jira_url: HttpUrl = Field(validation_alias="JIRA_URL")
    jira_username: str = Field(validation_alias="JIRA_USERNAME")
    jira_api_token: SecretStr = Field(validation_alias="JIRA_API_TOKEN")


class VectorDBSettings(BaseSettings):
    collection_name: str = Field(validation_alias="COLLECTION_NAME")


class PlaywrightSettings(BaseSettings):
    root_dir_name: str = Field(validation_alias="ROOT_DIR_NAME")


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file_encoding="utf-8",
        extra="ignore"
    )

    openai: OpenAISettings = Field(default_factory=OpenAISettings)
    atlassian: AtlassianSettings = Field(default_factory=AtlassianSettings)
    vector_db: VectorDBSettings = Field(default_factory=VectorDBSettings)
    playwright: PlaywrightSettings = Field(default_factory=PlaywrightSettings)

    mcp_very_verbose: bool = Field(default=True, validation_alias="MCP_VERY_VERBOSE")
    mcp_logging_stdout: bool = Field(default=True, validation_alias="MCP_LOGGING_STDOUT")


# Instantiate once to be used across the project
settings = Settings()