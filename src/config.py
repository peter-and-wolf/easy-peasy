from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import AnyHttpUrl


class CalwatchConfig(BaseSettings):
  zimbra_user: str = ""
  zimbra_password: str = ""
  db_file: str = "calwatch.db"
  zimbra_url: AnyHttpUrl = AnyHttpUrl("https://mail.bloomtech.ru/dav/pemelyanov@bloomtech.ru")
    
  model_config = SettingsConfigDict(
    env_prefix="CALWATCH_",
    env_file=".env",
    env_file_encoding="utf-8",
    extra="ignore"
  )


calwatch_config = CalwatchConfig() 
