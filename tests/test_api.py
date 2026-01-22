python
"""
Тесты API эндпоинтов
"""

import pytest
import json
from datetime import datetime, timedelta


@pytest.fixture
def auth_header():
    """Фикстура для заголовков авторизации"""
    return {
        'Authorization': 'Bearer test-token',
        'Content-Type': 'application/json'
    }


class TestHealthAPI:
    """Тесты эндпоинтов проверки работоспособности"""
    
    def test_health_check(self, client):
        """Тест /health"""
        response = client.get('/health')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['status'] == 'healthy'
        assert 'timestamp' in data
        assert 'components' in data
    
    def test_home_page(self, client):
        """Тест главной страницы"""
        response = client.get('/')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['service'] == 'MATRIX CORE API - Дома-Цены.РФ'
        assert 'endpoints' in data


class TestPartnerAPI:
    """Тесты API партнеров"""
    
    def test_register_partner_success(self, client):
        """Тест успешной регистрации партнера"""
        partner_data = {
            'company_name': 'ООО "Тестовая компания"',
            'inn': '123456789012',
            'contact_person': 'Иван Иванов',
            'phone': '+79991234567',
            'email': 'test@example.com',
            'legal_form': 'ООО'
        }
        
        # Мокаем проверку ИНН
        with patch('backend.services.fns_service.FNSVerificationService.verify_inn') as mock_verify:
            mock_verify.return_value = {
                'success': True,
                'data': {'ИНН': '123456789012', 'Статус': 'действующая'}
            }
            
            response = client.post('/api/v1/partners/register',
                                 json=partner_data)
            
            assert response.status_code == 201
            
            data = json.loads(response.data)
            assert data['success'] == True
            assert 'partner' in data
            assert 'next_steps' in data
            assert len(data['next_steps']) == 2
    
    def test_register_partner_validation_error(self, client):
        """Тест ошибки валидации при регистрации"""
        invalid_data = {
            'company_name': '',  # Пустое название
            'inn': '123',  # Неправильный ИНН
        }
        
        response = client.post('/api/v1/partners/register',
                             json=invalid_data)
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data
    
    def test_get_partner_profile(self, client, test_partner):
        """Тест получения профиля партнера"""
        response = client.get(f'/api/v1/partners/{test_partner.partner_id}')
        
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['success'] == True
        assert data['partner']['partner_id'] == test_partner.partner_id
        assert 'registration_progress' in data


class TestPaymentAPI:
    """Тесты API платежей"""
    
    def test_create_invoice(self, client, test_partner, auth_header):
        """Тест создания счета"""
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
                'amount': 5000.00,
                'currency': 'RUB'
            }
            
            response = client.post('/api/v1/payments/create-invoice',
                                 json=invoice_data,
                                 headers=auth_header)
            
            assert response.status_code == 200
            
            data = json.loads(response.data)
            assert data['success'] == True
            assert data['data']['invoice_number'] == 'INV-TEST-001'
    
    def test_get_revenue_analytics(self, client, auth_header):
        """Тест получения аналитики доходов"""
        with patch('backend.services.revenue_analytics.RevenueAnalytics.get_monthly_revenue') as mock_revenue:
            mock_revenue.return_value = {
                'total_revenue': 150000.00,
                'payment_count': 30,
                'average_payment': 5000.00
            }
            
            response = client.get('/api/v1/analytics/revenue/monthly?year=2024&month=1',
                                headers=auth_header)
            
            assert response.status_code == 200
            
            data = json.loads(response.data)
            assert data['success'] == True
            assert data['data']['total_revenue'] == 150000.00
    
    def test_download_invoice(self, client, test_payment):
        """Тест скачивания счета"""
        response = client.get(f'/api/v1/payments/invoice/{test_payment.payment_number}/download')
        
        # Может вернуть 200 (если файл есть) или 404 (если нет)
        assert response.status_code in [200, 404]


class TestWebhookAPI:
    """Тесты вебхуков"""
    
    def test_umnico_webhook(self, client):
        """Тест вебхука Umnico"""
        webhook_data = {
            'message': 'Привет, хочу стать партнером',
            'userId': 'user123',
            'type': 'message'
        }
        
        response = client.post('/webhook/umnico',
                             json=webhook_data,
                             headers={'X-Webhook-Secret': 'test-secret'})
        
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert 'messages' in data
        assert len(data['messages']) > 0
    
    def test_protalk_webhook(self, client):
        """Тест вебхука Protalk"""
        webhook_data = {
            'type': 'message',
            'message': {'text': '/start'},
            'user': {'id': 'user456'}
        }
        
        response = client.post('/webhook/protalk',
                             json=webhook_data,
                             headers={'X-Webhook-Secret': 'test-secret'})
        
        assert response.status_code == 200
    
    def test_tilda_webhook(self, client):
        """Тест вебхука Tilda"""
        webhook_data = {
            'formid': 'partner_registration_complete',
            'partner_code': 'TEST001',
            'data': {'company_name': 'Тест'}
        }
        
        response = client.post('/webhook/tilda',
                             json=webhook_data)
        
        assert response.status_code == 200


def test_api_error_handling(client):
    """Тест обработки ошибок API"""
    # Тест несуществующего эндпоинта
    response = client.get('/api/v1/nonexistent')
    assert response.status_code == 404
    
    # Тест некорректного метода
    response = client.post('/health')
    assert response.status_code == 405
    
    # Тест некорректного JSON
    response = client.post('/api/v1/partners/register',
                         data='invalid json',
                         headers={'Content-Type': 'application/json'})
    assert response.status_code == 400
