from pydantic_settings import BaseSettings

# BaseSettings replaces scattered os.environ calls with one validated object
class Settings(BaseSettings):
    app_name: str = "PersoLens API"
    environment: str = "development"
    database_url: str
    youtube_api_key: str
    openai_api_key: str
    
    
    class Config:
        env_file = ".env"

settings = Settings()