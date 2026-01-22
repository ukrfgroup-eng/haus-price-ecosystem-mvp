"""
Revenue Analytics - система аналитики доходов
"""

import logging
from datetime import datetime, timedelta
from collections import defaultdict
from sqlalchemy import func, extract, and_
from backend.models import db, Partner, Payment, Subscription

logger = logging.getLogger(__name__)


class RevenueAnalytics:
    def __init__(self):
        self.tariff_plans = {
            'start': {'price': 0, 'name': 'Стартовый'},
            'professional': {'price': 5000, 'name': 'Профессиональный'},
            'business': {'price': 15000, 'name': 'Бизнес'}
        }
    
    def get_revenue_by_period(self, start_date, end_date):
        """Получение доходов за период"""
        try:
            payments = Payment.query.filter(
                and_(
                    Payment.status == 'completed',
                    Payment.created_at >= start_date,
                    Payment.created_at <= end_date
                )
            ).all()
            
            total_revenue = sum(p.amount for p in payments)
            
            # Группировка по дням
            daily_revenue = defaultdict(float)
            for payment in payments:
                day = payment.created_at.date()
                daily_revenue[day] += payment.amount
            
            # Группировка по тарифам
            revenue_by_tariff = defaultdict(float)
            for payment in payments:
                revenue_by_tariff[payment.tariff_plan] += payment.amount
            
            return {
                'total_revenue': total_revenue,
                'payment_count': len(payments),
                'average_payment': total_revenue / len(payments) if payments else 0,
                'daily_revenue': dict(daily_revenue),
                'revenue_by_tariff': dict(revenue_by_tariff),
                'period': {
                    'start': start_date.strftime('%Y-%m-%d'),
                    'end': end_date.strftime('%Y-%m-%d')
                }
            }
            
        except Exception as e:
            logger.error(f"Ошибка получения статистики доходов: {e}")
            return None
    
    def get_monthly_revenue(self, year=None, month=None):
        """Получение месячной статистики"""
        if not year:
            year = datetime.now().year
        if not month:
            month = datetime.now().month
        
        start_date = datetime(year, month, 1)
        if month == 12:
            end_date = datetime(year + 1, 1, 1) - timedelta(days=1)
        else:
            end_date = datetime(year, month + 1, 1) - timedelta(days=1)
        
        return self.get_revenue_by_period(start_date, end_date)
    
    def get_yearly_revenue(self, year=None):
        """Получение годовой статистики"""
        if not year:
            year = datetime.now().year
        
        start_date = datetime(year, 1, 1)
        end_date = datetime(year, 12, 31)
        
        return self.get_revenue_by_period(start_date, end_date)
    
    def get_partner_lifetime_value(self, partner_id):
        """Расчет LTV (Lifetime Value) партнера"""
        try:
            payments = Payment.query.filter(
                Payment.partner_id == partner_id,
                Payment.status == 'completed'
            ).all()
            
            if not payments:
                return {
                    'total_spent': 0,
                    'payment_count': 0,
                    'average_payment': 0,
                    'first_payment': None,
                    'last_payment': None,
                    'active_months': 0
                }
            
            total_spent = sum(p.amount for p in payments)
            first_payment = min(p.created_at for p in payments)
            last_payment = max(p.created_at for p in payments)
            
            # Расчет активных месяцев
            active_months = (last_payment.year - first_payment.year) * 12 + \
                           (last_payment.month - first_payment.month) + 1
            
            return {
                'total_spent': total_spent,
                'payment_count': len(payments),
                'average_payment': total_spent / len(payments),
                'first_payment': first_payment.strftime('%Y-%m-%d'),
                'last_payment': last_payment.strftime('%Y-%m-%d'),
                'active_months': active_months,
                'ltv': total_spent / active_months if active_months > 0 else 0
            }
            
        except Exception as e:
            logger.error(f"Ошибка расчета LTV для партнера {partner_id}: {e}")
            return None
    
    def get_churn_rate(self, period_days=30):
        """Расчет уровня оттока (Churn Rate)"""
        try:
            total_partners = Partner.query.filter(
                Partner.verification_status == 'verified',
                Partner.is_active == True
            ).count()
            
            if total_partners == 0:
                return {'churn_rate': 0, 'lost_partners': 0, 'total_partners': 0}
            
            cutoff_date = datetime.now() - timedelta(days=period_days)
            
            # Партнеры без платежей за период
            lost_partners = db.session.query(Partner).outerjoin(
                Payment, and_(
                    Partner.partner_id == Payment.partner_id,
                    Payment.status == 'completed',
                    Payment.created_at >= cutoff_date
                )
            ).filter(
                Partner.verification_status == 'verified',
                Partner.is_active == True,
                Payment.id.is_(None)
            ).count()
            
            churn_rate = (lost_partners / total_partners) * 100
            
            return {
                'churn_rate': churn_rate,
                'lost_partners': lost_partners,
                'total_partners': total_partners,
                'period_days': period_days
            }
            
        except Exception as e:
            logger.error(f"Ошибка расчета уровня оттока: {e}")
            return None
    
    def get_revenue_forecast(self, months=6):
        """Прогноз доходов на следующие месяцы"""
        try:
            # Анализ исторических данных за последние 12 месяцев
            end_date = datetime.now()
            start_date = end_date - timedelta(days=365)
            
            monthly_data = []
            current = start_date
            
            while current <= end_date:
                month_data = self.get_monthly_revenue(current.year, current.month)
                if month_data:
                    monthly_data.append({
                        'year': current.year,
                        'month': current.month,
                        'revenue': month_data['total_revenue'],
                        'growth': 0  # Будет рассчитано позже
                    })
                
                # Переход к следующему месяцу
                if current.month == 12:
                    current = datetime(current.year + 1, 1, 1)
                else:
                    current = datetime(current.year, current.month + 1, 1)
            
            # Расчет среднего роста
            if len(monthly_data) > 1:
                total_growth = 0
                for i in range(1, len(monthly_data)):
                    if monthly_data[i-1]['revenue'] > 0:
                        growth = ((monthly_data[i]['revenue'] - monthly_data[i-1]['revenue']) / 
                                 monthly_data[i-1]['revenue']) * 100
                        monthly_data[i]['growth'] = growth
                        total_growth += growth
                
                avg_growth = total_growth / (len(monthly_data) - 1)
            else:
                avg_growth = 5  # 5% по умолчанию
            
            # Прогноз
            forecast = []
            last_revenue = monthly_data[-1]['revenue'] if monthly_data else 100000
            current_date = datetime.now()
            
            for i in range(1, months + 1):
                if current_date.month == 12:
                    current_date = datetime(current_date.year + 1, 1, 1)
                else:
                    current_date = datetime(current_date.year, current_date.month + 1, 1)
                
                forecast_revenue = last_revenue * (1 + avg_growth/100)
                
                forecast.append({
                    'year': current_date.year,
                    'month': current_date.month,
                    'month_name': current_date.strftime('%B'),
                    'forecast_revenue': forecast_revenue,
                    'growth_rate': avg_growth
                })
                
                last_revenue = forecast_revenue
            
            return {
                'historical_data': monthly_data,
                'average_growth_rate': avg_growth,
                'forecast': forecast,
                'forecast_months': months
            }
            
        except Exception as e:
            logger.error(f"Ошибка прогнозирования доходов: {e}")
            return None
    
    def get_top_partners(self, limit=10, period_days=30):
        """Получение топовых партнеров по доходам"""
        try:
            cutoff_date = datetime.now() - timedelta(days=period_days)
            
            top_partners = db.session.query(
                Partner.company_name,
                Partner.partner_id,
                func.sum(Payment.amount).label('total_spent'),
                func.count(Payment.id).label('payment_count')
            ).join(
                Payment, Partner.partner_id == Payment.partner_id
            ).filter(
                Payment.status == 'completed',
                Payment.created_at >= cutoff_date
            ).group_by(
                Partner.id
            ).order_by(
                func.sum(Payment.amount).desc()
            ).limit(limit).all()
            
            return [
                {
                    'company_name': partner.company_name,
                    'partner_id': partner.partner_id,
                    'total_spent': partner.total_spent,
                    'payment_count': partner.payment_count,
                    'average_payment': partner.total_spent / partner.payment_count if partner.payment_count > 0 else 0
                }
                for partner in top_partners
            ]
            
        except Exception as e:
            logger.error(f"Ошибка получения топовых партнеров: {e}")
            return []
