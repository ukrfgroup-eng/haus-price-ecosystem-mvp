"""
СЕРВИС EMAIL РАССЫЛОК
Отправка email уведомлений партнерам и заказчикам
"""

import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.utils import formatdate
from typing import Dict, Any, List, Optional, Union
from datetime import datetime
import jinja2
import os

logger = logging.getLogger(__name__)

class EmailService:
    """Сервис для отправки email уведомлений"""
    
    def __init__(self, smtp_host: str, smtp_port: int, 
                 smtp_user: str, smtp_password: str,
                 email_from: str, template_dir: str = "templates/email"):
        self.smtp_host = smtp_host
        self.smtp_port = smtp_port
        self.smtp_user = smtp_user
        self.smtp_password = smtp_password
        self.email_from = email_from
        
        # Настройка Jinja2 для шаблонов
        template_loader = jinja2.FileSystemLoader(searchpath=template_dir)
        self.template_env = jinja2.Environment(
            loader=template_loader,
            autoescape=jinja2.select_autoescape(['html', 'xml'])
        )
        
        # Проверка подключения при инициализации
        self._test_connection()
    
    def _test_connection(self):
        """Тестирование подключения к SMTP серверу"""
        try:
            with smtplib.SMTP(self.smtp_host, self.smtp_port, timeout=10) as server:
                server.starttls()
                server.login(self.smtp_user, self.smtp_password)
            logger.info("SMTP connection test successful")
        except Exception as e:
            logger.error(f"SMTP connection test failed: {e}")
    
    def send_email(self, to_email: Union[str, List[str]], subject: str,
                  html_content: str, text_content: Optional[str] = None,
                  cc: Optional[List[str]] = None, bcc: Optional[List[str]] = None,
                  attachments: Optional[List[Dict]] = None) -> Dict[str, Any]:
        """Отправка email"""
        try:
            # Подготовка получателей
            if isinstance(to_email, str):
                to_emails = [to_email]
            else:
                to_emails = to_email
            
            # Создание сообщения
            msg = MIMEMultipart('alternative')
            msg['From'] = self.email_from
            msg['To'] = ', '.join(to_emails)
            msg['Subject'] = subject
            msg['Date'] = formatdate(localtime=True)
            
            if cc:
                msg['Cc'] = ', '.join(cc)
                to_emails.extend(cc)
            
            if bcc:
                to_emails.extend(bcc)
            
            # Текстовая часть
            if text_content:
                text_part = MIMEText(text_content, 'plain', 'utf-8')
                msg.attach(text_part)
            
            # HTML часть
            html_part = MIMEText(html_content, 'html', 'utf-8')
            msg.attach(html_part)
            
            # Подключение к SMTP серверу
            with smtplib.SMTP(self.smtp_host, self.smtp_port, timeout=30) as server:
                server.starttls()
                server.login(self.smtp_user, self.smtp_password)
                
                # Отправка
                server.send_message(msg, from_addr=self.email_from, to_addrs=to_emails)
            
            logger.info(f"Email sent to {', '.join(to_emails[:3])}...")
            
            return {
                'success': True,
                'to': to_emails,
                'subject': subject,
                'sent_at': datetime.utcnow().isoformat(),
                'message_id': msg['Message-ID'] if 'Message-ID' in msg else None
            }
            
        except smtplib.SMTPException as e:
            logger.error(f"SMTP error sending email: {e}")
            return {
                'success': False,
                'error': f'Ошибка SMTP при отправке email: {str(e)}'
            }
        except Exception as e:
            logger.error(f"Error sending email: {e}")
            return {
                'success': False,
                'error': f'Ошибка отправки email: {str(e)}'
            }
    
    def send_template_email(self, to_email: str, template_name: str,
                           template_data: Dict[str, Any],
                           subject: Optional[str] = None) -> Dict[str, Any]:
        """Отправка email на основе шаблона"""
        try:
            # Загрузка шаблона
            template = self.template_env.get_template(f"{template_name}.html")
            
            # Рендеринг HTML
            html_content = template.render(**template_data)
            
            # Генерация текстовой версии (упрощенная)
            text_content = self._html_to_text(html_content)
            
            # Тема письма
            if not subject and 'subject' in template_data:
                subject = template_data['subject']
            elif not subject:
                subject = "Сообщение от Дома-Цены.РФ"
            
            return self.send_email(
                to_email=to_email,
                subject=subject,
                html_content=html_content,
                text_content=text_content
            )
            
        except jinja2.TemplateError as e:
            logger.error(f"Template error for {template_name}: {e}")
            return {
                'success': False,
                'error': f'Ошибка шаблона: {str(e)}'
            }
        except Exception as e:
            logger.error(f"Error sending template email {template_name}: {e}")
            return {
                'success': False,
                'error': f'Ошибка отправки email: {str(e)}'
            }
    
    def send_partner_welcome_email(self, partner_email: str, partner_data: Dict[str, Any]) -> Dict[str, Any]:
        """Отправка приветственного письма партнеру"""
        template_data = {
            'subject': 'Добро пожаловать в экосистему Дома-Цены.РФ!',
            'partner_name': partner_data.get('contact_person'),
            'company_name': partner_data.get('company_name'),
            'partner_code': partner_data.get('partner_code'),
            'verification_status': partner_data.get('verification_status'),
            'dashboard_url': f"https://партнер.дома-цены.рф/{partner_data.get('partner_code')}",
            'support_email': 'support@дома-цены.рф',
            'current_year': datetime.now().year
        }
        
        return self.send_template_email(
            to_email=partner_email,
            template_name='partner_welcome',
            template_data=template_data
        )
    
    def send_partner_verification_email(self, partner_email: str, 
                                       partner_data: Dict[str, Any],
                                       status: str) -> Dict[str, Any]:
        """Отправка письма о верификации партнера"""
        status_texts = {
            'verified': 'ваш аккаунт успешно верифицирован!',
            'rejected': 'требуются дополнительные документы',
            'pending': 'ваша заявка на верификацию получена'
        }
        
        template_data = {
            'subject': f'Статус верификации: {status}',
            'partner_name': partner_data.get('contact_person'),
            'company_name': partner_data.get('company_name'),
            'status': status,
            'status_text': status_texts.get(status, status),
            'details': partner_data.get('rejection_reason', ''),
            'dashboard_url': f"https://партнер.дома-цены.рф/{partner_data.get('partner_code')}",
            'current_year': datetime.now().year
        }
        
        return self.send_template_email(
            to_email=partner_email,
            template_name='partner_verification',
            template_data=template_data
        )
    
    def send_lead_notification_email(self, partner_email: str, 
                                    lead_data: Dict[str, Any]) -> Dict[str, Any]:
        """Отправка уведомления о новой заявке"""
        template_data = {
            'subject': '🎯 Новая заявка от заказчика!',
            'partner_name': lead_data.get('partner_name'),
            'customer_name': lead_data.get('customer_name', 'Заказчик'),
            'project_type': lead_data.get('project_type'),
            'region': lead_data.get('region'),
            'budget': lead_data.get('budget'),
            'description': lead_data.get('description', ''),
            'lead_id': lead_data.get('lead_id'),
            'lead_url': f"https://партнер.дома-цены.рф/leads/{lead_data.get('lead_id')}",
            'response_deadline': (datetime.now() + timedelta(hours=24)).strftime('%d.%m.%Y %H:%M'),
            'current_year': datetime.now().year
        }
        
        return self.send_template_email(
            to_email=partner_email,
            template_name='lead_notification',
            template_data=template_data
        )
    
    def send_payment_confirmation_email(self, partner_email: str,
                                       payment_data: Dict[str, Any]) -> Dict[str, Any]:
        """Отправка подтверждения оплаты"""
        template_data = {
            'subject': '✅ Оплата получена',
            'partner_name': payment_data.get('partner_name'),
            'amount': payment_data.get('amount'),
            'currency': payment_data.get('currency', 'RUB'),
            'tariff_plan': payment_data.get('tariff_plan'),
            'payment_id': payment_data.get('payment_id'),
            'invoice_url': payment_data.get('invoice_url', '#'),
            'subscription_expires': payment_data.get('subscription_expires'),
            'current_year': datetime.now().year
        }
        
        return self.send_template_email(
            to_email=partner_email,
            template_name='payment_confirmation',
            template_data=template_data
        )
    
    def send_monthly_report_email(self, partner_email: str,
                                 report_data: Dict[str, Any]) -> Dict[str, Any]:
        """Отправка месячного отчета партнеру"""
        template_data = {
            'subject': f'📊 Отчет за {report_data.get("month")}',
            'partner_name': report_data.get('partner_name'),
            'company_name': report_data.get('company_name'),
            'month': report_data.get('month'),
            'leads_received': report_data.get('leads_received', 0),
            'leads_accepted': report_data.get('leads_accepted', 0),
            'response_rate': report_data.get('response_rate', 0),
            'rating_change': report_data.get('rating_change', 0),
            'top_regions': report_data.get('top_regions', []),
            'recommendations': report_data.get('recommendations', []),
            'dashboard_url': report_data.get('dashboard_url'),
            'current_year': datetime.now().year
        }
        
        return self.send_template_email(
            to_email=partner_email,
            template_name='monthly_report',
            template_data=template_data
        )
    
    def send_support_ticket_email(self, ticket_data: Dict[str, Any]) -> Dict[str, Any]:
        """Отправка письма в поддержку"""
        template_data = {
            'subject': f'📋 Запрос в поддержку: {ticket_data.get("subject")}',
            'customer_name': ticket_data.get('customer_name'),
            'customer_email': ticket_data.get('customer_email'),
            'ticket_id': ticket_data.get('ticket_id'),
            'subject': ticket_data.get('subject'),
            'message': ticket_data.get('message'),
            'priority': ticket_data.get('priority', 'normal'),
            'created_at': ticket_data.get('created_at'),
            'current_year': datetime.now().year
        }
        
        return self.send_template_email(
            to_email='support@дома-цены.рф',
            template_name='support_ticket',
            template_data=template_data
        )
    
    def _html_to_text(self, html: str) -> str:
        """Конвертация HTML в текстовый формат (упрощенная)"""
        import re
        
        # Удаляем HTML теги
        text = re.sub(r'<[^>]+>', ' ', html)
        
        # Заменяем HTML entities
        replacements = {
            '&nbsp;': ' ',
            '&amp;': '&',
            '&lt;': '<',
            '&gt;': '>',
            '&quot;': '"',
            '&#39;': "'"
        }
        
        for entity, replacement in replacements.items():
            text = text.replace(entity, replacement)
        
        # Удаляем лишние пробелы
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text
    
    def create_bulk_email_campaign(self, recipients: List[Dict[str, Any]],
                                 template_name: str, 
                                 template_data_func) -> Dict[str, Any]:
        """Создание массовой рассылки"""
        results = {
            'total': len(recipients),
            'sent': 0,
            'failed': 0,
            'errors': []
        }
        
        for recipient in recipients:
            try:
                # Получение данных шаблона для конкретного получателя
                data = template_data_func(recipient)
                
                # Отправка email
                result = self.send_template_email(
                    to_email=recipient['email'],
                    template_name=template_name,
                    template_data=data
                )
                
                if result.get('success'):
                    results['sent'] += 1
                else:
                    results['failed'] += 1
                    results['errors'].append({
                        'email': recipient['email'],
                        'error': result.get('error')
                    })
                
                # Небольшая задержка между отправками
                import time
                time.sleep(0.1)
                
            except Exception as e:
                results['failed'] += 1
                results['errors'].append({
                    'email': recipient.get('email', 'unknown'),
                    'error': str(e)
                })
        
        return results
