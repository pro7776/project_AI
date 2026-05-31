import os
from dataclasses import dataclass


@dataclass
class Config:
    secret_key: str = os.environ.get('SECRET_KEY', 'dev-secret-key')
    database_url: str = os.environ.get('DATABASE_URL', '')
    ml_service_url: str = os.environ.get(
        'ML_SERVICE_URL', 'http://fastapi:8000')
    debug: bool = os.environ.get('DEBUG', 'False').lower() == 'true'


config = Config()
