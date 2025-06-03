from pydantic_settings import BaseSettings, SettingsConfigDict

class CalwatchConfig(BaseSettings):
  db_file: str = "calwatch.db"

  model_config = SettingsConfigDict(
    env_prefix="CALWATCH_",
    env_file=".env",
    env_file_encoding="utf-8",
    extra="ignore"
  )


class ZimbraConfig(BaseSettings):
  user: str = ""
  password: str = ""
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


calwatch_config = CalwatchConfig() 
zimbra_config = ZimbraConfig() 
google_config = GoogleConfig()

