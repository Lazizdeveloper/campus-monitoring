from typing import List, Optional
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    bot_token: str = Field(default="", description="Telegram Bot Token from @BotFather")
    school21_api_url: str = Field(
        default="https://platform.21-school.ru/services/21-school/api",
        description="Base URL for School 21 API",
    )
    school21_token: str = Field(
        default="",
        description="School 21 Authorization API/JWT token",
    )
    default_campus_id: Optional[str] = Field(
        default=None,
        description="Default campus UUID",
    )
    admin_ids: List[int] = Field(
        default_factory=list,
        description="List of admin Telegram user IDs",
    )
    check_sales_interval_minutes: int = Field(
        default=5,
        description="Sales check interval for background monitoring",
    )
    check_events_interval_minutes: int = Field(
        default=30,
        description="Events check interval for background monitoring",
    )

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
