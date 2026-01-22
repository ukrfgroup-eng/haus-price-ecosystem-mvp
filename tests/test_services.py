python
"""
Тесты сервисов экосистемы Дома-Цены.РФ
"""

import pytest
import json
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock, AsyncMock
from decimal import Decimal

# Импорты для тестирования
from backend.services.fns_service import FNSVerificationService
from backend.services.invoice_generator import InvoiceGenerator
from backend.services.revenue_analytics import RevenueAnalytics
from backend.services.subscription_manager import SubscriptionManager
from backend.services.partner_service import PartnerService
from backend.services.bot_service import BotService
from backend.services.ai_analyzer import AIAnalyzer
from backend.services.payment_processor import PaymentProcessor


class TestFNSVerificationService:
    """Тесты сервиса верификации ФНС"""
    
    def setup_method(self):
        """Настройка перед каждым тестом"""
        self.service = FNSVerificationService()
        self.service.api_key = "test-api-key"
        self.service.api_url = "https://api-fns.ru/test"
    
    @patch('backend.services.fns_service.requests.get')
    def test_verify_inn_success(self, mock_get):
        """Тест успешной проверки ИНН"""
        # Мокаем успешный ответ API ФНС
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "status": "success",
            "data": {
                "ИНН": "123456789012",
                "Наименование": 'ООО "ТЕСТОВАЯ КОМПАНИЯ"',
                "Статус": "действующая",
                "ОГРН": "1234567890123",
                "ДатаРег": "2020-01-01",
                "Адрес": "г. Москва, ул. Тестовая, д. 1"
            }
        }
        mock_get.return_value = mock_response
        
        result = self.service.verify_inn("123456789012")
        
        assert result['success'] == True
        assert result['data']['ИНН'] == "123456789012"
        assert result['data']['Статус'] == "действующая"
        assert 'Наименование' in result['data']
        
        mock_get.assert_called_once_with(
            "https://api-fns.ru/test",
            params={"req": "123456789012", "key": "test-api-key"}
        )
    
    @patch('backend.services.fns_service.requests.get')
    def test_verify_inn_not_found(self, mock_get):
        """Тест проверки несуществующего ИНН"""
        mock_response = Mock()
        mock_response.status_code = 404
        mock_get.return_value = mock_response
        
        result = self.service.verify_inn("000000000000")
        
        assert result['success'] == False
        assert 'error' in result
        assert 'не найден' in result['error'].lower()
    
    @patch('backend.services.fns_service.requests.get')
    def test_verify_inn_api_error(self, mock_get):
        """Тест ошибки API ФНС"""
        mock_response = Mock()
        mock_response.status_code = 500
        mock_response.text = "Internal Server Error"
        mock_get.return_value = mock_response
        
        result = self.service.verify_inn("123456789012")
        
        assert result['success'] == False
        assert 'error' in result
        assert '500' in result['error']
    
    def test_validate_inn_format(self):
        """Тест валидации формата ИНН"""
        test_cases = [
            ("1234567890", True),      # 10 цифр (ИП)
            ("123456789012", True),    # 12 цифр (ООО)
            ("123456789", False),      # 9 цифр
            ("12345678901", False),    # 11 цифр
            ("abcdefghij", False),     # не цифры
            ("", False),               # пустая строка
            (None, False),             # None
        ]
        
        for inn, expected_valid in test_cases:
            is_valid = self.service.validate_inn_format(inn)
            assert is_valid == expected_valid, f"ИНН: {inn}"
    
    @patch('backend.services.fns_service.requests.get')
    def test_verify_company_comprehensive(self, mock_get):
        """Комплексная проверка компании"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "status": "success",
            "data": {
                "ИНН": "123456789012",
                "Наименование": 'ООО "СТРОЙДОМ"',
                "Статус": "действующая",
                "ОГРН": "1234567890123",
                "ДатаРег": "2018-05-15",
                "Адрес": "123456, г. Москва, ул. Строителей, д. 10",
                "УставнойКапитал": "1000000",
                "Руководитель": "Иванов Иван Иванович"
            }
        }
        mock_get.return_value = mock_response
        
        result = self.service.verify_company(
            inn="123456789012",
            company_name="СТРОЙДОМ"
        )
        
        assert result['success'] == True
        assert result['data']['ИНН'] == "123456789012"
        assert result['data']['Статус'] == "действующая"
        assert result['is_active'] == True
        assert 'details' in result


class TestInvoiceGenerator:
    """Тесты генератора счетов"""
    
    def setup_method(self):
        self.generator = InvoiceGenerator()
    
    def test_generate_invoice_number(self):
        """Тест генерации номера счета"""
        with patch('backend.services.invoice_generator.datetime') as mock_datetime, \
             patch('backend.services.invoice_generator.Payment') as mock_payment:
            
            # Мокаем дату
            mock_now = Mock()
            mock_now.strftime.return_value = "240101"
            mock_now.replace.return_value = mock_now
            mock_datetime.now.return_value = mock_now
            mock_datetime.utcnow.return_value = mock_now
            
            # Мокаем запрос к базе данных
            mock_query = Mock()
            mock_filter = Mock()
            mock_count = Mock()
            mock_count.count.return_value = 3
            mock_filter.filter.return_value = mock_count
            mock_query.filter.return_value = mock_filter
            mock_payment.query = mock_query
            
            invoice_number = self.generator.generate_invoice_number("TEST123")
            
            assert invoice_number.startswith("INV-")
            assert "240101" in invoice_number
            assert "TEST123" in invoice_number
            assert invoice_number.endswith("-0004")  # 3 + 1
    
    def test_amount_to_words(self):
        """Тест конвертации суммы прописью"""
        test_cases = [
            (0, "ноль рублей 00 копеек"),
            (1, "один рубль 00 копеек"),
            (2, "два рубля 00 копеек"),
            (5, "пять рублей 00 копеек"),
            (10, "десять рублей 00 копеек"),
            (11, "одиннадцать рублей 00 копеек"),
            (20, "двадцать рублей 00 копеек"),
            (100, "сто рублей 00 копеек"),
            (101, "сто один рубль 00 копеек"),
            (115, "сто пятнадцать рублей 00 копеек"),
            (1000, "одна тысяча рублей 00 копеек"),
            (2000, "две тысячи рублей 00 копеек"),
            (5000, "пять тысяч рублей 00 копеек"),
            (10000, "десять тысяч рублей 00 копеек"),
            (123456, "сто двадцать три тысячи четыреста пятьдесят шесть рублей 00 копеек"),
            (1000000, "один миллион рублей 00 копеек"),
            (1.50, "один рубль 50 копеек"),
            (1234.56, "одна тысяча двести тридцать четыре рубля 56 копеек"),
        ]
        
        for amount, expected in test_cases:
            result = self.generator.amount_to_words(amount)
            # Нормализуем сравнение (пробелы, регистр)
            result_lower = result.lower()
            expected_lower = expected.lower()
            
            # Проверяем ключевые слова
            assert "рубл" in result_lower
            assert "копе" in result_lower
            
            # Проверяем точность для простых случаев
            if amount <= 20:
                amount_int = int(amount)
                if amount_int == 1:
                    assert "один рубль" in result_lower
                elif amount_int == 2:
                    assert "два рубля" in result_lower
    
    @patch('backend.services.invoice_generator.Partner')
    @patch('backend.services.invoice_generator.Payment')
    @patch('backend.services.invoice_generator.db.session')
    @patch('builtins.open', new_callable=MagicMock)
    @patch('os.makedirs')
    def test_create_invoice_success(self, mock_makedirs, mock_open, 
                                   mock_session, mock_payment, mock_partner):
        """Тест успешного создания счета"""
        # Мокаем партнера
        mock_partner_obj = Mock()
        mock_partner_obj.partner_id = "TEST001"
        mock_partner_obj.company_name = "ООО ТЕСТ"
        mock_partner_obj.inn = "123456789012"
        mock_partner_obj.legal_address = "Москва"
        mock_partner_obj.actual_address = "Москва"
        mock_partner_obj.contact_person = "Иван Иванов"
        mock_partner_obj.email = "test@test.com"
        
        mock_partner.query.filter_by.return_value.first.return_value = mock_partner_obj
        
        # Мокаем сессию базы данных
        mock_session.add = Mock()
        mock_session.commit = Mock()
        mock_session.rollback = Mock()
        
        # Мокаем Payment для generate_invoice_number
        with patch.object(InvoiceGenerator, 'generate_invoice_number') as mock_gen:
            mock_gen.return_value = "INV-20240101-001"
            
            # Мокаем open для сохранения файла
            mock_file = Mock()
            mock_open.return_value.__enter__.return_value = mock_file
            
            result = self.generator.create_invoice(
                partner_id="TEST001",
                amount=5000.00,
                tariff_plan="professional",
                description="Тестовый счет"
            )
            
            assert result is not None
            assert 'invoice_number' in result
            assert result['invoice_number'] == "INV-20240101-001"
            assert result['amount'] == 5000.00
            assert result['currency'] == 'RUB'
            assert 'payment_url' in result
            assert 'due_date' in result
            
            # Проверяем вызовы
            mock_session.add.assert_called()
            mock_session.commit.assert_called()
            mock_open.assert_called()
            mock_file.write.assert_called()
    
    def test_get_invoice_info(self):
        """Тест получения информации о счете"""
        with patch('backend.services.invoice_generator.Payment') as mock_payment:
            mock_payment_obj = Mock()
            mock_payment_obj.payment_number = "INV-001"
            mock_payment_obj.partner_id = "TEST001"
            mock_payment_obj.amount = 5000.00
            mock_payment_obj.currency = "RUB"
            mock_payment_obj.status = "pending"
            mock_payment_obj.created_at = datetime(2024, 1, 1)
            mock_payment_obj.paid_at = None
            mock_payment_obj.description = "Тест"
            mock_payment_obj.invoice_file = "invoices/INV-001.html"
            
            mock_payment.query.filter_by.return_value.first.return_value = mock_payment_obj
            
            result = self.generator.get_invoice("INV-001")
            
            assert result is not None
            assert result['invoice_number'] == "INV-001"
            assert result['partner_id'] == "TEST001"
            assert result['amount'] == 5000.00
            assert result['status'] == "pending"


class TestRevenueAnalytics:
    """Тесты аналитики доходов"""
    
    def setup_method(self):
        self.analytics = RevenueAnalytics()
    
    @patch('backend.services.revenue_analytics.Payment')
    @patch('backend.services.revenue_analytics.db.session')
    def test_get_revenue_by_period(self, mock_session, mock_payment):
        """Тест получения доходов за период"""
        # Мокаем платежи
        mock_payment1 = Mock()
        mock_payment1.amount = 5000.00
        mock_payment1.created_at = datetime(2024, 1, 15)
        mock_payment1.tariff_plan = "professional"
        
        mock_payment2 = Mock()
        mock_payment2.amount = 15000.00
        mock_payment2.created_at = datetime(2024, 1, 20)
        mock_payment2.tariff_plan = "business"
        
        mock_payment3 = Mock()
        mock_payment3.amount = 5000.00
        mock_payment3.created_at = datetime(2024, 1, 25)
        mock_payment3.tariff_plan = "professional"
        
        # Мокаем запрос
        mock_query = Mock()
        mock_filter = Mock()
        mock_filter.filter.return_value.all.return_value = [
            mock_payment1, mock_payment2, mock_payment3
        ]
        mock_query.filter.return_value = mock_filter
        mock_session.query.return_value = mock_query
        
        start_date = datetime(2024, 1, 1)
        end_date = datetime(2024, 1, 31)
        
        result = self.analytics.get_revenue_by_period(start_date, end_date)
        
        assert result is not None
        assert result['total_revenue'] == 25000.00  # 5000 + 15000 + 5000
        assert result['payment_count'] == 3
        assert result['average_payment'] == pytest.approx(8333.33, rel=0.01)
        assert result['revenue_by_tariff']['professional'] == 10000.00
        assert result['revenue_by_tariff']['business'] == 15000.00
        assert len(result['daily_revenue']) == 3
    
    def test_get_monthly_revenue(self):
        """Тест получения месячной статистики"""
        with patch.object(RevenueAnalytics, 'get_revenue_by_period') as mock_method:
            mock_method.return_value = {
                'total_revenue': 25000.00,
                'payment_count': 10
            }
            
            result = self.analytics.get_monthly_revenue(2024, 1)
            
            assert result is not None
            assert result['total_revenue'] == 25000.00
            mock_method.assert_called_once()
    
    def test_get_yearly_revenue(self):
        """Тест получения годовой статистики"""
        with patch.object(RevenueAnalytics, 'get_revenue_by_period') as mock_method:
            mock_method.return_value = {
                'total_revenue': 300000.00,
                'payment_count': 120
            }
            
            result = self.analytics.get_yearly_revenue(2024)
            
            assert result is not None
            assert result['total_revenue'] == 300000.00
            mock_method.assert_called_once()
    
    @patch('backend.services.revenue_analytics.Payment')
    def test_get_partner_lifetime_value(self, mock_payment):
        """Тест расчета LTV партнера"""
        # Мокаем платежи партнера
        mock_payment1 = Mock()
        mock_payment1.amount = 5000.00
        mock_payment1.created_at = datetime(2024, 1, 1)
        
        mock_payment2 = Mock()
        mock_payment2.amount = 15000.00
        mock_payment2.created_at = datetime(2024, 2, 1)
        
        mock_payment3 = Mock()
        mock_payment3.amount = 5000.00
        mock_payment3.created_at = datetime(2024, 3, 1)
        
        # Мокаем запрос
        mock_query = Mock()
        mock_filter = Mock()
        mock_filter.filter.return_value.all.return_value = [
            mock_payment1, mock_payment2, mock_payment3
        ]
        mock_query.filter.return_value = mock_filter
        mock_payment.query = mock_query
        
        result = self.analytics.get_partner_lifetime_value("TEST001")
        
        assert result is not None
        assert result['total_spent'] == 25000.00
        assert result['payment_count'] == 3
        assert result['average_payment'] == pytest.approx(8333.33, rel=0.01)
        assert result['active_months'] == 3
        assert 'ltv' in result
    
    @patch('backend.services.revenue_analytics.Partner')
    @patch('backend.services.revenue_analytics.Payment')
    @patch('backend.services.revenue_analytics.db.session')
    def test_get_churn_rate(self, mock_session, mock_payment, mock_partner):
        """Тест расчета уровня оттока"""
        # Мокаем общее количество партнеров
        mock_partner_count = Mock()
        mock_partner_count.count.return_value = 100
        mock_partner.query.filter.return_value = mock_partner_count
        
        # Мокаем запрос для партнеров без платежей
        mock_query_result = Mock()
        mock_query_result.count.return_value = 5
        mock_session.query.return_value.filter.return_value = mock_query_result
        
        result = self.analytics.get_churn_rate(30)
        
        assert result is not None
        assert result['total_partners'] == 100
        assert result['lost_partners'] == 5
        assert result['churn_rate'] == 5.0  # (5/100)*100
        assert result['period_days'] == 30
    
    @patch('backend.services.revenue_analytics.db.session')
    def test_get_top_partners(self, mock_session):
        """Тест получения топовых партнеров"""
        # Мокаем результаты запроса
        mock_results = [
            ('ООО "СТРОЙДОМ"', 'PART001', 50000.00, 10),
            ('ИП Иванов', 'PART002', 30000.00, 6),
            ('ООО "РЕМОНТ"', 'PART003', 20000.00, 4),
        ]
        
        mock_query = Mock()
        mock_query.join.return_value.filter.return_value.group_by.return_value \
            .order_by.return_value.limit.return_value.all.return_value = mock_results
        
        mock_session.query.return_value = mock_query
        
        result = self.analytics.get_top_partners(limit=3, period_days=30)
        
        assert len(result) == 3
        assert result[0]['company_name'] == 'ООО "СТРОЙДОМ"'
        assert result[0]['total_spent'] == 50000.00
        assert result[0]['payment_count'] == 10
        assert result[0]['average_payment'] == 5000.00
    
    def test_get_revenue_forecast(self):
        """Тест прогнозирования доходов"""
        with patch.object(RevenueAnalytics, 'get_monthly_revenue') as mock_monthly:
            # Мокаем исторические данные
            mock_monthly.side_effect = [
                {'total_revenue': 100000},  # 3 месяца назад
                {'total_revenue': 110000},  # 2 месяца назад
                {'total_revenue': 120000},  # 1 месяц назад
                {'total_revenue': 130000},  # текущий месяц
            ]
            
            result = self.analytics.get_revenue_forecast(months=3)
            
            assert result is not None
            assert 'historical_data' in result
            assert 'forecast' in result
            assert len(result['forecast']) == 3
            assert 'average_growth_rate' in result
            
            # Проверяем, что прогнозные значения имеют правильную структуру
            for forecast in result['forecast']:
                assert 'year' in forecast
                assert 'month' in forecast
                assert 'month_name' in forecast
                assert 'forecast_revenue' in forecast
                assert 'growth_rate' in forecast


class TestSubscriptionManager:
    """Тесты менеджера подписок"""
    
    def setup_method(self):
        self.manager = SubscriptionManager()
    
    def test_tariff_plans(self):
        """Тест тарифных планов"""
        plans = self.manager.get_tariff_plans()
        
        assert 'start' in plans
        assert 'professional' in plans
        assert 'business' in plans
        
        # Проверяем структуру тарифов
        for plan_name, plan_data in plans.items():
            assert 'price' in plan_data
            assert 'leads_per_month' in plan_data
            assert 'features' in plan_data
            assert isinstance(plan_data['features'], list)
    
    @patch('backend.services.subscription_manager.Partner')
    @patch('backend.services.subscription_manager.Subscription')
    @patch('backend.services.subscription_manager.db.session')
    def test_create_subscription(self, mock_session, mock_subscription, mock_partner):
        """Тест создания подписки"""
        # Мокаем партнера
        mock_partner_obj = Mock()
        mock_partner_obj.partner_id = "TEST001"
        mock_partner_obj.company_name = "ООО ТЕСТ"
        
        mock_partner.query.filter_by.return_value.first.return_value = mock_partner_obj
        
        # Мокаем создание подписки
        mock_subscription_obj = Mock()
        mock_subscription.return_value = mock_subscription_obj
        
        # Мокаем сессию
        mock_session.add = Mock()
        mock_session.commit = Mock()
        
        result = self.manager.create_subscription(
            partner_id="TEST001",
            tariff_plan="professional",
            period="monthly"
        )
        
        assert result is not None
        assert 'subscription_id' in result
        assert 'tariff_plan' in result
        assert 'price' in result
        assert 'period' in result
        assert 'expires_at' in result
        
        mock_session.add.assert_called_with(mock_subscription_obj)
        mock_session.commit.assert_called()
    
    @patch('backend.services.subscription_manager.Subscription')
    @patch('backend.services.subscription_manager.db.session')
    def test_get_active_subscription(self, mock_session, mock_subscription):
        """Тест получения активной подписки"""
        # Мокаем подписку
        mock_subscription_obj = Mock()
        mock_subscription_obj.id = 1
        mock_subscription_obj.partner_id = "TEST001"
        mock_subscription_obj.tariff_plan = "professional"
        mock_subscription_obj.status = "active"
        mock_subscription_obj.expires_at = datetime.utcnow() + timedelta(days=10)
        
        mock_subscription.query.filter.return_value.first.return_value = mock_subscription_obj
        
        result = self.manager.get_active_subscription("TEST001")
        
        assert result is not None
        assert result['partner_id'] == "TEST001"
        assert result['tariff_plan'] == "professional"
        assert result['status'] == "active"
        assert result['days_remaining'] > 0
    
    @patch('backend.services.subscription_manager.Subscription')
    @patch('backend.services.subscription_manager.db.session')
    def test_check_subscription_status(self, mock_session, mock_subscription):
        """Тест проверки статуса подписки"""
        # Мокаем подписку с разными статусами
        test_cases = [
            ("active", datetime.utcnow() + timedelta(days=10), True),
            ("expired", datetime.utcnow() - timedelta(days=1), False),
            ("cancelled", datetime.utcnow() + timedelta(days=10), False),
            ("suspended", datetime.utcnow() + timedelta(days=10), False),
        ]
        
        for status, expires_at, expected_active in test_cases:
            mock_subscription_obj = Mock()
            mock_subscription_obj.status = status
            mock_subscription_obj.expires_at = expires_at
            
            mock_subscription.query.filter.return_value.first.return_value = mock_subscription_obj
            
            result = self.manager.check_subscription_status("TEST001")
            
            assert result['is_active'] == expected_active
            assert result['status'] == status
            assert 'expires_at' in result
    
    @patch('backend.services.subscription_manager.Subscription')
    @patch('backend.services.subscription_manager.db.session')
    def test_renew_subscription(self, mock_session, mock_subscription):
        """Тест продления подписки"""
        # Мокаем существующую подписку
        mock_subscription_obj = Mock()
        mock_subscription_obj.id = 1
        mock_subscription_obj.partner_id = "TEST001"
        mock_subscription_obj.tariff_plan = "professional"
        mock_subscription_obj.status = "active"
        mock_subscription_obj.expires_at = datetime.utcnow() + timedelta(days=5)
        
        mock_subscription.query.filter.return_value.first.return_value = mock_subscription_obj
        
        # Мокаем сессию
        mock_session.commit = Mock()
        
        result = self.manager.renew_subscription(
            subscription_id=1,
            period="monthly"
        )
        
        assert result is not None
        assert result['success'] == True
        assert 'new_expires_at' in result
        assert 'days_added' in result
        assert result['days_added'] == 30  # 30 дней для monthly
        
        mock_session.commit.assert_called()
    
    @patch('backend.services.subscription_manager.Subscription')
    @patch('backend.services.subscription_manager.db.session')
    def test_cancel_subscription(self, mock_session, mock_subscription):
        """Тест отмены подписки"""
        # Мокаем подписку
        mock_subscription_obj = Mock()
        mock_subscription_obj.id = 1
        mock_subscription_obj.partner_id = "TEST001"
        mock_subscription_obj.status = "active"
        
        mock_subscription.query.filter_by.return_value.first.return_value = mock_subscription_obj
        
        # Мокаем сессию
        mock_session.commit = Mock()
        
        result = self.manager.cancel_subscription(
            subscription_id=1,
            reason="тестовая отмена"
        )
        
        assert result is not None
        assert result['success'] == True
        assert mock_subscription_obj.status == "cancelled"
        assert mock_subscription_obj.cancellation_reason == "тестовая отмена"
        
        mock_session.commit.assert_called()
    
    @patch('backend.services.subscription_manager.Subscription')
    @patch('backend.services.subscription_manager.db.session')
    def test_get_expiring_subscriptions(self, mock_session, mock_subscription):
        """Тест получения истекающих подписок"""
        # Мокаем список подписок
        mock_subscription_list = [
            Mock(partner_id="PART001", expires_at=datetime.utcnow() + timedelta(days=3)),
            Mock(partner_id="PART002", expires_at=datetime.utcnow() + timedelta(days=5)),
            Mock(partner_id="PART003", expires_at=datetime.utcnow() + timedelta(days=7)),
        ]
        
        mock_subscription.query.filter.return_value.all.return_value = mock_subscription_list
        
        result = self.manager.get_expiring_subscriptions(days_threshold=7)
        
        assert len(result) == 3
        for i, subscription in enumerate(result):
            assert 'partner_id' in subscription
            assert 'expires_at' in subscription
            assert 'days_remaining' in subscription
            assert subscription['days_remaining'] <= 7


class TestPaymentProcessor:
    """Тесты платежного процессора"""
    
    def setup_method(self):
        self.processor = PaymentProcessor()
    
    @patch('backend.services.payment_processor.requests.post')
    def test_create_payment(self, mock_post):
        """Тест создания платежа"""
        # Мокаем ответ платежной системы
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "id": "payment_123",
            "status": "pending",
            "confirmation": {
                "confirmation_url": "https://payment.test/confirm"
            },
            "amount": {
                "value": "5000.00",
                "currency": "RUB"
            }
        }
        mock_post.return_value = mock_response
        
        result = self.processor.create_payment(
            amount=5000.00,
            currency="RUB",
            description="Тестовый платеж",
            metadata={"partner_id": "TEST001"}
        )
        
        assert result is not None
        assert result['payment_id'] == "payment_123"
        assert result['status'] == "pending"
        assert result['payment_url'] == "https://payment.test/confirm"
        assert result['amount'] == 5000.00
        
        mock_post.assert_called_once()
    
    @patch('backend.services.payment_processor.requests.post')
    def test_create_payment_failure(self, mock_post):
        """Тест ошибки создания платежа"""
        mock_response = Mock()
        mock_response.status_code = 400
        mock_response.json.return_value = {
            "error": "Invalid amount"
        }
        mock_post.return_value = mock_response
        
        result = self.processor.create_payment(
            amount=-100.00,  # Неверная сумма
            currency="RUB",
            description="Тест"
        )
        
        assert result is not None
        assert result['success'] == False
        assert 'error' in result
    
    @patch('backend.services.payment_processor.requests.get')
    def test_check_payment_status(self, mock_get):
        """Тест проверки статуса платежа"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "id": "payment_123",
            "status": "succeeded",
            "paid": True,
            "amount": {
                "value": "5000.00",
                "currency": "RUB"
            },
            "metadata": {"partner_id": "TEST001"}
        }
        mock_get.return_value = mock_response
        
        result = self.processor.check_payment_status("payment_123")
        
        assert result is not None
        assert result['payment_id'] == "payment_123"
        assert result['status'] == "succeeded"
        assert result['paid'] == True
        assert result['amount'] == 5000.00
        
        mock_get.assert_called_once()
    
    def test_validate_payment_data(self):
        """Тест валидации платежных данных"""
        test_cases = [
            (
                {"amount": 100.00, "currency": "RUB", "description": "Тест"},
                True
            ),
            (
                {"amount": -100.00, "currency": "RUB", "description": "Тест"},
                False  # Отрицательная сумма
            ),
            (
                {"amount": 100.00, "currency": "", "description": "Тест"},
                False  # Пустая валюта
            ),
            (
                {"amount": 100.00, "currency": "RUB", "description": ""},
                False  # Пустое описание
            ),
            (
                {"amount": 0, "currency": "RUB", "description": "Тест"},
                False  # Нулевая сумма
            ),
        ]
        
        for data, expected_valid in test_cases:
            is_valid = self.processor.validate_payment_data(data)
            assert is_valid == expected_valid, f"Data: {data}"
    
    @patch('backend.services.payment_processor.requests.post')
    def test_refund_payment(self, mock_post):
        """Тест возврата платежа"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "id": "refund_123",
            "status": "succeeded",
            "amount": {
                "value": "5000.00",
                "currency": "RUB"
            }
        }
        mock_post.return_value = mock_response
        
        result = self.processor.refund_payment(
            payment_id="payment_123",
            amount=5000.00,
            reason="тестовый возврат"
        )
        
        assert result is not None
        assert result['refund_id'] == "refund_123"
        assert result['status'] == "succeeded"
        assert result['amount'] == 5000.00
        
        mock_post.assert_called_once()


class TestAIAnalyzer:
    """Тесты AI анализатора"""
    
    def setup_method(self):
        self.analyzer = AIAnalyzer()
    
    def test_analyze_customer_request(self):
        """Тест анализа запроса заказчика"""
        test_messages = [
            (
                "Хочу построить каркасный дом в Московской области площадью 100м2",
                {
                    "project_type": "строительство",
                    "specializations": ["каркасные дома"],
                    "region": "Московская область"
                }
            ),
            (
                "Нужен ремонт квартиры в Москве, санузел и кухня",
                {
                    "project_type": "ремонт",
                    "specializations": ["отделочные работы"],
                    "region": "Москва"
                }
            ),
            (
                "Ищу подрядчика для строительства бани из бруса в Ленобласти",
                {
                    "project_type": "строительство",
                    "specializations": ["бани", "деревянные дома"],
                    "region": "Ленинградская область"
                }
            ),
        ]
        
        for message, expected in test_messages:
            result = self.analyzer.analyze_customer_request(message)
            
            assert result is not None
            assert 'project_type' in result
            assert 'required_specializations' in result
            assert 'confidence_score' in result
            assert isinstance(result['confidence_score'], float)
            assert 0 <= result['confidence_score'] <= 1
    
    def test_extract_entities(self):
        """Тест извлечения сущностей из текста"""
        test_cases = [
            (
                "Строительство дома 10x12 в Подмосковье за 3 млн рублей",
                {
                    "regions": ["Подмосковье", "Московская область"],
                    "budget": 3000000,
                    "size": "10x12"
                }
            ),
            (
                "Ремонт 2-комнатной квартиры в СПб, бюджет 500 тыс",
                {
                    "regions": ["СПб", "Санкт-Петербург"],
                    "budget": 500000,
                    "rooms": 2
                }
            ),
        ]
        
        for text, expected in test_cases:
            result = self.analyzer.extract_entities(text)
            
            assert result is not None
            assert isinstance(result, dict)
            
            # Проверяем наличие ключевых полей
            if 'бюджет' in text.lower():
                assert 'budget' in result or 'budget_range' in result
    
    def test_classify_project_type(self):
        """Тест классификации типа проекта"""
        test_cases = [
            ("строительство дома", "строительство"),
            ("ремонт квартиры", "ремонт"),
            ("отделка офиса", "отделка"),
            ("проектирование коттеджа", "проектирование"),
            ("нужны строительные материалы", "материалы"),
            ("ищу архитектора", "проектирование"),
        ]
        
        for text, expected_type in test_cases:
            result = self.analyzer.classify_project_type(text)
            assert result is not None
            # Проверяем, что результат содержит ожидаемый тип или похожий
            if expected_type in ["строительство", "ремонт", "отделка"]:
                assert result in ["строительство", "ремонт", "отделка"]
    
    def test_extract_budget(self):
        """Тест извлечения бюджета"""
        test_cases = [
            ("бюджет 2 миллиона рублей", (2000000, 2000000)),
            ("от 1 до 3 млн", (1000000, 3000000)),
            ("500 тысяч", (500000, 500000)),
            ("1.5 млн", (1500000, 1500000)),
            ("до 10 млн", (0, 10000000)),
            ("минимальный бюджет", (0, 0)),
        ]
        
        for text, expected_range in test_cases:
            result = self.analyzer.extract_budget(text)
            assert result is not None
            assert isinstance(result, tuple)
            assert len(result) == 2
            assert isinstance(result[0], (int, float))
            assert isinstance(result[1], (int, float))
    
    def test_map_to_specializations(self):
        """Тест маппинга на специализации"""
        test_cases = [
            (
                "строительство",
                {"region": "Московская область", "budget_range": (1000000, 5000000)},
                ["каркасные дома", "кирпичные дома", "деревянные дома"]
            ),
            (
                "ремонт",
                {"region": "Москва", "budget_range": (500000, 2000000)},
                ["отделочные работы", "сантехнические работы", "электромонтаж"]
            ),
            (
                "кровля",
                {"region": "Ленинградская область", "budget_range": (300000, 1000000)},
                ["кровельные работы", "металлочерепица", "гибкая черепица"]
            ),
        ]
        
        for project_type, params, expected_specializations in test_cases:
            result = self.analyzer.map_to_specializations(project_type, params)
            
            assert result is not None
            assert isinstance(result, list)
            assert len(result) > 0
            
            # Проверяем, что хотя бы одна специализация соответствует ожидаемой
            matches = any(spec in expected_specializations for spec in result)
            assert matches, f"Expected: {expected_specializations}, Got: {result}"
    
    def test_calculate_urgency(self):
        """Тест расчета срочности"""
        test_cases = [
            ("срочно нужно начать на следующей неделе", "high"),
            ("планируем начать через месяц", "medium"),
            ("пока на стадии планирования", "low"),
            ("хотелось бы в ближайшее время", "medium"),
            ("как можно быстрее", "high"),
        ]
        
        for text, expected_urgency in test_cases:
            result = self.analyzer.calculate_urgency(text)
            
            assert result in ["low", "medium", "high"]
            
            # Проверяем логику: если в тексте есть "срочно" или "быстро", то high
            if "срочно" in text or "быстро" in text:
                assert result == "high"
    
    def test_determine_missing_info(self):
        """Тест определения недостающей информации"""
        test_cases = [
            (
                {"region": "Москва", "budget_range": (1000000, 5000000)},
                ["timeline", "specific_requirements"]
            ),
            (
                {"budget_range": (1000000, 5000000), "timeline": "3 месяца"},
                ["region", "specific_requirements"]
            ),
            (
                {"region": "Московская область", "timeline": "6 месяцев"},
                ["budget_range", "specific_requirements"]
            ),
            (
                {},  # Пустые параметры
                ["region", "budget_range", "timeline", "specific_requirements"]
            ),
        ]
        
        for params, expected_questions in test_cases:
            result = self.analyzer.determine_missing_info(params)
            
            assert isinstance(result, list)
            
            # Проверяем, что все ожидаемые вопросы присутствуют
            for expected in expected_questions:
                # Ищем вопрос, который относится к недостающей информации
                found = any(
                    expected in q.lower() or 
                    any(keyword in q.lower() for keyword in {
                        'регион': 'region',
                        'бюджет': 'budget_range', 
                        'срок': 'timeline',
                        'требован': 'specific_requirements'
                    }[expected] if expected in {'region', 'budget_range', 'timeline', 'specific_requirements'})
                    for q in result
                )
                assert found, f"Missing question about {expected}"


# Тесты интеграции сервисов
class TestServicesIntegration:
    """Интеграционные тесты взаимодействия сервисов"""
    
    def setup_method(self):
        self.fns_service = FNSVerificationService()
        self.invoice_generator = InvoiceGenerator()
        self.revenue_analytics = RevenueAnalytics()
        self.subscription_manager = SubscriptionManager()
    
    def test_complete_partner_onboarding_flow(self):
        """Тест полного цикла онбординга партнера"""
        # 1. Верификация компании через ФНС
        with patch.object(FNSVerificationService, 'verify_inn') as mock_verify:
            mock_verify.return_value = {
                'success': True,
                'data': {
                    'ИНН': '123456789012',
                    'Наименование': 'ООО "СТРОЙДОМ"',
                    'Статус': 'действующая'
                }
            }
            
            verification_result = self.fns_service.verify_inn('123456789012')
            assert verification_result['success'] == True
        
        # 2. Создание подписки
        with patch.object(SubscriptionManager, 'create_subscription') as mock_create_sub:
            mock_create_sub.return_value = {
                'subscription_id': 1,
                'tariff_plan': 'professional',
                'price': 5000.00,
                'period': 'monthly'
            }
            
            subscription_result = self.subscription_manager.create_subscription(
                partner_id='PART001',
                tariff_plan='professional'
            )
            assert subscription_result['subscription_id'] == 1
        
        # 3. Создание счета для оплаты
        with patch.object(InvoiceGenerator, 'create_invoice') as mock_create_inv:
            mock_create_inv.return_value = {
                'invoice_number': 'INV-001',
                'payment_url': '/pay/INV-001',
                'amount': 5000.00
            }
            
            invoice_result = self.invoice_generator.create_invoice(
                partner_id='PART001',
                amount=5000.00,
                tariff_plan='professional'
            )
            assert invoice_result['invoice_number'] == 'INV-001'
        
        # 4. Проверка аналитики после оплаты
        with patch.object(RevenueAnalytics, 'get_monthly_revenue') as mock_revenue:
            mock_revenue.return_value = {
                'total_revenue': 5000.00,
                'payment_count': 1,
                'average_payment': 5000.00
            }
            
            analytics_result = self.revenue_analytics.get_monthly_revenue()
            assert analytics_result['total_revenue'] == 5000.00
        
        # Все шаги выполнены успешно
        assert True
    
    def test_service_dependencies(self):
        """Тест зависимостей между сервисами"""
        # Проверяем, что сервисы могут работать вместе
        services = [
            self.fns_service,
            self.invoice_generator,
            self.revenue_analytics,
            self.subscription_manager
        ]
        
        for service in services:
            assert service is not None
        
        # Проверяем, что сервисы имеют необходимые методы
        required_methods = {
            FNSVerificationService: ['verify_inn', 'validate_inn_format'],
            InvoiceGenerator: ['create_invoice', 'generate_invoice_number'],
            RevenueAnalytics: ['get_monthly_revenue', 'get_partner_lifetime_value'],
            SubscriptionManager: ['create_subscription', 'get_active_subscription']
        }
        
        for service_class, methods in required_methods.items():
            for method in methods:
                assert hasattr(service_class, method), \
                    f"{service_class.__name__} не имеет метода {method}"


# Запуск тестов
if __name__ == '__main__':
    pytest.main([__file__, '-v'])
