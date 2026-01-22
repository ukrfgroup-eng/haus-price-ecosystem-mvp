"""
API эндпоинты для системы платежей
"""

from flask import Blueprint, request, jsonify, send_file
from backend.services.invoice_generator import InvoiceGenerator
from backend.services.revenue_analytics import RevenueAnalytics
from backend.models import db, Payment, Partner
from datetime import datetime, timedelta
import os

payment_bp = Blueprint('payment', __name__)
invoice_generator = InvoiceGenerator()
revenue_analytics = RevenueAnalytics()


@payment_bp.route('/api/v1/payments/create-invoice', methods=['POST'])
def create_invoice():
    """Создание счета для партнера"""
    data = request.json
    
    required_fields = ['partner_id', 'amount', 'tariff_plan']
    for field in required_fields:
        if not data.get(field):
            return jsonify({'error': f'Отсутствует обязательное поле: {field}'}), 400
    
    result = invoice_generator.create_invoice(
        partner_id=data['partner_id'],
        amount=data['amount'],
        tariff_plan=data['tariff_plan'],
        description=data.get('description', 'Оплата подписки')
    )
    
    if result:
        return jsonify({'success': True, 'data': result})
    else:
        return jsonify({'error': 'Не удалось создать счет'}), 500


@payment_bp.route('/api/v1/payments/invoice/<invoice_number>', methods=['GET'])
def get_invoice(invoice_number):
    """Получение информации о счете"""
    invoice_info = invoice_generator.get_invoice(invoice_number)
    
    if invoice_info:
        return jsonify({'success': True, 'data': invoice_info})
    else:
        return jsonify({'error': 'Счет не найден'}), 404


@payment_bp.route('/api/v1/payments/invoice/<invoice_number>/download', methods=['GET'])
def download_invoice(invoice_number):
    """Скачивание счета в формате HTML"""
    payment = Payment.query.filter_by(payment_number=invoice_number).first()
    
    if not payment or not payment.invoice_file:
        return jsonify({'error': 'Файл счета не найден'}), 404
    
    if os.path.exists(payment.invoice_file):
        return send_file(payment.invoice_file, as_attachment=True, download_name=f'{invoice_number}.html')
    else:
        return jsonify({'error': 'Файл счета не найден на сервере'}), 404


@payment_bp.route('/api/v1/analytics/revenue/monthly', methods=['GET'])
def get_monthly_revenue():
    """Получение месячной статистики доходов"""
    year = request.args.get('year', type=int)
    month = request.args.get('month', type=int)
    
    result = revenue_analytics.get_monthly_revenue(year, month)
    
    if result:
        return jsonify({'success': True, 'data': result})
    else:
        return jsonify({'error': 'Не удалось получить статистику'}), 500


@payment_bp.route('/api/v1/analytics/revenue/yearly', methods=['GET'])
def get_yearly_revenue():
    """Получение годовой статистики доходов"""
    year = request.args.get('year', type=int)
    
    result = revenue_analytics.get_yearly_revenue(year)
    
    if result:
        return jsonify({'success': True, 'data': result})
    else:
        return jsonify({'error': 'Не удалось получить статистику'}), 500


@payment_bp.route('/api/v1/analytics/partner/<partner_id>/ltv', methods=['GET'])
def get_partner_ltv(partner_id):
    """Получение LTV партнера"""
    result = revenue_analytics.get_partner_lifetime_value(partner_id)
    
    if result:
        return jsonify({'success': True, 'data': result})
    else:
        return jsonify({'error': 'Не удалось получить данные LTV'}), 500


@payment_bp.route('/api/v1/analytics/churn-rate', methods=['GET'])
def get_churn_rate():
    """Получение уровня оттока партнеров"""
    period_days = request.args.get('period_days', 30, type=int)
    
    result = revenue_analytics.get_churn_rate(period_days)
    
    if result:
        return jsonify({'success': True, 'data': result})
    else:
        return jsonify({'error': 'Не удалось рассчитать уровень оттока'}), 500


@payment_bp.route('/api/v1/analytics/forecast', methods=['GET'])
def get_revenue_forecast():
    """Получение прогноза доходов"""
    months = request.args.get('months', 6, type=int)
    
    result = revenue_analytics.get_revenue_forecast(months)
    
    if result:
        return jsonify({'success': True, 'data': result})
    else:
        return jsonify({'error': 'Не удалось построить прогноз'}), 500


@payment_bp.route('/api/v1/analytics/top-partners', methods=['GET'])
def get_top_partners():
    """Получение топовых партнеров"""
    limit = request.args.get('limit', 10, type=int)
    period_days = request.args.get('period_days', 30, type=int)
    
    result = revenue_analytics.get_top_partners(limit, period_days)
    
    return jsonify({'success': True, 'data': result})
