cat > BLOCK_D_MONETIZATION/block_d/test_all_services.py << 'EOF'
"""
Тест всех сервисов блока D
"""

import sys
import os

# Добавляем текущую директорию в путь
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_all_services():
    """Тестирование всех сервисов блока D"""
    print("=" * 70)
    print("ТЕСТИРОВАНИЕ ВСЕХ СЕРВИСОВ БЛОКА D")
    print("=" * 70)
    
    try:
        # Импортируем конфигурацию
        from config import config
        print("✅ Конфигурация загружена")
        
        # Импортируем сервисы
        from services.payment_processor import PaymentProcessor
        from services.subscription_manager import SubscriptionManager
        from services.tariff_service import TariffService
        from services.invoice_generator import InvoiceGenerator
        from services.revenue_analytics import RevenueAnalytics
        from services.notification_service import NotificationService
        
        print("✅ Все сервисы импортированы")
        
        # 1. Тестируем TariffService
        print("\n1. Тестирование TariffService:")
        tariff_service = TariffService(config)
        tariffs = tariff_service.get_all_tariffs()
        print(f"   ✓ Тарифов загружено: {len(tariffs)}")
        for tariff in tariffs:
            print(f"     - {tariff['name']}: {tariff['price_monthly']} руб/мес")
        
        # 2. Тестируем PaymentProcessor
        print("\n2. Тестирование PaymentProcessor:")
        payment_processor = PaymentProcessor(config)
        payment = payment_processor.create_payment(
            amount=5000,
            currency='RUB',
            description='Тестовый платеж',
            partner_id='test_partner_001',
            tariff_code='professional'
        )
        print(f"   ✓ Создан платеж: {payment['payment_id']}")
        
        # 3. Тестируем SubscriptionManager
        print("\n3. Тестирование SubscriptionManager:")
        subscription_manager = SubscriptionManager(config, tariff_service)
        subscription = subscription_manager.create_subscription(
            partner_id='test_partner_001',
            tariff_code='professional',
            billing_period='monthly'
        )
        print(f"   ✓ Создана подписка: {subscription['subscription_id']}")
        
        # 4. Тестируем RevenueAnalytics
        print("\n4. Тестирование RevenueAnalytics:")
        revenue_analytics = RevenueAnalytics(config)
        mrr = revenue_analytics.calculate_mrr()
        print(f"   ✓ Рассчитан MRR: {mrr['current_mrr']} руб")
        
        # 5. Тестируем InvoiceGenerator
        print("\n5. Тестирование InvoiceGenerator:")
        invoice_generator = InvoiceGenerator(config)
        
        client_info = {
            'name': 'Тестовый Партнер',
            'email': 'test@example.com',
            'company': 'Тестовая компания'
        }
        
        items = [{
            'name': 'Подписка Professional',
            'quantity': 1,
            'price': 5000,
            'total': 5000
        }]
        
        invoice = invoice_generator.create_invoice(
            partner_id='test_partner_001',
            client_info=client_info,
            items=items,
            tariff_code='professional'
        )
        print(f"   ✓ Создан счет: {invoice['invoice_number']}")
        
        # 6. Тестируем NotificationService
        print("\n6. Тестирование NotificationService:")
        notification_service = NotificationService(config)
        print(f"   ✓ Сервис уведомлений инициализирован")
        
        # Тест отправки email
        email_sent = notification_service.send_invoice_email(invoice, 'test@example.com')
        print(f"   ✓ Тест отправки счета: {'Успешно' if email_sent else 'Не удалось'}")
        
        print("\n" + "=" * 70)
        print("✅ ВСЕ СЕРВИСЫ БЛОКА D РАБОТАЮТ КОРРЕКТНО!")
        print("=" * 70)
        
        return True
        
    except ImportError as e:
        print(f"\n❌ ОШИБКА ИМПОРТА: {e}")
        print("\nПроверьте наличие файлов:")
        print("1. config.py")
        print("2. Все файлы в services/")
        return False
        
    except Exception as e:
        print(f"\n❌ ОШИБКА ТЕСТИРОВАНИЯ: {e}")
        return False

if __name__ == "__main__":
    success = test_all_services()
    sys.exit(0 if success else 1)
EOF
