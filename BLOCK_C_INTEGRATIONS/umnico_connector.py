"""
КОННЕКТОР ДЛЯ UMNICO (ЧАТ НА САЙТЕ)
Интеграция с чат-виджетом на сайте
"""

import requests
import logging
import json
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class UmnicoConnector:
    """Коннектор для работы с Umnico (чат-виджет на сайте)"""
    
    def __init__(self, api_key: str, widget_token: str, base_url: str = "https://umnico.com"):
        self.api_key = api_key
        self.widget_token = widget_token
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        self.session.headers.update({
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json',
            'User-Agent': 'HausPrice-Ecosystem/1.0'
        })
    
    def send_widget_message(self, user_id: str, message: str, 
                          message_type: str = 'text', 
                          attachments: Optional[List[Dict]] = None) -> Dict[str, Any]:
        """Отправка сообщения через виджет Umnico"""
        try:
            url = f"{self.base_url}/api/v1/widget/messages/send"
            
            payload = {
                'widget_token': self.widget_token,
                'user_id': user_id,
                'message': {
                    'type': message_type,
                    'text': message
                }
            }
            
            if attachments:
                payload['message']['attachments'] = attachments
            
            logger.info(f"Sending Umnico widget message to user {user_id}")
            response = self.session.post(url, json=payload, timeout=10)
            
            if response.status_code == 200:
                result = response.json()
                return {
                    'success': True,
                    'message_id': result.get('id'),
                    'user_id': user_id,
                    'sent_at': datetime.utcnow().isoformat()
                }
            else:
                logger.error(f"Failed to send widget message: {response.status_code} - {response.text}")
                return {
                    'success': False,
                    'error': f'Ошибка отправки сообщения: {response.status_code}',
                    'details': response.text[:200]
                }
                
        except requests.Timeout:
            logger.error(f"Timeout sending widget message to user {user_id}")
            return {
                'success': False,
                'error': 'Таймаут при отправке сообщения'
            }
        except Exception as e:
            logger.error(f"Error sending widget message to user {user_id}: {e}")
            return {
                'success': False,
                'error': f'Ошибка отправки сообщения: {str(e)}'
            }
    
    def send_quick_reply(self, user_id: str, message: str, 
                        options: List[Dict[str, str]]) -> Dict[str, Any]:
        """Отправка сообщения с быстрыми ответами"""
        try:
            url = f"{self.base_url}/api/v1/widget/messages/send"
            
            quick_replies = []
            for option in options:
                quick_replies.append({
                    'title': option.get('title', ''),
                    'payload': option.get('payload', '')
                })
            
            payload = {
                'widget_token': self.widget_token,
                'user_id': user_id,
                'message': {
                    'type': 'quick_reply',
                    'text': message,
                    'quick_replies': quick_replies
                }
            }
            
            response = self.session.post(url, json=payload, timeout=10)
            
            if response.status_code == 200:
                return {
                    'success': True,
                    'message': 'Сообщение с быстрыми ответами отправлено',
                    'user_id': user_id
                }
            else:
                return {
                    'success': False,
                    'error': f'Ошибка отправки сообщения: {response.status_code}'
                }
                
        except Exception as e:
            logger.error(f"Error sending quick reply to user {user_id}: {e}")
            return {
                'success': False,
                'error': f'Ошибка отправки сообщения: {str(e)}'
            }
    
    def send_carousel(self, user_id: str, items: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Отправка карусели с карточками партнеров"""
        try:
            url = f"{self.base_url}/api/v1/widget/messages/send"
            
            carousel_items = []
            for item in items:
                carousel_item = {
                    'title': item.get('title', ''),
                    'description': item.get('description', ''),
                    'image_url': item.get('image_url', ''),
                    'buttons': item.get('buttons', [])
                }
                carousel_items.append(carousel_item)
            
            payload = {
                'widget_token': self.widget_token,
                'user_id': user_id,
                'message': {
                    'type': 'carousel',
                    'items': carousel_items
                }
            }
            
            response = self.session.post(url, json=payload, timeout=10)
            
            if response.status_code == 200:
                return {
                    'success': True,
                    'message': 'Карусель отправлена',
                    'user_id': user_id,
                    'items_count': len(items)
                }
            else:
                return {
                    'success': False,
                    'error': f'Ошибка отправки карусели: {response.status_code}'
                }
                
        except Exception as e:
            logger.error(f"Error sending carousel to user {user_id}: {e}")
            return {
                'success': False,
                'error': f'Ошибка отправки карусели: {str(e)}'
            }
    
    def get_user_conversation(self, user_id: str, limit: int = 50) -> Dict[str, Any]:
        """Получение истории диалога с пользователем"""
        try:
            url = f"{self.base_url}/api/v1/widget/conversations/{user_id}"
            params = {'limit': limit}
            
            response = self.session.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                return {
                    'success': True,
                    'conversation': data.get('messages', []),
                    'user_id': user_id,
                    'message_count': len(data.get('messages', []))
                }
            elif response.status_code == 404:
                return {
                    'success': False,
                    'error': 'Диалог с пользователем не найден',
                    'user_id': user_id
                }
            else:
                return {
                    'success': False,
                    'error': f'Ошибка получения диалога: {response.status_code}'
                }
                
        except Exception as e:
            logger.error(f"Error getting conversation for user {user_id}: {e}")
            return {
                'success': False,
                'error': f'Ошибка получения диалога: {str(e)}'
            }
    
    def update_user_profile(self, user_id: str, profile_data: Dict[str, Any]) -> Dict[str, Any]:
        """Обновление профиля пользователя"""
        try:
            url = f"{self.base_url}/api/v1/widget/users/{user_id}"
            
            payload = {
                'widget_token': self.widget_token,
                'profile': profile_data
            }
            
            response = self.session.put(url, json=payload, timeout=10)
            
            if response.status_code == 200:
                return {
                    'success': True,
                    'message': 'Профиль пользователя обновлен',
                    'user_id': user_id
                }
            else:
                return {
                    'success': False,
                    'error': f'Ошибка обновления профиля: {response.status_code}'
                }
                
        except Exception as e:
            logger.error(f"Error updating user profile {user_id}: {e}")
            return {
                'success': False,
                'error': f'Ошибка обновления профиля: {str(e)}'
            }
    
    def track_event(self, user_id: str, event_name: str, 
                   event_data: Optional[Dict] = None) -> Dict[str, Any]:
        """Отслеживание событий пользователя"""
        try:
            url = f"{self.base_url}/api/v1/widget/events/track"
            
            payload = {
                'widget_token': self.widget_token,
                'user_id': user_id,
                'event': event_name
            }
            
            if event_data:
                payload['data'] = event_data
            
            response = self.session.post(url, json=payload, timeout=10)
            
            if response.status_code == 200:
                return {
                    'success': True,
                    'message': f'Событие {event_name} отслежено',
                    'user_id': user_id
                }
            else:
                return {
                    'success': False,
                    'error': f'Ошибка отслеживания события: {response.status_code}'
                }
                
        except Exception as e:
            logger.error(f"Error tracking event for user {user_id}: {e}")
            return {
                'success': False,
                'error': f'Ошибка отслеживания события: {str(e)}'
            }
    
    def create_partner_carousel_item(self, partner: Dict[str, Any]) -> Dict[str, Any]:
        """Создание элемента карусели для партнера"""
        name = partner.get('company_name', 'Не указано')
        specializations = ', '.join(partner.get('specializations', [])[:2])
        rating = partner.get('rating', 0)
        region = partner.get('regions', ['Не указано'])[0]
        
        return {
            'title': name,
            'description': f'⭐ {rating}/5 | {specializations} | {region}',
            'image_url': partner.get('logo_url', 'https://via.placeholder.com/300x200?text=Partner'),
            'buttons': [
                {
                    'type': 'postback',
                    'title': '📞 Позвонить',
                    'payload': f'call_{partner.get("partner_code")}'
                },
                {
                    'type': 'web_url',
                    'title': 'ℹ️ Подробнее',
                    'url': f'/partner/{partner.get("partner_code")}'
                }
            ]
        }
    
    def send_welcome_message(self, user_id: str, user_name: Optional[str] = None) -> Dict[str, Any]:
        """Отправка приветственного сообщения новому пользователю"""
        welcome_text = "👋 Добро пожаловать в экосистему Дома-Цены.РФ!"
        
        if user_name:
            welcome_text = f"👋 {user_name}, добро пожаловать в экосистему Дома-Цены.РФ!"
        
        options = [
            {'title': '🔨 Я заказчик', 'payload': 'customer'},
            {'title': '🏢 Я партнер', 'payload': 'partner'},
            {'title': '❓ Узнать больше', 'payload': 'info'}
        ]
        
        return self.send_quick_reply(user_id, welcome_text, options)
    
    def format_statistics_message(self, stats: Dict[str, Any]) -> str:
        """Форматирование статистического сообщения"""
        return f"""
📊 <b>Статистика экосистемы</b>

🏢 Партнеров в системе: {stats.get('total_partners', 0)}
✅ Верифицировано: {stats.get('verified_partners', 0)}
🔨 Активных заявок: {stats.get('active_leads', 0)}
🎯 Средний рейтинг: {stats.get('average_rating', 0)}/5

💼 Завершено проектов: {stats.get('completed_projects', 0)}
💰 Оборот системы: {stats.get('total_revenue', 0):,} руб
👥 Заказчиков сегодня: {stats.get('customers_today', 0)}
"""
