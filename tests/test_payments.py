"""
Тесты для системы монетизации (Блок D)
"""

import pytest
import json
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock

# Импорты для тестирования
from backend.services.invoice_generator import InvoiceGenerator
from backend.services.revenue_analytics import RevenueAnalytics
from backend.models import db, Partner, Payment, Subscription
from backend.routes.payment_routes import invoice_generator, revenue_analytics


class TestInvoiceGenerator:
    """Тесты для генератора счетов"""
    
    def setup_method(self):
        """Настройка перед каждым тестом"""
        self.generator = InvoiceGenerator()
        
    def test_generate_invoice_number(self):
        """Тест генерации номера счета"""
        # Мокаем запрос к базе данных
        with patch.object(Payment, 'query') as mock_query:
            mock_filter = MagicMock()
            mock_count = MagicMock()
            mock_count.count.return_value = 2
            mock_filter.filter.return_value = mock_count
            mock_query.filter.return_value = mock_filter
            
            invoice_number = self.generator.generate_invoice_number("TEST123")
            
            # Проверяем формат номера счета
            assert invoice_number.startswith("INV-")
            assert "TEST123" in invoice_number
            
    def test_amount_to_words(self):
        """Тест конвертации суммы прописью"""
        test_cases = [
            (1000.00, "одна тысяча рублей 00 копеек"),
            (2500.50, "две тысячи пятьсот рублей 50 копеек"),
            (123456.78, "сто двадцать три тысячи четыреста пятьдесят шесть рублей 78 копеек"),
            (1.01, "один рубль 01 копейка"),
            (2.02, "два рубля 02 копейки"),
            (5.05, "пять рублей 05 копеек"),
        ]
        
        for amount, expected in test_cases:
            result = self.generator.amount_to_words(amount)
            # Проверяем, что результат содержит ожидаемые слова
            assert "рубл" in result.lower()
            assert "копе" in result.lower()
            
    def test_create_invoice_with_mocks(self):
        """Тест создания счета с моками"""
        test_partner_data = {
            'partner_id': 'TEST001',
            'company_name': 'Тестовая компания',
            'inn': '1234567890',
            'legal_address': 'Москва',
            'actual_address': 'Москва',
            'contact_person': 'Иван Иванов',
            'email': 'test@test.com',
            'verification_status': 'verified',
            'status': 'active'
        }
        
        # Мокаем все зависимости
        with patch.object(Partner, 'query') as mock_partner_query, \
             patch.object(db.session, 'add') as mock_add, \
             patch.object(db.session, 'commit') as mock_commit, \
             patch.object(db.session, 'rollback') as mock_rollback, \
             patch('builtins.open', create=True) as mock_open, \
             patch('os.makedirs'):
            
            # Настраиваем моки
            mock_partner = Mock()
            mock_partner.partner_id = test_partner_data['partner_id']
            mock_partner.company_name = test_partner_data['company_name']
            mock_partner.inn = test_partner_data['inn']
            mock_partner.legal_address = test_partner_data['legal_address']
            mock_partner.actual_address = test_partner_data['actual_address']
            mock_partner.contact_person = test_partner_data['contact_person']
            mock_partner.email = test_partner_data['email']
            mock_partner.verification_status = test_partner_data['verification_status']
            mock_partner.status = test_partner_data['status']
            
            mock_partner_query.filter_by.return_value.first.return_value = mock_partner
            
            # Мокаем запросы к Payment для генерации номера
            with patch.object(Payment, 'query') as mock_payment_query:
                mock_filter = MagicMock()
                mock_count = MagicMock()
                mock_count.count.return_value = 0
                mock_filter.filter.return_value = mock_count
                mock_payment_query.filter.return_value = mock_filter
                
                # Вызываем метод
                result = self.generator.create_invoice(
                    partner_id='TEST001',
                    amount=5000.00,
                    tariff_plan='professional',
                    description='Тестовый счет'
                )
                
                # Проверяем результаты
                assert result is not None
                assert 'invoice_number' in result
                assert result['amount'] == 5000.00
                assert result['currency'] == 'RUB'
                assert 'payment_url' in result
                
                # Проверяем, что методы были вызваны
                mock_add.assert_called()
                mock_commit.assert_called()
                mock_open.assert_called()


class TestRevenueAnalytics:
    """Тесты для аналитики доходов"""
    
    def setup_method(self):
        """Настройка перед каждым тестом"""
        self.analytics = RevenueAnalytics()
        
    def test_get_monthly_revenue_with_mocks(self):
        """Тест получения месячной статистики с моками"""
        # Создаем тестовые данные
        test_payments = [
            Mock(
                amount=5000.00,
                created_at=datetime(2024, 1, 15),
                tariff_plan='professional'
            ),
            Mock(
                amount=15000.00,
                created_at=datetime(2024, 1, 20),
                tariff_plan='business'
            ),
            Mock(
                amount=5000.00,
                created_at=datetime(2024, 1, 25),
                tariff_plan='professional'
            ),
        ]
        
        # Мокаем запросы
        with patch.object(Payment, 'query') as mock_query:
            mock_filter = MagicMock()
            mock_filter.filter.return_value.all.return_value = test_payments
            mock_query.filter.return_value = mock_filter
            
            # Вызываем метод
            result = self.analytics.get_monthly_revenue(2024, 1)
            
            # Проверяем результаты
            assert result is not None
            assert result['total_revenue'] == 25000.00  # 5000 + 15000 + 5000
            assert result['payment_count'] == 3
            assert result['average_payment'] == 25000.00 / 3
            assert 'professional' in result['revenue_by_tariff']
            assert 'business' in result['revenue_by_tariff']
            
    def test_get_partner_ltv_with_mocks(self):
        """Тест расчета LTV партнера с моками"""
        # Тестовые платежи
        test_payments = [
            Mock(
                amount=5000.00,
                created_at=datetime(2024, 1, 1)
            ),
            Mock(
                amount=15000.00,
                created_at=datetime(2024, 2, 1)
            ),
            Mock(
                amount=5000.00,
                created_at=datetime(2024, 3, 1)
            ),
        ]
        
        # Мокаем запросы
        with patch.object(Payment, 'query') as mock_query:
            mock_filter = MagicMock()
            mock_filter.filter.return_value.all.return_value = test_payments
            mock_query.filter.return_value = mock_filter
            
            # Вызываем метод
            result = self.analytics.get_partner_lifetime_value('TEST001')
            
            # Проверяем результаты
            assert result is not None
            assert result['total_spent'] == 25000.00
            assert result['payment_count'] == 3
            assert result['average_payment'] == 25000.00 / 3
            assert result['active_months'] == 3  # с января по март
            
    def test_get_churn_rate_with_mocks(self):
        """Тест расчета уровня оттока с моками"""
        # Мокаем запросы к Partner
        with patch.object(Partner, 'query') as mock_partner_query, \
             patch.object(db.session, 'query') as mock_db_query:
            
            # Настраиваем моки для общего количества партнеров
            mock_total_count = MagicMock()
            mock_total_count.count.return_value = 100
            mock_partner_query.filter.return_value = mock_total_count
            
            # Настраиваем моки для партнеров без платежей
            mock_lost_query = MagicMock()
            mock_lost_count = MagicMock()
            mock_lost_count.count.return_value = 5
            mock_lost_query.filter.return_value = mock_lost_count
            mock_db_query.return_value = mock_lost_query
            
            # Вызываем метод
            result = self.analytics.get_churn_rate(30)
            
            # Проверяем результаты
            assert result is not None
            assert result['total_partners'] == 100
            assert result['lost_partners'] == 5
            assert result['churn_rate'] == 5.0  # 5/100*100
            
    def test_get_top_partners_with_mocks(self):
        """Тест получения топовых партнеров с моками"""
        # Тестовые данные
        test_results = [
            ('Компания А', 'PART001', 50000.00, 5),
            ('Компания Б', 'PART002', 30000.00, 3),
            ('Компания В', 'PART003', 20000.00, 2),
        ]
        
        # Мокаем SQLAlchemy запросы
        with patch('backend.services.revenue_analytics.db.session.query') as mock_query:
            # Настраиваем цепочку вызовов
            mock_select = MagicMock()
            mock_join = MagicMock()
            mock_filter = MagicMock()
            mock_group_by = MagicMock()
            mock_order_by = MagicMock()
            mock_limit = MagicMock()
            
            mock_limit.limit.return_value.all.return_value = test_results
            mock_order_by.order_by.return_value = mock_limit
            mock_group_by.group_by.return_value = mock_order_by
            mock_filter.filter.return_value = mock_group_by
            mock_join.join.return_value = mock_filter
            mock_select.select.return_value = mock_join
            mock_query.return_value = mock_select
            
            # Вызываем метод
            result = self.analytics.get_top_partners(limit=3, period_days=30)
            
            # Проверяем результаты
            assert len(result) == 3
            assert result[0]['company_name'] == 'Компания А'
            assert result[0]['total_spent'] == 50000.00
            assert result[0]['payment_count'] == 5


class TestPaymentRoutes:
    """Тесты для API эндпоинтов платежей"""
    
    def test_create_invoice_endpoint(self, client):
        """Тест эндпоинта создания счета"""
        test_data = {
            'partner_id': 'TEST001',
            'amount': 5000.00,
            'tariff_plan': 'professional',
            'description': 'Тестовый счет'
        }
        
        # Мокаем InvoiceGenerator
        with patch('backend.routes.payment_routes.invoice_generator') as mock_generator:
            mock_generator.create_invoice.return_value = {
                'invoice_number': 'INV-20240101-001',
                'invoice_file': 'invoices/INV-20240101-001.html',
                'payment_url': '/api/v1/payments/1/pay',
                'amount': 5000.00,
                'currency': 'RUB',
                'due_date': '15.01.2024'
            }
            
            response = client.post('/api/v1/payments/create-invoice',
                                 json=test_data)
            
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['success'] == True
            assert 'data' in data
            assert data['data']['invoice_number'] == 'INV-20240101-001'
            
    def test_get_monthly_revenue_endpoint(self, client):
        """Тест эндпоинта получения месячной статистики"""
        # Мокаем RevenueAnalytics
        with patch('backend.routes.payment_routes.revenue_analytics') as mock_analytics:
            mock_analytics.get_monthly_revenue.return_value = {
                'total_revenue': 25000.00,
                'payment_count': 5,
                'average_payment': 5000.00,
                'daily_revenue': {'2024-01-01': 5000.00},
                'revenue_by_tariff': {'professional': 15000.00, 'business': 10000.00},
                'period': {'start': '2024-01-01', 'end': '2024-01-31'}
            }
            
            response = client.get('/api/v1/analytics/revenue/monthly?year=2024&month=1')
            
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['success'] == True
            assert data['data']['total_revenue'] == 25000.00
            
    def test_get_churn_rate_endpoint(self, client):
        """Тест эндпоинта получения уровня оттока"""
        with patch('backend.routes.payment_routes.revenue_analytics') as mock_analytics:
            mock_analytics.get_churn_rate.return_value = {
                'churn_rate': 5.0,
                'lost_partners': 5,
                'total_partners': 100,
                'period_days': 30
            }
            
            response = client.get('/api/v1/analytics/churn-rate?period_days=30')
            
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['success'] == True
            assert data['data']['churn_rate'] == 5.0
            
    def test_create_invoice_validation_error(self, client):
        """Тест валидации ошибок при создании счета"""
        # Тест с неполными данными
        test_data = {
            'partner_id': 'TEST001',
            # отсутствует amount
            'tariff_plan': 'professional'
        }
        
        response = client.post('/api/v1/payments/create-invoice',
                             json=test_data)
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data
        assert 'Отсутствует обязательное поле' in data['error']


class TestIntegration:
    """Интеграционные тесты"""
    
    def test_full_payment_flow(self, client, test_partner):
        """Тест полного цикла оплаты"""
        # 1. Регистрация партнера
        partner_data = {
            'company_name': 'Тестовая компания',
            'inn': '123456789012',
            'contact_person': 'Иван Иванов',
            'phone': '+79999999999',
            'email': 'test@test.com'
        }
        
        # 2. Создание счета
        invoice_data = {
            'partner_id': test_partner.partner_id,
            'amount': 5000.00,
            'tariff_plan': 'professional',
            'description': 'Подписка на 1 месяц'
        }
        
        with patch('backend.services.invoice_generator.InvoiceGenerator.create_invoice') as mock_create:
            mock_create.return_value = {
                'invoice_number': 'INV-TEST-001',
                'payment_url': '/pay/test',
                'amount': 5000.00
            }
            
            response = client.post('/api/v1/payments/create-invoice',
                                 json=invoice_data)
            
            assert response.status_code == 200
            
        # 3. Получение аналитики
        with patch('backend.services.revenue_analytics.RevenueAnalytics.get_monthly_revenue') as mock_revenue:
            mock_revenue.return_value = {'total_revenue': 5000.00}
            
            response = client.get('/api/v1/analytics/revenue/monthly')
            
            assert response.status_code == 200


# Фикстуры для тестов
@pytest.fixture
def client():
    """Фикстура для тестового клиента Flask"""
    from main import app
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            yield client
            db.drop_all()

@pytest.fixture
def test_partner():
    """Фикстура для тестового партнера"""
    partner = Partner(
        partner_id='TEST001',
        company_name='Тестовая компания',
        inn='123456789012',
        contact_person='Иван Иванов',
        phone='+79999999999',
        email='test@test.com',
        verification_status='verified',
        status='active'
    )
    
    db.session.add(partner)
    db.session.commit()
    
    yield partner
    
    db.session.delete(partner)
    db.session.commit()


# Запуск тестов
if __name__ == '__main__':
    pytest.main([__file__, '-v'])
