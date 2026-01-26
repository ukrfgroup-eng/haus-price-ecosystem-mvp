cat > services/__init__.py << 'EOF'
"""
Сервисы блока D - бизнес-логика системы монетизации
"""

from .payment_processor import PaymentProcessor
from .subscription_manager import SubscriptionManager
from .tariff_service import TariffService
from .invoice_generator import InvoiceGenerator
from .revenue_analytics import RevenueAnalytics
from .notification_service import NotificationService

__all__ = [
    'PaymentProcessor',
    'SubscriptionManager',
    'TariffService',
    'InvoiceGenerator',
    'RevenueAnalytics',
    'NotificationService'
]
EOF
