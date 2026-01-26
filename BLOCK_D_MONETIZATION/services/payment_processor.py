cat > services/payment_processor.py << 'EOF'
"""
PaymentProcessor - обработчик платежей через ЮKassa и Тинькофф
"""

import logging
import hashlib
import hmac
import json
from datetime import datetime
from typing import Dict, Any, Optional, Tuple
from enum import Enum

logger = logging.getLogger(__name__)

class PaymentStatus(Enum):
    """Статусы платежей"""
    PENDING = 'pending'
    WAITING_FOR_CAPTURE = 'waiting_for_capture'
    SUCCEEDED = 'succeeded'
    CANCELED = 'canceled'
    REFUNDED = 'refunded'
    FAILED = 'failed'

class PaymentSystem(Enum):
    """Платежные системы"""
    YOOKASSA = 'yookassa'
    TINKOFF = 'tinkoff'
    MANUAL = 'manual'

class PaymentProcessor:
    """Основной класс для обработки платежей"""
    
    def __init__(self, config):
        """
        Инициализация платежного процессора
        
        Args:
            config: Конфигурация блока D
        """
        self.config = config
        self._yookassa_client = None
        self._tinkoff_client = None
        self._init_clients()
    
    def _init_clients(self):
        """Инициализация клиентов платежных систем"""
        # Инициализация ЮKassa
        if self.config.YOOKASSA_SHOP_ID and self.config.YOOKASSA_SECRET_KEY:
            try:
                from yookassa import Configuration, Payment
                Configuration.account_id = self.config.YOOKASSA_SHOP_ID
                Configuration.secret_key = self.config.YOOKASSA_SECRET_KEY
                self._yookassa_client = Payment
                logger.info("YooKassa клиент инициализирован")
            except ImportError:
                logger.warning("Библиотека yookassa не установлена")
            except Exception as e:
                logger.error(f"Ошибка инициализации YooKassa: {e}")
        
        # Инициализация Тинькофф
        if self.config.TINKOFF_TERMINAL_KEY and self.config.TINKOFF_PASSWORD:
            try:
                from tinkoff_api import TinkoffAPI
                self._tinkoff_client = TinkoffAPI(
                    terminal_key=self.config.TINKOFF_TERMINAL_KEY,
                    password=self.config.TINKOFF_PASSWORD
                )
                logger.info("Tinkoff клиент инициализирован")
            except ImportError:
                logger.warning("Библиотека tinkoff_api не установлена")
            except Exception as e:
                logger.error(f"Ошибка инициализации Tinkoff: {e}")
    
    def create_payment(self, amount: float, currency: str = 'RUB',
                      description: str = '', partner_id: str = None,
                      invoice_id: str = None, tariff_code: str = None,
                      payment_system: str = 'yookassa') -> Dict[str, Any]:
        """
        Создание платежа
        
        Args:
            amount: Сумма платежа
            currency: Валюта (RUB, USD, EUR)
            description: Описание платежа
            partner_id: ID партнера
            invoice_id: ID счета
            tariff_code: Код тарифа
            payment_system: Платежная система (yookassa, tinkoff)
            
        Returns:
            Dict с данными платежа
        """
        try:
            payment_data = {
                'amount': amount,
                'currency': currency,
                'description': description,
                'partner_id': partner_id,
                'invoice_id': invoice_id,
                'tariff_code': tariff_code,
                'payment_system': payment_system,
                'status': PaymentStatus.PENDING.value,
                'created_at': datetime.utcnow().isoformat()
            }
            
            if payment_system == PaymentSystem.YOOKASSA.value and self._yookassa_client:
                return self._create_yookassa_payment(payment_data)
            elif payment_system == PaymentSystem.TINKOFF.value and self._tinkoff_client:
                return self._create_tinkoff_payment(payment_data)
            else:
                # Тестовый режим или ручной платеж
                return self._create_test_payment(payment_data)
                
        except Exception as e:
            logger.error(f"Ошибка создания платежа: {e}")
            raise
    
    def _create_yookassa_payment(self, payment_data: Dict) -> Dict:
        """Создание платежа через ЮKassa"""
        try:
            from yookassa import Payment as YooPayment
            
            payment = YooPayment.create({
                "amount": {
                    "value": payment_data['amount'],
                    "currency": payment_data['currency']
                },
                "confirmation": {
                    "type": "redirect",
                    "return_url": self.config.YOOKASSA_RETURN_URL
                },
                "capture": True,
                "description": payment_data['description'],
                "metadata": {
                    "partner_id": payment_data['partner_id'],
                    "invoice_id": payment_data['invoice_id'],
                    "tariff_code": payment_data['tariff_code']
                }
            })
            
            return {
                'payment_id': payment.id,
                'status': payment.status,
                'amount': float(payment.amount.value),
                'currency': payment.amount.currency,
                'confirmation_url': payment.confirmation.confirmation_url if payment.confirmation else None,
                'created_at': payment.created_at,
                'payment_system': 'yookassa',
                'metadata': {
                    'partner_id': payment_data['partner_id'],
                    'invoice_id': payment_data['invoice_id'],
                    'tariff_code': payment_data['tariff_code']
                }
            }
            
        except Exception as e:
            logger.error(f"Ошибка создания платежа YooKassa: {e}")
            raise
    
    def _create_tinkoff_payment(self, payment_data: Dict) -> Dict:
        """Создание платежа через Тинькофф"""
        try:
            order_id = f"order_{datetime.now().strftime('%Y%m%d%H%M%S')}_{payment_data['partner_id']}"
            
            payment = self._tinkoff_client.init(
                amount=payment_data['amount'] * 100,  # В копейках
                order_id=order_id,
                description=payment_data['description'],
                data={
                    'PartnerId': payment_data['partner_id'],
                    'InvoiceId': payment_data['invoice_id'],
                    'TariffCode': payment_data['tariff_code']
                }
            )
            
            return {
                'payment_id': payment['PaymentId'],
                'order_id': order_id,
                'status': 'NEW',
                'amount': payment_data['amount'],
                'currency': payment_data['currency'],
                'payment_url': payment['PaymentURL'],
                'created_at': datetime.utcnow().isoformat(),
                'payment_system': 'tinkoff',
                'metadata': {
                    'partner_id': payment_data['partner_id'],
                    'invoice_id': payment_data['invoice_id'],
                    'tariff_code': payment_data['tariff_code']
                }
            }
            
        except Exception as e:
            logger.error(f"Ошибка создания платежа Tinkoff: {e}")
            raise
    
    def _create_test_payment(self, payment_data: Dict) -> Dict:
        """Создание тестового платежа"""
        payment_id = f"test_pay_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        return {
            'payment_id': payment_id,
            'status': PaymentStatus.PENDING.value,
            'amount': payment_data['amount'],
            'currency': payment_data['currency'],
            'payment_url': f"https://test-payment.example.com/{payment_id}",
            'created_at': datetime.utcnow().isoformat(),
            'payment_system': 'test',
            'metadata': {
                'partner_id': payment_data['partner_id'],
                'invoice_id': payment_data['invoice_id'],
                'tariff_code': payment_data['tariff_code'],
                'test_mode': True
            }
        }
    
    def verify_webhook(self, payment_system: str, data: Dict, signature: str = None) -> bool:
        """
        Верификация вебхука от платежной системы
        
        Args:
            payment_system: Платежная система (yookassa, tinkoff)
            data: Данные вебхука
            signature: Подпись (если есть)
            
        Returns:
            bool: Валидность вебхука
        """
        if payment_system == PaymentSystem.YOOKASSA.value:
            return self._verify_yookassa_webhook(data, signature)
        elif payment_system == PaymentSystem.TINKOFF.value:
            return self._verify_tinkoff_webhook(data, signature)
        else:
            logger.warning(f"Неизвестная платежная система: {payment_system}")
            return False
    
    def _verify_yookassa_webhook(self, data: Dict, signature: str) -> bool:
        """Верификация вебхука ЮKassa"""
        try:
            # ЮKassa отправляет подпись в заголовке
            if not signature:
                return False
            
            # Создаем строку для проверки
            check_string = f"{data['type']}&{data['event']}&{data['object']['id']}"
            
            # Генерируем HMAC-SHA256 подпись
            secret = self.config.YOOKASSA_SECRET_KEY.encode()
            expected_signature = hmac.new(secret, check_string.encode(), hashlib.sha256).hexdigest()
            
            return hmac.compare_digest(expected_signature, signature)
            
        except Exception as e:
            logger.error(f"Ошибка верификации вебхука YooKassa: {e}")
            return False
    
    def _verify_tinkoff_webhook(self, data: Dict, signature: str) -> bool:
        """Верификация вебхука Тинькофф"""
        try:
            # Тинькофф использует подпись на основе данных
            if not signature:
                return False
            
            # Порядок полей для подписи
            fields = ['TerminalKey', 'OrderId', 'Success', 'Status', 'PaymentId', 'ErrorCode', 'Amount', 'CardId', 'Pan']
            
            # Собираем строку для подписи
            check_string = ''
            for field in fields:
                if field in data and data[field]:
                    check_string += str(data[field])
            
            check_string += self.config.TINKOFF_PASSWORD
            
            # Вычисляем SHA256
            expected_signature = hashlib.sha256(check_string.encode()).hexdigest()
            
            return expected_signature == signature
            
        except Exception as e:
            logger.error(f"Ошибка верификации вебхука Tinkoff: {e}")
            return False
    
    def process_refund(self, payment_id: str, amount: float = None,
                      reason: str = '') -> Dict[str, Any]:
        """
        Обработка возврата средств
        
        Args:
            payment_id: ID платежа
            amount: Сумма возврата (None = полный возврат)
            reason: Причина возврата
            
        Returns:
            Dict с результатом возврата
        """
        try:
            # Здесь должна быть логика определения платежной системы
            # и вызова соответствующего API
            
            refund_data = {
                'refund_id': f"ref_{datetime.now().strftime('%Y%m%d%H%M%S')}",
                'payment_id': payment_id,
                'amount': amount,
                'reason': reason,
                'status': 'pending',
                'created_at': datetime.utcnow().isoformat()
            }
            
            logger.info(f"Создан возврат: {refund_data}")
            return refund_data
            
        except Exception as e:
            logger.error(f"Ошибка обработки возврата: {e}")
            raise
    
    def get_payment_status(self, payment_id: str) -> Dict[str, Any]:
        """
        Получение статуса платежа
        
        Args:
            payment_id: ID платежа
            
        Returns:
            Dict с информацией о платеже
        """
        # Заглушка - в реальности нужно обращаться к API платежной системы
        return {
            'payment_id': payment_id,
            'status': 'succeeded',
            'checked_at': datetime.utcnow().isoformat()
        }
EOF
