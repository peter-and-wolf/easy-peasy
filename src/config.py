import calendar
from pydantic_settings import BaseSettings, SettingsConfigDict

class SyncConfig(BaseSettings):
  db_file: str = "sync.db"

  model_config = SettingsConfigDict(
    env_prefix="SYNC_",
    env_file=".env",
    env_file_encoding="utf-8",
    extra="ignore"
  )


class ZimbraConfig(BaseSettings):
  user: str = ""
  password: str = ""
  calendar_name: str = "Calendar"
  url_template: str = "https://mail.bloomtech.ru/dav/{user}"
    
  model_config = SettingsConfigDict(
    env_prefix="ZIMBRA_",
    env_file=".env",
    env_file_encoding="utf-8",
    extra="ignore"
  )
  @property
  def url(self) -> str:
    return self.url_template.format(user=self.user)


class GoogleConfig(BaseSettings):
  user: str = ""
  token_file: str = "token.json"
  credentials_file: str = "google-calendar-creds.json"
  calendar_name: str = "Bloom"
  url_template: str = "https://apidata.googleusercontent.com/caldav/v2/{user}/events"
    
  model_config = SettingsConfigDict(
    env_prefix="GOOGLE_",
    env_file=".env",
    env_file_encoding="utf-8",
    extra="ignore"
  ) 
  @property
  def url(self) -> str:
    return self.url_template.format(user=self.user)


sync_config = SyncConfig() 
zimbra_config = ZimbraConfig() 
google_config = GoogleConfig()

