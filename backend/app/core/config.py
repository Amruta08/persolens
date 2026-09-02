from pydantic_settings import BaseSettings

# BaseSettings replaces scattered os.environ calls with one validated object
class Settings(BaseSettings):
    app_name: str = "PersoLens API"
    environment: str = "development"
    
    class Config:
        env_file = ".env"

settings = Settings()