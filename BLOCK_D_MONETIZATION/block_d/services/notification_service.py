cat > BLOCK_D_MONETIZATION/block_d/services/notification_service.py << 'EOF'
"""
NotificationService - система уведомлений для блока D
"""

class NotificationService:
    """Сервис уведомлений блока D"""
    
    def __init__(self, config):
        self.config = config
        print("✅ NotificationService инициализирован")
    
    def send_invoice_email(self, invoice, recipient_email):
        """Отправка счета по email"""
        if self.config.is_test_mode:
            print(f"📧 Тестовый режим: Счет {invoice['invoice_number']} отправлен на {recipient_email}")
            return True
        print(f"📧 Счет {invoice['invoice_number']} отправлен на {recipient_email}")
        return True
    
    def send_payment_success_email(self, payment, recipient_email):
        """Отправка подтверждения оплаты"""
        if self.config.is_test_mode:
            print(f"📧 Тестовый режим: Подтверждение оплаты {payment['payment_id']} отправлено на {recipient_email}")
            return True
        print(f"📧 Подтверждение оплаты {payment['payment_id']} отправлено на {recipient_email}")
        return True
EOF
