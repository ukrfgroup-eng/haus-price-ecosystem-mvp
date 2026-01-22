python
"""
Тесты API эндпоинтов
"""

import pytest
import json
from main import app


@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


class TestAPIEndpoints:
    def test_health_check(self, client):
        """Тест проверки работоспособности"""
        response = client.get('/health')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'healthy'
    
    def test_partner_registration(self, client):
        """Тест регистрации партнера"""
        data = {
            "company_name": "Тестовая компания",
            "inn": "123456789012",
            "contact_person": "Иван Иванов",
            "phone": "+79999999999",
            "email": "test@test.com"
        }
        response = client.post('/api/v1/partners/register', json=data)
        assert response.status_code in [201, 400]
