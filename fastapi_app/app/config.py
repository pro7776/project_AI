import os
from dataclasses import dataclass


@dataclass
class Config:
    database_url: str = os.environ.get(
        'DATABASE_URL', 'postgresql://bookuser:bookpass@db:5432/bookdb')
    debug: bool = os.environ.get('DEBUG', 'False').lower() == 'true'
    model_name: str = 'paraphrase-multilingual-MiniLM-L12-v2'


config = Config()
