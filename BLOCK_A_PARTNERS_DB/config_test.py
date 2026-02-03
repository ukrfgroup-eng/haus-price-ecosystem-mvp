import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'postgresql://admin:password@localhost:5432/haus_price'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Настройки для блока A
    PARTNER_VERIFICATION_TIMEOUT = 30  # секунд
    MAX_DOCUMENTS_PER_PARTNER = 10
    DEFAULT_PARTNER_STATUS = 'pending'
    
    # S3 настройки (для теста используем заглушки)
    S3_ENDPOINT = os.environ.get('S3_ENDPOINT', 'https://storage.yandexcloud.net')
    S3_ACCESS_KEY = os.environ.get('S3_ACCESS_KEY', 'test_key')
    S3_SECRET_KEY = os.environ.get('S3_SECRET_KEY', 'test_secret')
    S3_BUCKET = os.environ.get('S3_BUCKET', 'haus-price-documents')
