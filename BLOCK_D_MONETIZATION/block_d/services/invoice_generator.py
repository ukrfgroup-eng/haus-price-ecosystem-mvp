cat > BLOCK_D_MONETIZATION/block_d/services/invoice_generator.py << 'EOF'
"""
InvoiceGenerator - генерация счетов для блока D
"""

from datetime import datetime, timedelta

class InvoiceGenerator:
    """Генератор счетов блока D"""
    
    def __init__(self, config):
        self.config = config
        self._invoice_counter = 1
        print("✅ InvoiceGenerator инициализирован")
    
    def create_invoice(self, partner_id, client_info, items, tariff_code=None):
        """Создание счета"""
        invoice_number = self._generate_invoice_number(partner_id)
        
        # Рассчитываем сумму
        total_amount = sum(item.get('total', item.get('price', 0)) for item in items)
        
        invoice = {
            'invoice_number': invoice_number,
            'partner_id': partner_id,
            'client_info': client_info,
            'items': items,
            'total_amount': total_amount,
            'currency': 'RUB',
            'invoice_date': datetime.now().isoformat(),
            'due_date': (datetime.now() + timedelta(days=self.config.INVOICE['due_days'])).isoformat(),
            'status': 'pending',
            'tariff_code': tariff_code,
            'created_at': datetime.now().isoformat()
        }
        
        print(f"✅ Создан счет: {invoice_number}")
        return invoice
    
    def _generate_invoice_number(self, partner_id):
        """Генерация номера счета"""
        date_str = datetime.now().strftime('%y%m%d')
        seq = self._invoice_counter
        self._invoice_counter += 1
        return f"INV-{date_str}-{partner_id}-{seq:04d}"
    
    def get_invoice_html(self, invoice):
        """Получение HTML счета"""
        return f"""
        <html>
        <head><title>Счет №{invoice['invoice_number']}</title></head>
        <body>
            <h1>Счет на оплату №{invoice['invoice_number']}</h1>
            <p>Клиент: {invoice['client_info'].get('name', 'Не указано')}</p>
            <p>Сумма: {invoice['total_amount']} {invoice['currency']}</p>
            <p>Дата: {invoice['invoice_date'][:10]}</p>
        </body>
        </html>
        """
EOF
