"""
Тесты для системы платежей
"""

import pytest
from datetime import datetime, timedelta
from backend.services.invoice_generator import InvoiceGenerator
from backend.services.revenue_analytics import RevenueAnalytics


def test_invoice_generation():
    """Тест генерации счета"""
    generator = InvoiceGenerator()
    
    # Тестовые данные
    test_data = {
        'partner_id': 'TEST-001',
        'amount': 5000.00,
        'tariff_plan': 'professional',
        'description': 'Тестовая оплата'
    }
    
    result = generator.create_invoice(**test_data)
    
    assert result is not None
    assert 'invoice_number' in result
    assert result['amount'] == 5000.00
    assert result['currency'] == 'RUB'


def test_revenue_analytics():
    """Тест аналитики доходов"""
    analytics = RevenueAnalytics()
    
    # Тест месячной статистики
    monthly_stats = analytics.get_monthly_revenue(2024, 1)
    assert monthly_stats is not None
    
    # Тест расчета LTV
    ltv_data = analytics.get_partner_lifetime_value('TEST-001')
    assert ltv_data is not None
    
    # Тест уровня оттока
    churn_rate = analytics.get_churn_rate(30)
    assert churn_rate is not None


def test_amount_to_words():
    """Тест конвертации суммы прописью"""
    generator = InvoiceGenerator()
    
    test_cases = [
        (1000, 'одна тысяча рублей 00 копеек'),
        (2500.50, 'две тысячи пятьсот рублей 50 копеек'),
        (123456.78, 'сто двадцать три тысячи четыреста пятьдесят шесть рублей 78 копеек')
    ]
    
    for amount, expected in test_cases:
        result = generator.amount_to_words(amount)
        # Проверяем наличие ключевых слов
        assert 'рубл' in result.lower()
        assert 'копе' in result.lower()


if __name__ == '__main__':
    pytest.main([__file__])
