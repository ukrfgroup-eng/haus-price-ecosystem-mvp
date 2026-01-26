cat > services/payment_processor.py << 'EOF'
"""
PaymentProcessor - обработчик платежей для блока D
Версия: 1.0.0
"""

import logging
from datetime import datetime
from typing import Dict, Any, Optional
from enum import Enum

logger = logging.getLogger(__name__)

class PaymentStatus(Enum):
    """Статусы платежей блока D"""
    PENDING = 'pending'
    PROCESSING = 'processing'
    COMPLETED = 'completed'
    FAILED = 'failed'
    REFUNDED = 'refunded'

class PaymentProcessor:
    """Обработчик платежей блока D"""
    
    def __init__(self, config):
        """
        Инициализация платежного процессора блока D
        
        Args:
            config: Конфигурация блока D
        """
        self.config = config
        self._payments = {}
        logger.info("PaymentProcessor блока D инициализирован")
    
    def create_payment(self, amount: float, currency: str = 'RUB',
                      description: str = '', partner_id: str = None,
                      tariff_code: str = None) -> Dict[str, Any]:
        """
        Создание платежа (блок D)
        
        Args:
            amount: Сумма
            currency: Валюта
            description: Описание
            partner_id: ID партнера
            tariff_code: Код тарифа
            
        Returns:
            Данные платежа
        """
        try:
            # Генерация ID платежа
            payment_id = f"pay_d_{partner_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
            
            # Создаем платеж
            payment = {
                'payment_id': payment_id,
                'partner_id': partner_id,
                'amount': amount,
                'currency': currency,
                'description': description,
                'status': PaymentStatus.PENDING.value,
                'tariff_code': tariff_code,
                'payment_url': f"https://payment.block-d.example.com/{payment_id}",
                'created_at': datetime.utcnow().isoformat(),
                'updated_at': datetime.utcnow().isoformat(),
                'source': 'block_d'
            }
            
            # Сохраняем
            self._payments[payment_id] = payment
            
            logger.info(f"Блок D: Создан платеж {payment_id} на сумму {amount} {currency}")
            return payment
            
        except Exception as e:
            logger.error(f"Блок D: Ошибка создания платежа: {e}")
            raise
    
    def process_payment(self, payment_id: str) -> bool:
        """
        Обработка платежа (блок D)
        
        Args:
            payment_id: ID платежа
            
        Returns:
            bool: Успешность обработки
        """
        payment = self._payments.get(payment_id)
        if not payment:
            logger.error(f"Блок D: Платеж {payment_id} не найден")
            return False
        
        try:
            # Имитация обработки платежа
            payment['status'] = PaymentStatus.COMPLETED.value
            payment['paid_at'] = datetime.utcnow().isoformat()
            payment['updated_at'] = datetime.utcnow().isoformat()
            
            logger.info(f"Блок D: Обработан платеж {payment_id}")
            return True
            
        except Exception as e:
            logger.error(f"Блок D: Ошибка обработки платежа {payment_id}: {e}")
            payment['status'] = PaymentStatus.FAILED.value
            payment['error_message'] = str(e)
            return False
    
    def get_payment(self, payment_id: str) -> Optional[Dict]:
        """
        Получение платежа (блок D)
        
        Args:
            payment_id: ID платежа
            
        Returns:
            Данные платежа или None
        """
        return self._payments.get(payment_id)
    
    def get_payments_by_partner(self, partner_id: str) -> List[Dict]:
        """
        Получение платежей партнера (блок D)
        
        Args:
            partner_id: ID партнера
            
        Returns:
            Список платежей
        """
        return [
            payment for payment in self._payments.values()
            if payment['partner_id'] == partner_id and payment.get('source') == 'block_d'
        ]
    
    def refund_payment(self, payment_id: str, amount: float = None,
                      reason: str = '') -> Dict[str, Any]:
        """
        Возврат платежа (блок D)
        
        Args:
            payment_id: ID платежа
            amount: Сумма возврата
            reason: Причина
            
        Returns:
            Данные возврата
        """
        payment = self._payments.get(payment_id)
        if not payment:
            raise ValueError(f"Блок D: Платеж {payment_id} не найден")
        
        if payment['status'] != PaymentStatus.COMPLETED.value:
            raise ValueError(f"Блок Д: Платеж должен быть завершен для возврата")
        
        refund_amount = amount if amount is not None else payment['amount']
        
        refund = {
            'refund_id': f"ref_d_{payment_id}_{datetime.now().strftime('%H%M%S')}",
            'payment_id': payment_id,
            'amount': refund_amount,
            'currency': payment['currency'],
            'reason': reason,
            'status': 'pending',
            'created_at': datetime.utcnow().isoformat(),
            'source': 'block_d'
        }
        
        # Обновляем статус платежа
        payment['status'] = PaymentStatus.REFUNDED.value
        payment['updated_at'] = datetime.utcnow().isoformat()
        
        logger.info(f"Блок D: Создан возврат {refund['refund_id']} для платежа {payment_id}")
        return refund

# Экспорт
__all__ = ['PaymentProcessor', 'PaymentStatus']
EOF
