python
"""
Конфигурация pytest с фикстурами
"""

import pytest
import tempfile
import os
from datetime import datetime, timedelta
from unittest.mock import Mock, patch

from main import app, db
from backend.models import Partner, Payment, Subscription


@pytest.fixture(scope='session')
def database_url():
    """URL тестовой базы данных"""
    return 'sqlite:///:memory:'


@pytest.fixture
def app_context(database_url):
    """Фикстура контекста приложения"""
    app.config.update({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': database_url,
        'SQLALCHEMY_TRACK_MODIFICATIONS': False,
        'SECRET_KEY': 'test-secret-key',
    })
    
    with app.app_context():
        yield app


@pytest.fixture
def client(app_context):
    """Фикстура тестового клиента"""
    return app_context.test_client()


@pytest.fixture
def init_database(app_context):
    """Фикстура инициализации базы данных"""
    with app_context.app_context():
        db.create_all()
        yield db
        db.session.remove()
        db.drop_all()


@pytest.fixture
def test_partner(init_database):
    """Фикстура тестового партнера"""
    partner = Partner(
        partner_id='TEST001',
        company_name='Тестовая компания ООО',
        inn='123456789012',
        legal_form='ООО',
        contact_person='Иван Иванов',
        phone='+79991234567',
        email='test@example.com',
        verification_status='verified',
        is_active=True,
        subscription_type='professional'
    )
    
    db.session.add(partner)
    db.session.commit()
    
    yield partner
    
    db.session.delete(partner)
    db.session.commit()


@pytest.fixture
def test_payment(init_database, test_partner):
    """Фикстура тестового платежа"""
    payment = Payment(
        payment_number='INV-TEST-001',
        partner_id=test_partner.partner_id,
        amount=5000.00,
        currency='RUB',
        status='completed',
        payment_type='subscription',
        tariff_plan='professional',
        description='Тестовый платеж'
    )
    
    db.session.add(payment)
    db.session.commit()
    
    yield payment
    
    db.session.delete(payment)
    db.session.commit()


@pytest.fixture
def test_subscription(init_database, test_partner):
    """Фикстура тестовой подписки"""
    subscription = Subscription(
        partner_id=test_partner.partner_id,
        tariff_plan='professional',
        price=5000.00,
        period='monthly',
        leads_included=15,
        starts_at=datetime.utcnow(),
        expires_at=datetime.utcnow() + timedelta(days=30),
        auto_renewal=True
    )
    
    db.session.add(subscription)
    db.session.commit()
    
    yield subscription
    
    db.session.delete(subscription)
    db.session.commit()


@pytest.fixture
def mock_fns_service():
    """Фикстура мока сервиса ФНС"""
    with patch('backend.services.fns_service.FNSVerificationService') as mock:
        mock_instance = Mock()
        mock_instance.verify_inn.return_value = {
            'success': True,
            'data': {
                'ИНН': '123456789012',
                'Статус': 'действующая',
                'Наименование': 'Тестовая компания'
            }
        }
        mock.return_value = mock_instance
        yield mock_instance


@pytest.fixture
def mock_payment_gateway():
    """Фикстура мока платежного шлюза"""
    with patch('backend.services.payment_processor.PaymentProcessor') as mock:
        mock_instance = Mock()
        mock_instance.create_payment_link.return_value = 'https://payment.test/link'
        mock_instance.handle_payment_webhook.return_value = {'status': 'success'}
        mock.return_value = mock_instance
        yield mock_instance


@pytest.fixture
def mock_ai_analyzer():
    """Фикстура мока AI анализатора"""
    with patch('backend.ai.request_analyzer.RequestAnalyzer') as mock:
        mock_instance = Mock()
        mock_instance.analyze_customer_request.return_value = {
            'project_type': 'строительство',
            'required_specializations': ['каркасные дома'],
            'confidence_score': 0.85
        }
        mock.return_value = mock_instance
        yield mock_instance


@pytest.fixture(autouse=True)
def mock_external_apis():
    """Автоматический мок внешних API"""
    with patch('requests.get') as mock_get, \
         patch('requests.post') as mock_post:
        
        # Мокаем ответы внешних API
        mock_get.return_value = Mock(
            status_code=200,
            json=lambda: {'status': 'ok'}
        )
        mock_post.return_value = Mock(
            status_code=200,
            json=lambda: {'success': True}
        )
        
        yield


@pytest.fixture(scope='session')
def test_data_dir():
    """Директория для тестовых данных"""
    return os.path.join(os.path.dirname(__file__), 'test_data')


@pytest.fixture
def sample_partner_data():
    """Пример данных партнера"""
    return {
        'company_name': 'ООО "СтройДом"',
        'inn': '123456789012',
        'legal_form': 'ООО',
        'contact_person': 'Петров Иван Сергеевич',
        'phone': '+79991234567',
        'email': 'info@stroydom.ru',
        'website': 'https://stroydom.ru',
        'main_category': 'подрядчик',
        'specializations': ['каркасные дома', 'отделка'],
        'regions': ['Московская область']
    }


@pytest.fixture
def sample_customer_request():
    """Пример запроса заказчика"""
    return {
        'message': 'Хочу построить каркасный дом в Московской области',
        'budget': 5000000,
        'timeline': '3-6 месяцев',
        'region': 'Московская область'
    }
