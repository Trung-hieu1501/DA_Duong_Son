import os
from datetime import timedelta

SQLALCHEMY_DATABASE_URI = os.getenv(
    'SUPERSET_METADATA_DB_URI',
    'sqlite:////app/superset_home/superset.db' 
)

SECRET_KEY = os.getenv('SUPERSET_SECRET_KEY', 'DCXpM4EBG1H2o9WUsww4E3rWt5EjNzFjHpNUhxgiH_0=')

RESULTS_BACKEND = 'redis://redis:6379/1'
CACHE_CONFIG = {
    'CACHE_TYPE': 'RedisCache',
    'CACHE_DEFAULT_TIMEOUT': 300,
    'CACHE_KEY_PREFIX': 'superset_',
    'CACHE_REDIS_URL': 'redis://redis:6379/0',
}

PERMANENT_SESSION_LIFETIME = timedelta(hours=12)
SESSION_PERMANENT = True