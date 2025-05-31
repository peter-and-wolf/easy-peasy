import os

from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import AnyHttpUrl, BaseModel
from pydantic_settings.sources import PydanticBaseSettingsSource, EnvSettingsSource
from pydantic.fields import FieldInfo
from typing import Any


class MyCustomSource(EnvSettingsSource):
  def prepare_field_value(
    self, 
    field_name: str, 
    field: FieldInfo, 
    value: Any, 
    value_is_complex: bool
  ) -> Any:
    print(os.getenv("GOOGLE_CREDENTIALS_PATH"))
    return value


class GoogleCredentials(BaseModel):
  client_id: str
  project_id: str
  auth_uri: str
  token_uri: str
  auth_provider_x509_cert_url: str
  client_secret: str
    

class Settings(BaseSettings):
  zimbra_user: str | None = None
  zimbra_password: str | None = None
  zimbra_url: AnyHttpUrl | None = None
  server_host: str = "0.0.0.0"
  server_port: int = 8999
  starlette_secret_key: str | None = None
  google_credentials_path: str | None = None
    
  model_config = SettingsConfigDict(
    env_file=".env",
    env_file_encoding="utf-8",
    extra="ignore"
  )

  @classmethod
  def settings_customise_sources(
    cls, 
    settings_cls: type[BaseSettings], 
    init_settings: PydanticBaseSettingsSource, 
    env_settings: PydanticBaseSettingsSource, 
    dotenv_settings: PydanticBaseSettingsSource, 
    file_secret_settings: PydanticBaseSettingsSource) -> tuple[PydanticBaseSettingsSource, ...]:
    
    s = MyCustomSource(settings_cls)
    
    return (s,)

settings = Settings()
