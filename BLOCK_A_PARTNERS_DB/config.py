import os

class Config:
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'postgresql://admin:admin123@postgres:5432/haus_partners')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

config = Config()

def load_config():
    return config

def get_database_url():
    return config.SQLALCHEMY_DATABASE_URI
