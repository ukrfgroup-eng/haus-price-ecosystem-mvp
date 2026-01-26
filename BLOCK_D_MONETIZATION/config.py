cat > config.py << 'EOF'
"""
Конфигурация системы монетизации (Блок D)
"""

import os
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()

class MonetizationConfig:
    # ============ ПЛАТЕЖНЫЕ СИСТЕМЫ ============
    YOOKASSA_SHOP_ID = os.getenv('YOOKASSA_SHOP_ID', 'test_shop_id')
    YOOKASSA_SECRET_KEY = os.getenv('YOOKASSA_SECRET_KEY', 'test_secret_key')
    YOOKASSA_WEBHOOK_URL = os.getenv('YOOKASSA_WEBHOOK_URL', '')
    YOOKASSA_RETURN_URL = os.getenv('YOOKASSA_RETURN_URL', '')
    
    TINKOFF_TERMINAL_KEY = os.getenv('TINKOFF_TERMINAL_KEY', '')
    TINKOFF_PASSWORD = os.getenv('TINKOFF_PASSWORD', '')
    TINKOFF_API_URL = 'https://securepay.tinkoff.ru/v2/'
    
    # ============ ТАРИФНЫЕ ПЛАНЫ ============
    TARIFF_PLANS = {
        'start': {
            'code': 'start',
            'name': 'Стартовый',
            'description': 'Базовый доступ для новых партнеров',
            'price_monthly': 0,
            'price_quarterly': 0,
            'price_yearly': 0,
            'currency': 'RUB',
            'leads_included': 10,
            'features': [
                'basic_dashboard',
                '10_leads_per_month',
                'email_support',
                'basic_analytics'
            ],
            'is_active': True,
            'is_default': True
        },
        'professional': {
            'code': 'professional',
            'name': 'Профессиональный',
            'description': 'Для активно работающих партнеров',
            'price_monthly': 5000,
            'price_quarterly': 13500,  # 10% скидка
            'price_yearly': 48000,     # 20% скидка
            'currency': 'RUB',
            'leads_included': 100,
            'features': [
                'advanced_dashboard',
                '100_leads_per_month',
                'priority_support',
                'advanced_analytics',
                'api_access',
                'custom_reports'
            ],
            'is_active': True,
            'is_default': False
        },
        'business': {
            'code': 'business',
            'name': 'Бизнес',
            'description': 'Для крупных партнеров и агентств',
            'price_monthly': 15000,
            'price_quarterly': 40500,  # 10% скидка
            'price_yearly': 144000,    # 20% скидка
            'currency': 'RUB',
            'leads_included': 1000,
            'features': [
                'full_dashboard',
                'unlimited_leads',
                '24_7_support',
                'premium_analytics',
                'full_api_access',
                'white_label',
                'dedicated_manager'
            ],
            'is_active': True,
            'is_default': False
        }
    }
    
    # ============ НАСТРОЙКИ СЧЕТОВ ============
    INVOICE = {
        'number_format': 'INV-{date}-{partner_id}-{seq:04d}',
        'due_days': 7,
        'company_details': {
            'name': 'HAUS Price Ecosystem',
            'legal_name': 'ООО "ХАУС Прайс"',
            'inn': '1234567890',
            'kpp': '123456789',
            'ogrn': '1234567890123',
            'address': 'г. Москва, ул. Примерная, д. 1',
            'bank_name': 'ПАО Сбербанк',
            'bank_bik': '044525225',
            'bank_account': '40702810123450123456',
            'bank_corr_account': '30101810400000000225',
            'ceo': 'Иванов Иван Иванович'
        }
    }
    
    # ============ УВЕДОМЛЕНИЯ ============
    NOTIFICATIONS = {
        'email': {
            'enabled': True,
            'smtp_server': os.getenv('SMTP_SERVER', 'smtp.gmail.com'),
            'smtp_port': int(os.getenv('SMTP_PORT', 587)),
            'smtp_username': os.getenv('SMTP_USERNAME', ''),
            'smtp_password': os.getenv('SMTP_PASSWORD', ''),
            'from_email': os.getenv('FROM_EMAIL', 'noreply@haus-price.ru'),
            'from_name': 'HAUS Price Ecosystem'
        },
        'telegram': {
            'enabled': False,
            'bot_token': os.getenv('TELEGRAM_BOT_TOKEN', ''),
            'admin_chat_id': os.getenv('ADMIN_TELEGRAM_CHAT_ID', ''),
            'notify_on_payment': True,
            'notify_on_refund': True,
            'notify_on_subscription': True
        },
        'sms': {
            'enabled': False,
            'provider': os.getenv('SMS_PROVIDER', ''),
            'api_key': os.getenv('SMS_API_KEY', ''),
            'sender': os.getenv('SMS_SENDER', 'HAUS')
        }
    }
    
    # ============ АНАЛИТИКА ============
    ANALYTICS = {
        'calculate_daily': True,
        'calculate_weekly': True,
        'calculate_monthly': True,
        'forecast_months': 3,
        'churn_window_days': 30,
        'retention_periods': [7, 30, 90, 180, 365]
    }
    
    # ============ БАЗА ДАННЫХ ============
    DATABASE = {
        'url': os.getenv('DATABASE_URL', 'sqlite:///monetization.db'),
        'pool_size': 10,
        'max_overflow': 20,
        'echo': False
    }
    
    # ============ БЕЗОПАСНОСТЬ ============
    SECURITY = {
        'webhook_secret': os.getenv('WEBHOOK_SECRET', ''),
        'api_key_header': 'X-API-Key',
        'rate_limit_per_minute': 60,
        'jwt_secret': os.getenv('JWT_SECRET', ''),
        'jwt_expire_hours': 24
    }
    
    # ============ ДРУГИЕ НАСТРОЙКИ ============
    DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'
    TEST_MODE = os.getenv('TEST_MODE', 'False').lower() == 'true'
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    
    @property
    def is_production(self):
        return os.getenv('ENVIRONMENT', 'development') == 'production'
    
    @property
    def is_development(self):
        return os.getenv('ENVIRONMENT', 'development') == 'development'
    
    def get_tariff(self, tariff_code):
        """Получить тариф по коду"""
        return self.TARIFF_PLANS.get(tariff_code)
    
    def validate_config(self):
        """Валидация конфигурации"""
        errors = []
        
        if self.is_production and not self.YOOKASSA_SHOP_ID:
            errors.append("YOOKASSA_SHOP_ID не установлен для production")
        
        if self.NOTIFICATIONS['email']['enabled'] and not self.NOTIFICATIONS['email']['smtp_username']:
            errors.append("SMTP username не установлен")
        
        return errors

# Создаем глобальный экземпляр конфигурации
config = MonetizationConfig()
EOF
