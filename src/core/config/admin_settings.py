from pydantic_settings import BaseSettings, SettingsConfigDict


class AdminSettings(BaseSettings):
    ADMIN_EMAIL: str
    ADMIN_PASSWORD: str

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="allow")


admin_settings = AdminSettings()
