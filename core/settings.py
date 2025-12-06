import os
from dataclasses import dataclass
from dotenv import load_dotenv

DEBUG = os.getenv('DEBUG', 'True').lower() == 'true'

load_dotenv('.env.dev' if DEBUG else '.env.prod')

@dataclass
class Settings:
    debug: bool = True
    port: int = 8001
    postgres_username: str = 'postgres'
    postgres_password: str = 'postgres'
    postgres_host: str = 'db'
    postgres_port: int = 5432
    postgres_db: str = 'trip_expenses'

    def __post_init__(self):
        self.debug = os.getenv('DEBUG', 'True').lower() == 'true'
        self.port = int(os.getenv('PORT', '8001'))

        required = [
            'POSTGRES_USERNAME',
            'POSTGRES_PASSWORD',
            'POSTGRES_HOST',
            'POSTGRES_PORT',
            'POSTGRES_DB',
        ]

        for var in required:
            value = os.getenv(var)
            if not value:
                raise ValueError(f"Missing required environment variable: {var}")
            if var == 'POSTGRES_PORT':
                setattr(self, var.lower(), int(value))
            else:
                setattr(self, var.lower(), value)

    def get_db_url(self):
        return f"postgresql+psycopg2://{self.postgres_username}:{self.postgres_password}@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"

def get_settings():
    return Settings()