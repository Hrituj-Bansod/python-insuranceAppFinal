from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config=SettingsConfigDict(env_file="Core/.env")
    DB_URL: str
    SECRET_KEY: str
    ALGORITHM: str
    EMAIL: str
    PASSWORD: str
    SMTP_SERVER: str
    SMTP_PORT: int
    
settings = Settings()    
