python
"""
Тесты для блока B: Бот-проводник + AI-анализ
"""

import pytest
from backend.bot.bot_handler import BotHandler
from backend.ai.request_analyzer import RequestAnalyzer


class TestBotFunctionality:
    def test_message_processing(self):
        """Тест обработки сообщений ботом"""
        handler = BotHandler()
        response = handler.process_message("Хочу построить дом")
        assert response is not None
