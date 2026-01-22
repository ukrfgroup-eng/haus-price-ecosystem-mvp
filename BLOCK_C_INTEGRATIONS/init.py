"""
БЛОК C: ВНЕШНИЕ ИНТЕГРАЦИИ
Интеграция всех внешних сервисов в единую экосистему
"""

__version__ = "1.0.0"
__description__ = "Интеграции с внешними сервисами (Protalk, Umnico, Tilda, API ФНС)"

from .webhook_handlers import WebhookHandler
from .fns_api_client import FNSAPIClient
from .protalk_connector import ProtalkConnector
from .umnico_connector import UmnicoConnector
from .tilda_connector import TildaConnector
from .payment_gateway import PaymentGateway
from .email_service import EmailService

__all__ = [
    'WebhookHandler',
    'FNSAPIClient',
    'ProtalkConnector',
    'UmnicoConnector',
    'TildaConnector',
    'PaymentGateway',
    'EmailService'
]
