from pathlib import Path

from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).parent.parent


class DbConfig(BaseModel):
    echo: bool = False
    dialect: str = "postgresql"
    engine: str = "asyncpg"
    host: str
    port: int

    user: str
    password: str
    database: str

    @property
    def url(self) -> str:
        return f"{self.dialect}+{self.engine}://{self.user}:{self.password}@{self.host}:{self.port}/{self.database}"

    @property
    def sync_url(self) -> str:
        return f"{self.dialect}+psycopg://{self.user}:{self.password}@{self.host}:{self.port}/{self.database}"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="WALLET__APP__",
        env_nested_delimiter="__",
        case_sensitive=False,
        env_file=(
            BASE_DIR / ".env.template",
            BASE_DIR / ".env",
        ),
    )
    db: DbConfig


# noinspection PyArgumentList
settings = Settings()

if __name__ == "__main__":
    print(BASE_DIR)
    print(settings.model_dump_json(indent=2))
