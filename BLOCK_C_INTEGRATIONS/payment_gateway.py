"""
ПЛАТЕЖНЫЙ ШЛЮЗ
Интеграция с платежными системами (ЮKassa, CloudPayments)
"""

import requests
import logging
import json
import base64
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
import uuid

logger = logging.getLogger(__name__)

class PaymentGateway:
    """Платежный шлюз для обработки оплаты подписок"""
    
    def __init__(self, provider: str = 'yookassa', **config):
        self.provider = provider.lower()
        self.config = config
        
        if self.provider == 'yookassa':
            self.gateway = YooKassaGateway(**config)
        elif self.provider == 'cloudpayments':
            self.gateway = CloudPaymentsGateway(**config)
        else:
            raise ValueError(f"Unsupported payment provider: {provider}")
    
    def create_payment(self, amount: float, currency: str, 
                      description: str, metadata: Dict[str, Any],
                      return_url: str) -> Dict[str, Any]:
        """Создание платежа"""
        try:
            # Генерация уникального ID платежа
            payment_id = str(uuid.uuid4())
            
            result = self.gateway.create_payment(
                amount=amount,
                currency=currency,
                description=description,
                metadata={**metadata, 'payment_id': payment_id},
                return_url=return_url
            )
            
            if result.get('success'):
                result['payment_id'] = payment_id
            
            return result
            
        except Exception as e:
            logger.error(f"Error creating payment: {e}")
            return {
                'success': False,
                'error': f'Ошибка создания платежа: {str(e)}'
            }
    
    def verify_payment(self, payment_id: str) -> Dict[str, Any]:
        """Проверка статуса платежа"""
        try:
            return self.gateway.verify_payment(payment_id)
        except Exception as e:
            logger.error(f"Error verifying payment {payment_id}: {e}")
            return {
                'success': False,
                'error': f'Ошибка проверки платежа: {str(e)}'
            }
    
    def create_subscription(self, partner_code: str, tariff_plan: str,
                           amount: float, interval: str = 'month') -> Dict[str, Any]:
        """Создание подписки для партнера"""
        try:
            # Генерация описания подписки
            description = f"Подписка {tariff_plan} для партнера {partner_code}"
            
            # Методанные для отслеживания
            metadata = {
                'partner_code': partner_code,
                'tariff_plan': tariff_plan,
                'subscription_type': 'recurring',
                'interval': interval
            }
            
            result = self.gateway.create_subscription(
                amount=amount,
                description=description,
                metadata=metadata,
                interval=interval
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Error creating subscription for {partner_code}: {e}")
            return {
                'success': False,
                'error': f'Ошибка создания подписки: {str(e)}'
            }
    
    def cancel_subscription(self, subscription_id: str) -> Dict[str, Any]:
        """Отмена подписки"""
        try:
            return self.gateway.cancel_subscription(subscription_id)
        except Exception as e:
            logger.error(f"Error canceling subscription {subscription_id}: {e}")
            return {
                'success': False,
                'error': f'Ошибка отмены подписки: {str(e)}'
            }
    
    def get_payment_history(self, partner_code: str, 
                           start_date: Optional[str] = None,
                           end_date: Optional[str] = None) -> Dict[str, Any]:
        """Получение истории платежей партнера"""
        try:
            # Если даты не указаны, берем последние 30 дней
            if not start_date:
                start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
            if not end_date:
                end_date = datetime.now().strftime('%Y-%m-%d')
            
            result = self.gateway.get_payment_history(
                metadata_filter={'partner_code': partner_code},
                start_date=start_date,
                end_date=end_date
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Error getting payment history for {partner_code}: {e}")
            return {
                'success': False,
                'error': f'Ошибка получения истории платежей: {str(e)}'
            }
    
    def refund_payment(self, payment_id: str, amount: Optional[float] = None) -> Dict[str, Any]:
        """Возврат платежа"""
        try:
            return self.gateway.refund_payment(payment_id, amount)
        except Exception as e:
            logger.error(f"Error refunding payment {payment_id}: {e}")
            return {
                'success': False,
                'error': f'Ошибка возврата платежа: {str(e)}'
            }
    
    def calculate_tariff_amount(self, tariff_plan: str) -> Dict[str, Any]:
        """Расчет суммы платежа по тарифу"""
        tariffs = {
            'start': {'monthly': 0, 'yearly': 0},
            'basic': {'monthly': 5000, 'yearly': 50000},  # Скидка 16.7%
            'premium': {'monthly': 15000, 'yearly': 150000},
            'business': {'monthly': 30000, 'yearly': 300000}
        }
        
        if tariff_plan not in tariffs:
            return {
                'success': False,
                'error': f'Неизвестный тарифный план: {tariff_plan}'
            }
        
        return {
            'success': True,
            'tariff_plan': tariff_plan,
            'amounts': tariffs[tariff_plan],
            'currency': 'RUB',
            'description': f'Тарифный план: {tariff_plan}'
        }


class YooKassaGateway:
    """Интеграция с ЮKassa (Яндекс.Касса)"""
    
    def __init__(self, shop_id: str, secret_key: str, 
                 api_url: str = "https://api.yookassa.ru/v3"):
        self.shop_id = shop_id
        self.secret_key = secret_key
        self.api_url = api_url.rstrip('/')
        
        auth_string = f"{shop_id}:{secret_key}"
        self.auth_header = f"Basic {base64.b64encode(auth_string.encode()).decode()}"
        
        self.session = requests.Session()
        self.session.headers.update({
            'Authorization': self.auth_header,
            'Content-Type': 'application/json',
            'Idempotence-Key': ''  # Будет обновляться для каждого запроса
        })
    
    def create_payment(self, amount: float, currency: str, 
                      description: str, metadata: Dict[str, Any],
                      return_url: str) -> Dict[str, Any]:
        """Создание платежа в ЮKassa"""
        try:
            url = f"{self.api_url}/payments"
            
            # Генерация уникального ключа идемпотентности
            idempotence_key = str(uuid.uuid4())
            self.session.headers['Idempotence-Key'] = idempotence_key
            
            # Конвертация суммы в копейки для RUB
            amount_value = int(amount * 100) if currency == 'RUB' else amount
            
            payload = {
                'amount': {
                    'value': str(amount_value),
                    'currency': currency
                },
                'description': description,
                'metadata': metadata,
                'confirmation': {
                    'type': 'redirect',
                    'return_url': return_url
                },
                'capture': True
            }
            
            logger.info(f"Creating YooKassa payment: {description}")
            response = self.session.post(url, json=payload, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                
                return {
                    'success': True,
                    'payment_id': data.get('id'),
                    'confirmation_url': data.get('confirmation', {}).get('confirmation_url'),
                    'status': data.get('status'),
                    'amount': amount,
                    'currency': currency,
                    'idempotence_key': idempotence_key
                }
            else:
                logger.error(f"YooKassa payment creation failed: {response.status_code} - {response.text}")
                return {
                    'success': False,
                    'error': f'Ошибка создания платежа: {response.status_code}',
                    'details': response.text[:200]
                }
                
        except Exception as e:
            logger.error(f"Error creating YooKassa payment: {e}")
            return {
                'success': False,
                'error': f'Ошибка создания платежа: {str(e)}'
            }
    
    def verify_payment(self, payment_id: str) -> Dict[str, Any]:
        """Проверка статуса платежа"""
        try:
            url = f"{self.api_url}/payments/{payment_id}"
            
            idempotence_key = str(uuid.uuid4())
            self.session.headers['Idempotence-Key'] = idempotence_key
            
            response = self.session.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                return {
                    'success': True,
                    'payment_id': payment_id,
                    'status': data.get('status'),
                    'amount': float(data.get('amount', {}).get('value', 0)) / 100,
                    'currency': data.get('amount', {}).get('currency'),
                    'paid': data.get('paid'),
                    'metadata': data.get('metadata', {}),
                    'created_at': data.get('created_at')
                }
            else:
                return {
                    'success': False,
                    'error': f'Ошибка проверки платежа: {response.status_code}'
                }
                
        except Exception as e:
            logger.error(f"Error verifying YooKassa payment {payment_id}: {e}")
            return {
                'success': False,
                'error': f'Ошибка проверки платежа: {str(e)}'
            }
    
    def create_subscription(self, amount: float, description: str,
                           metadata: Dict[str, Any], interval: str = 'month') -> Dict[str, Any]:
        """Создание подписки (автоплатежей)"""
        try:
            url = f"{self.api_url}/subscriptions"
            
            idempotence_key = str(uuid.uuid4())
            self.session.headers['Idempotence-Key'] = idempotence_key
            
            # Конвертация суммы в копейки
            amount_value = int(amount * 100)
            
            payload = {
                'amount': {
                    'value': str(amount_value),
                    'currency': 'RUB'
                },
                'description': description,
                'metadata': metadata,
                'interval': interval,
                'start_date': (datetime.now() + timedelta(days=1)).isoformat() + 'Z'
            }
            
            response = self.session.post(url, json=payload, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                
                return {
                    'success': True,
                    'subscription_id': data.get('id'),
                    'status': data.get('status'),
                    'amount': amount,
                    'interval': interval,
                    'confirmation_url': data.get('confirmation_url')
                }
            else:
                return {
                    'success': False,
                    'error': f'Ошибка создания подписки: {response.status_code}'
                }
                
        except Exception as e:
            logger.error(f"Error creating YooKassa subscription: {e}")
            return {
                'success': False,
                'error': f'Ошибка создания подписки: {str(e)}'
            }
    
    def cancel_subscription(self, subscription_id: str) -> Dict[str, Any]:
        """Отмена подписки"""
        try:
            url = f"{self.api_url}/subscriptions/{subscription_id}/cancel"
            
            idempotence_key = str(uuid.uuid4())
            self.session.headers['Idempotence-Key'] = idempotence_key
            
            response = self.session.post(url, timeout=10)
            
            if response.status_code == 200:
                return {
                    'success': True,
                    'subscription_id': subscription_id,
                    'message': 'Подписка отменена'
                }
            else:
                return {
                    'success': False,
                    'error': f'Ошибка отмены подписки: {response.status_code}'
                }
                
        except Exception as e:
            logger.error(f"Error canceling YooKassa subscription {subscription_id}: {e}")
            return {
                'success': False,
                'error': f'Ошибка отмены подписки: {str(e)}'
            }
    
    def get_payment_history(self, metadata_filter: Dict[str, Any],
                           start_date: str, end_date: str) -> Dict[str, Any]:
        """Получение истории платежей"""
        try:
            url = f"{self.api_url}/payments"
            
            params = {
                'created_at.gte': f'{start_date}T00:00:00.000Z',
                'created_at.lte': f'{end_date}T23:59:59.999Z',
                'limit': 100
            }
            
            # Добавляем фильтр по метаданным
            if metadata_filter:
                for key, value in metadata_filter.items():
                    params[f'metadata.{key}'] = value
            
            response = self.session.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                payments = []
                for payment in data.get('items', []):
                    payments.append({
                        'id': payment.get('id'),
                        'status': payment.get('status'),
                        'amount': float(payment.get('amount', {}).get('value', 0)) / 100,
                        'currency': payment.get('amount', {}).get('currency'),
                        'description': payment.get('description'),
                        'metadata': payment.get('metadata', {}),
                        'created_at': payment.get('created_at'),
                        'paid': payment.get('paid')
                    })
                
                return {
                    'success': True,
                    'payments': payments,
                    'count': len(payments),
                    'period': f'{start_date} - {end_date}'
                }
            else:
                return {
                    'success': False,
                    'error': f'Ошибка получения истории платежей: {response.status_code}'
                }
                
        except Exception as e:
            logger.error(f"Error getting YooKassa payment history: {e}")
            return {
                'success': False,
                'error': f'Ошибка получения истории платежей: {str(e)}'
            }
    
    def refund_payment(self, payment_id: str, amount: Optional[float] = None) -> Dict[str, Any]:
        """Возврат платежа"""
        try:
            url = f"{self.api_url}/refunds"
            
            idempotence_key = str(uuid.uuid4())
            self.session.headers['Idempotence-Key'] = idempotence_key
            
            # Получаем информацию о платеже
            payment_info = self.verify_payment(payment_id)
            if not payment_info.get('success'):
                return payment_info
            
            refund_amount = amount or payment_info.get('amount', 0)
            refund_amount_value = int(refund_amount * 100)
            
            payload = {
                'payment_id': payment_id,
                'amount': {
                    'value': str(refund_amount_value),
                    'currency': payment_info.get('currency', 'RUB')
                }
            }
            
            response = self.session.post(url, json=payload, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                return {
                    'success': True,
                    'refund_id': data.get('id'),
                    'payment_id': payment_id,
                    'amount': refund_amount,
                    'status': data.get('status'),
                    'created_at': data.get('created_at')
                }
            else:
                return {
                    'success': False,
                    'error': f'Ошибка возврата платежа: {response.status_code}'
                }
                
        except Exception as e:
            logger.error(f"Error refunding YooKassa payment {payment_id}: {e}")
            return {
                'success': False,
                'error': f'Ошибка возврата платежа: {str(e)}'
            }


class CloudPaymentsGateway:
    """Интеграция с CloudPayments"""
    
    def __init__(self, public_id: str, api_secret: str,
                 api_url: str = "https://api.cloudpayments.ru"):
        self.public_id = public_id
        self.api_secret = api_secret
        self.api_url = api_url.rstrip('/')
        
        auth_string = f"{public_id}:{api_secret}"
        self.auth_header = f"Basic {base64.b64encode(auth_string.encode()).decode()}"
        
        self.session = requests.Session()
        self.session.headers.update({
            'Authorization': self.auth_header,
            'Content-Type': 'application/json'
        })
    
    def create_payment(self, amount: float, currency: str,
                      description: str, metadata: Dict[str, Any],
                      return_url: str) -> Dict[str, Any]:
        """Создание платежа в CloudPayments"""
        try:
            # CloudPayments требует токен карты, поэтому для первого платежа
            # возвращаем URL для формы оплаты
            
            payment_id = str(uuid.uuid4())
            invoice_id = f"INV-{payment_id[:8].upper()}"
            
            return {
                'success': True,
                'payment_id': payment_id,
                'invoice_id': invoice_id,
                'confirmation_url': f"{self.api_url}/payments/form?invoiceId={invoice_id}",
                'amount': amount,
                'currency': currency,
                'description': 'Для оплаты перейдите по ссылке',
                'metadata': metadata
            }
            
        except Exception as e:
            logger.error(f"Error creating CloudPayments payment: {e}")
            return {
                'success': False,
                'error': f'Ошибка создания платежа: {str(e)}'
            }
    
    def verify_payment(self, payment_id: str) -> Dict[str, Any]:
        """Проверка статуса платежа"""
        try:
            url = f"{self.api_url}/payments/get"
            
            params = {
                'InvoiceId': f"INV-{payment_id[:8].upper()}"
            }
            
            response = self.session.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get('Success'):
                    payment_data = data.get('Model', {})
                    
                    return {
                        'success': True,
                        'payment_id': payment_id,
                        'status': payment_data.get('Status'),
                        'amount': payment_data.get('Amount'),
                        'currency': payment_data.get('Currency'),
                        'paid': payment_data.get('Status') == 'Completed',
                        'metadata': payment_data.get('Data', {}),
                        'created_at': payment_data.get('CreatedDate')
                    }
                else:
                    return {
                        'success': False,
                        'error': data.get('Message', 'Ошибка проверки платежа')
                    }
            else:
                return {
                    'success': False,
                    'error': f'Ошибка проверки платежа: {response.status_code}'
                }
                
        except Exception as e:
            logger.error(f"Error verifying CloudPayments payment {payment_id}: {e}")
            return {
                'success': False,
                'error': f'Ошибка проверки платежа: {str(e)}'
            }
