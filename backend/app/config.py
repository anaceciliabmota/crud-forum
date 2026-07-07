from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env")

    database_url: str = "postgresql://forum_user:forum_pass@localhost:5432/forum_db"
    secret_key: str = "change-me-to-a-random-secret-key"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 24
    admin_email: str = "admin@forum.com"
    admin_password: str = "admin123"
    admin_nome: str = "Administrador"


settings = Settings()
