cat > BLOCK_D_MONETIZATION/block_d/config.py << 'EOF'
"""
Конфигурация системы монетизации (Блок D)
"""

import os

class MonetizationConfig:
    # Тарифные планы
    TARIFF_PLANS = {
        'start': {
            'name': 'Стартовый',
            'price_monthly': 0,
            'leads_included': 10,
            'features': ['basic_dashboard', '10_leads', 'email_support'],
            'is_active': True,
            'is_default': True
        },
        'professional': {
            'name': 'Профессиональный',
            'price_monthly': 5000,
            'price_quarterly': 13500,
            'price_yearly': 48000,
            'leads_included': 100,
            'features': ['advanced_dashboard', '100_leads', 'priority_support', 'analytics'],
            'is_active': True,
            'is_default': False
        },
        'business': {
            'name': 'Бизнес',
            'price_monthly': 15000,
            'price_quarterly': 40500,
            'price_yearly': 144000,
            'leads_included': 1000,
            'features': ['full_dashboard', 'unlimited_leads', '24_7_support', 'api_access'],
            'is_active': True,
            'is_default': False
        }
    }
    
    # Уведомления
    NOTIFICATIONS = {
        'email': {
            'enabled': True,
            'smtp_server': 'smtp.gmail.com',
            'smtp_port': 587,
            'from_email': 'noreply@haus-price.ru'
        }
    }
    
    # Настройки счетов
    INVOICE = {
        'number_format': 'INV-{date}-{partner_id}-{seq:04d}',
        'due_days': 7,
        'company_details': {
            'name': 'HAUS Price Ecosystem',
            'inn': '1234567890',
            'address': 'г. Москва',
            'bank': 'ПАО Сбербанк'
        }
    }
    
    # Режимы
    TEST_MODE = True
    DEBUG = True
    
    @property
    def is_test_mode(self):
        return self.TEST_MODE

# Создаем глобальный экземпляр конфигурации
config = MonetizationConfig()
EOF
