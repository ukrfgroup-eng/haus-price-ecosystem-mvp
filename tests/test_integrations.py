python
"""
Тесты для блока C: Внешние интеграции
"""

import pytest
from backend.integrations.umnico_webhook import handle_umnico_webhook
from backend.integrations.tilda_webhook import handle_tilda_registration


class TestIntegrations:
    def test_umnico_webhook(self):
        """Тест обработки вебхука Umnico"""
        data = {"message": "Привет", "userId": "test123"}
        response = handle_umnico_webhook(data)
        assert "messages" in response
