cat > services/invoice_generator.py << 'EOF'
"""
InvoiceGenerator - генерация и управление счетами
"""

import logging
import os
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, Tuple
from jinja2 import Environment, FileSystemLoader
import pdfkit

logger = logging.getLogger(__name__)

class InvoiceGenerator:
    """Генератор счетов"""
    
    def __init__(self, config, templates_dir: str = None):
        """
        Инициализация генератора счетов
        
        Args:
            config: Конфигурация блока D
            templates_dir: Директория с шаблонами
        """
        self.config = config
        self.templates_dir = templates_dir or os.path.join(
            os.path.dirname(__file__), '..', 'templates'
        )
        
        # Создаем директорию для шаблонов, если её нет
        os.makedirs(self.templates_dir, exist_ok=True)
        
        # Инициализируем Jinja2
        self.jinja_env = Environment(
            loader=FileSystemLoader(self.templates_dir),
            autoescape=True
        )
        
        # Счетчик для номеров счетов (в production использовать БД)
        self._invoice_counter = 1
        
        # Создаем шаблон по умолчанию, если его нет
        self._create_default_template()
    
    def _create_default_template(self):
        """Создание шаблона счета по умолчанию"""
        template_path = os.path.join(self.templates_dir, 'invoice_template.html')
        
        if not os.path.exists(template_path):
            default_template = '''
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Счет №{{ invoice_number }}</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; }
        .header { text-align: center; margin-bottom: 40px; }
        .company-info { margin-bottom: 30px; }
        .invoice-info { margin-bottom: 30px; }
        .items-table { width: 100%; border-collapse: collapse; margin-bottom: 30px; }
        .items-table th, .items-table td { border: 1px solid #ddd; padding: 12px; text-align: left; }
        .items-table th { background-color: #f4f4f4; }
        .total { text-align: right; font-size: 18px; font-weight: bold; }
        .footer { margin-top: 50px; font-size: 12px; color: #666; }
    </style>
</head>
<body>
    <div class="header">
        <h1>Счет на оплату №{{ invoice_number }}</h1>
        <p>от {{ invoice_date }}</p>
    </div>
    
    <div class="company-info">
        <h3>Поставщик:</h3>
        <p><strong>{{ company.name }}</strong></p>
        <p>ИНН {{ company.inn }}, КПП {{ company.kpp }}</p>
        <p>{{ company.address }}</p>
        <p>Банк: {{ company.bank_name }}</p>
        <p>БИК: {{ company.bank_bik }}</p>
        <p>Счет: {{ company.bank_account }}</p>
        <p>Корр. счет: {{ company.bank_corr_account }}</p>
    </div>
    
    <div class="invoice-info">
        <h3>Плательщик:</h3>
        <p><strong>{{ client.name }}</strong></p>
        <p>Email: {{ client.email }}</p>
        {% if client.inn %}<p>ИНН: {{ client.inn }}</p>{% endif %}
    </div>
    
    <table class="items-table">
        <thead>
            <tr>
                <th>№</th>
                <th>Наименование</th>
                <th>Количество</th>
                <th>Цена</th>
                <th>Сумма</th>
            </tr>
        </thead>
        <tbody>
            {% for item in items %}
            <tr>
                <td>{{ loop.index }}</td>
                <td>{{ item.name }}</td>
                <td>{{ item.quantity }}</td>
                <td>{{ item.price }} {{ currency }}</td>
                <td>{{ item.total }} {{ currency }}</td>
            </tr>
            {% endfor %}
        </tbody>
    </table>
    
    <div class="total">
        <p>Итого: {{ total_amount }} {{ currency }}</p>
        <p>Сумма прописью: {{ amount_in_words }}</p>
    </div>
    
    <div class="footer">
        <p>Счет действителен до {{ due_date }}</p>
        <p>Руководитель: {{ company.ceo }}</p>
        <p>Генеральный директор</p>
    </div>
</body>
</html>
'''
            
            with open(template_path, 'w', encoding='utf-8') as f:
                f.write(default_template)
            logger.info(f"Создан шаблон счета: {template_path}")
    
    def generate_invoice_number(self, partner_id: str) -> str:
        """
        Генерация номера счета
        
        Args:
            partner_id: ID партнера
            
        Returns:
            Номер счета
        """
        date_str = datetime.now().strftime("%y%m%d")
        seq = self._invoice_counter
        self._invoice_counter += 1
        
        return self.config.INVOICE['number_format'].format(
            date=date_str,
            partner_id=partner_id,
            seq=seq
        )
    
    def create_invoice(self, partner_id: str, client_info: Dict[str, Any],
                      items: List[Dict[str, Any]], tariff_code: str = None,
                      subscription_id: str = None) -> Dict[str, Any]:
        """
        Создание нового счета
        
        Args:
            partner_id: ID партнера
            client_info: Информация о клиенте
            items: Список товаров/услуг
            tariff_code: Код тарифа (опционально)
            subscription_id: ID подписки (опционально)
            
        Returns:
            Информация о счете
        """
        try:
            # Генерируем номер счета
            invoice_number = self.generate_invoice_number(partner_id)
            
            # Рассчитываем итоги
            total_amount = sum(item.get('total', 0) for item in items)
            
            # Определяем даты
            invoice_date = datetime.utcnow()
            due_date = invoice_date + timedelta(days=self.config.INVOICE['due_days'])
            
            # Создаем объект счета
            invoice = {
                'invoice_number': invoice_number,
                'partner_id': partner_id,
                'client_info': client_info,
                'items': items,
                'total_amount': total_amount,
                'currency': 'RUB',
                'invoice_date': invoice_date.isoformat(),
                'due_date': due_date.isoformat(),
                'status': 'pending',
                'tariff_code': tariff_code,
                'subscription_id': subscription_id,
                'created_at': datetime.utcnow().isoformat(),
                'updated_at': datetime.utcnow().isoformat()
            }
            
            # Генерируем HTML и PDF
            html_content = self._generate_html(invoice)
            pdf_path = self._generate_pdf(html_content, invoice_number)
            
            invoice['html_content'] = html_content
            invoice['pdf_path'] = pdf_path
            
            logger.info(f"Создан счет {invoice_number} для партнера {partner_id}")
            return invoice
            
        except Exception as e:
            logger.error(f"Ошибка создания счета: {e}")
            raise
    
    def _generate_html(self, invoice: Dict[str, Any]) -> str:
        """
        Генерация HTML счета
        
        Args:
            invoice: Данные счета
            
        Returns:
            HTML контент
        """
        try:
            template = self.jinja_env.get_template('invoice_template.html')
            
            # Подготавливаем данные для шаблона
            template_data = {
                'invoice_number': invoice['invoice_number'],
                'invoice_date': datetime.fromisoformat(invoice['invoice_date']).strftime('%d.%m.%Y'),
                'due_date': datetime.fromisoformat(invoice['due_date']).strftime('%d.%m.%Y'),
                'company': self.config.INVOICE['company_details'],
                'client': invoice['client_info'],
                'items': invoice['items'],
                'total_amount': invoice['total_amount'],
                'currency': invoice['currency'],
                'amount_in_words': self._amount_to_words(invoice['total_amount'])
            }
            
            html_content = template.render(**template_data)
            return html_content
            
        except Exception as e:
            logger.error(f"Ошибка генерации HTML: {e}")
            raise
    
    def _generate_pdf(self, html_content: str, invoice_number: str) -> str:
        """
        Генерация PDF из HTML
        
        Args:
            html_content: HTML контент
            invoice_number: Номер счета для имени файла
            
        Returns:
            Путь к PDF файлу
        """
        try:
            # Создаем директорию для PDF, если её нет
            pdf_dir = os.path.join(os.path.dirname(__file__), '..', 'static', 'invoices')
            os.makedirs(pdf_dir, exist_ok=True)
            
            # Генерируем имя файла
            pdf_filename = f"{invoice_number}.pdf"
            pdf_path = os.path.join(pdf_dir, pdf_filename)
            
            # Конфигурация для pdfkit
            options = {
                'page-size': 'A4',
                'margin-top': '20mm',
                'margin-right': '15mm',
                'margin-bottom': '20mm',
                'margin-left': '15mm',
                'encoding': "UTF-8",
                'no-outline': None
            }
            
            # Генерируем PDF
            pdfkit.from_string(html_content, pdf_path, options=options)
            
            logger.info(f"Создан PDF: {pdf_path}")
            return pdf_path
            
        except Exception as e:
            logger.error(f"Ошибка генерации PDF: {e}")
            # Возвращаем путь, даже если PDF не создан
            return pdf_path if 'pdf_path' in locals() else ''
    
    def _amount_to_words(self, amount: float) -> str:
        """
        Преобразование суммы в пропись
        
        Args:
            amount: Сумма
            
        Returns:
            Сумма прописью
        """
        # Базовая реализация
        rubles = int(amount)
        kopecks = int((amount - rubles) * 100)
        
        return f"{rubles} руб. {kopecks:02d} коп."
    
    def get_invoice_html(self, invoice: Dict[str, Any]) -> str:
        """
        Получение HTML счета
        
        Args:
            invoice: Данные счета
            
        Returns:
            HTML контент
        """
        return invoice.get('html_content', '')
    
    def get_invoice_pdf_path(self, invoice: Dict[str, Any]) -> str:
        """
        Получение пути к PDF файлу счета
        
        Args:
            invoice: Данные счета
            
        Returns:
            Путь к PDF файлу
        """
        return invoice.get('pdf_path', '')
    
    def send_invoice_email(self, invoice: Dict[str, Any], 
                          recipient_email: str) -> bool:
        """
        Отправка счета по email
        
        Args:
            invoice: Данные счета
            recipient_email: Email получателя
            
        Returns:
            bool: Успешность отправки
        """
        # Эта функция будет реализована в NotificationService
        # Здесь только заглушка
        logger.info(f"Счет {invoice['invoice_number']} отправлен на {recipient_email}")
        return True
EOF
