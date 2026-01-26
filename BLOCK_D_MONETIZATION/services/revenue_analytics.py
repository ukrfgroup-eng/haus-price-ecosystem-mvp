cat > services/revenue_analytics.py << 'EOF'
"""
RevenueAnalytics - аналитика доходов для блока D
Версия: 1.0.0
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from collections import defaultdict

logger = logging.getLogger(__name__)

class RevenueAnalytics:
    """Аналитика доходов блока D"""
    
    def __init__(self, config):
        """
        Инициализация аналитики блока D
        
        Args:
            config: Конфигурация блока D
        """
        self.config = config
        
        # Хранилище данных (в production - БД)
        self._payments = []
        self._subscriptions = []
        
        # Генерация тестовых данных для демонстрации
        self._generate_sample_data()
        
        logger.info("RevenueAnalytics блока D инициализирован")
    
    def _generate_sample_data(self):
        """Генерация тестовых данных для блока D"""
        logger.info("Блок D: Генерация тестовых данных аналитики")
        
        # Тестовые платежи
        for i in range(1, 31):
            self._payments.append({
                'payment_id': f'pay_d_{i}',
                'partner_id': f'partner_{i:03d}',
                'amount': 5000 if i % 3 == 0 else 15000 if i % 3 == 1 else 0,
                'currency': 'RUB',
                'status': 'completed',
                'tariff_code': 'professional' if i % 3 == 0 else 'business' if i % 3 == 1 else 'start',
                'created_at': (datetime.now() - timedelta(days=30-i)).isoformat(),
                'paid_at': (datetime.now() - timedelta(days=30-i)).isoformat(),
                'source': 'block_d'
            })
        
        # Тестовые подписки
        for i in range(1, 21):
            self._subscriptions.append({
                'subscription_id': f'sub_d_{i}',
                'partner_id': f'partner_{i:03d}',
                'tariff_code': 'professional' if i % 3 == 0 else 'business' if i % 3 == 1 else 'start',
                'status': 'active',
                'price': 5000 if i % 3 == 0 else 15000 if i % 3 == 1 else 0,
                'start_date': (datetime.now() - timedelta(days=30-i)).isoformat(),
                'expires_at': (datetime.now() + timedelta(days=30-i)).isoformat(),
                'source': 'block_d'
            })
    
    def calculate_mrr(self) -> Dict[str, Any]:
        """
        Расчет Monthly Recurring Revenue (MRR) для блока D
        
        Returns:
            MRR метрики
        """
        try:
            # Фильтруем активные подписки блока D
            active_subscriptions = [
                sub for sub in self._subscriptions 
                if sub['status'] == 'active' and sub.get('source') == 'block_d'
            ]
            
            # Группируем по тарифам
            mrr_by_tariff = defaultdict(float)
            for sub in active_subscriptions:
                tariff = sub['tariff_code']
                mrr_by_tariff[tariff] += sub['price']
            
            total_mrr = sum(mrr_by_tariff.values())
            
            # Формируем breakdown
            breakdown = []
            for tariff, revenue in mrr_by_tariff.items():
                percentage = (revenue / total_mrr * 100) if total_mrr > 0 else 0
                breakdown.append({
                    'tariff': tariff,
                    'revenue': round(revenue, 2),
                    'percentage': round(percentage, 2)
                })
            
            result = {
                'current_mrr': round(total_mrr, 2),
                'currency': 'RUB',
                'subscription_count': len(active_subscriptions),
                'breakdown': breakdown,
                'calculated_at': datetime.utcnow().isoformat(),
                'source': 'block_d'
            }
            
            logger.info(f"Блок D: Рассчитан MRR: {total_mrr} RUB")
            return result
            
        except Exception as e:
            logger.error(f"Блок D: Ошибка расчета MRR: {e}")
            return {
                'current_mrr': 0,
                'currency': 'RUB',
                'error': str(e),
                'source': 'block_d'
            }
    
    def calculate_churn_rate(self, period_days: int = 30) -> Dict[str, Any]:
        """
        Расчет уровня оттока (Churn Rate) для блока D
        
        Args:
            period_days: Период для расчета
            
        Returns:
            Метрики оттока
        """
        try:
            # В реальной системе здесь была бы логика расчета оттока
            # Для демонстрации используем фиксированные значения
            
            start_date = datetime.now() - timedelta(days=period_days)
            
            # Имитация данных
            total_customers_start = 100
            churned_customers = 8
            new_customers = 15
            total_customers_end = 107
            
            churn_rate = (churned_customers / total_customers_start) * 100
            
            result = {
                'period_days': period_days,
                'start_date': start_date.date().isoformat(),
                'end_date': datetime.now().date().isoformat(),
                'total_customers_start': total_customers_start,
                'total_customers_end': total_customers_end,
                'churned_customers': churned_customers,
                'new_customers': new_customers,
                'churn_rate': round(churn_rate, 2),
                'net_growth': total_customers_end - total_customers_start,
                'growth_rate': round(((total_customers_end - total_customers_start) / total_customers_start) * 100, 2),
                'calculated_at': datetime.utcnow().isoformat(),
                'source': 'block_d'
            }
            
            logger.info(f"Блок D: Рассчитан Churn Rate: {churn_rate}%")
            return result
            
        except Exception as e:
            logger.error(f"Блок D: Ошибка расчета Churn Rate: {e}")
            return {
                'churn_rate': 0,
                'error': str(e),
                'source': 'block_d'
            }
    
    def get_daily_revenue(self, start_date: datetime = None,
                         end_date: datetime = None) -> List[Dict]:
        """
        Получение ежедневной выручки блока D
        
        Args:
            start_date: Начальная дата
            end_date: Конечная дата
            
        Returns:
            Данные по дням
        """
        if not start_date:
            start_date = datetime.now() - timedelta(days=30)
        if not end_date:
            end_date = datetime.now()
        
        # Фильтруем платежи по дате и статусу
        filtered_payments = []
        for payment in self._payments:
            if payment.get('source') != 'block_d':
                continue
            
            if payment['status'] not in ['completed', 'succeeded']:
                continue
            
            paid_at = datetime.fromisoformat(payment['paid_at'])
            if start_date <= paid_at <= end_date:
                filtered_payments.append(payment)
        
        # Группируем по дням
        revenue_by_day = defaultdict(lambda: {
            'date': '',
            'revenue': 0,
            'payment_count': 0,
            'avg_ticket': 0
        })
        
        for payment in filtered_payments:
            paid_at = datetime.fromisoformat(payment['paid_at'])
            day_key = paid_at.date().isoformat()
            
            if not revenue_by_day[day_key]['date']:
                revenue_by_day[day_key]['date'] = day_key
            
            revenue_by_day[day_key]['revenue'] += payment['amount']
            revenue_by_day[day_key]['payment_count'] += 1
        
        # Рассчитываем средний чек
        for day_data in revenue_by_day.values():
            if day_data['payment_count'] > 0:
                day_data['avg_ticket'] = round(day_data['revenue'] / day_data['payment_count'], 2)
        
        # Преобразуем в список и сортируем
        result = sorted(revenue_by_day.values(), key=lambda x: x['date'])
        
        logger.info(f"Блок D: Получена выручка за {len(result)} дней")
        return result
    
    def get_top_partners(self, limit: int = 10, 
                        period_days: int = 30) -> List[Dict]:
        """
        Топ партнеров по объему платежей (блок D)
        
        Args:
            limit: Количество партнеров в топе
            period_days: Период анализа
            
        Returns:
            Список партнеров
        """
        try:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=period_days)
            
            # Группируем платежи по партнерам
            partner_revenue = defaultdict(lambda: {
                'revenue': 0,
                'payment_count': 0,
                'last_payment': None
            })
            
            for payment in self._payments:
                if payment.get('source') != 'block_d':
                    continue
                
                if payment['status'] not in ['completed', 'succeeded']:
                    continue
                
                paid_at = datetime.fromisoformat(payment['paid_at'])
                if not (start_date <= paid_at <= end_date):
                    continue
                
                partner_id = payment['partner_id']
                partner_revenue[partner_id]['revenue'] += payment['amount']
                partner_revenue[partner_id]['payment_count'] += 1
                
                # Обновляем последний платеж
                current_last = partner_revenue[partner_id]['last_payment']
                if not current_last or paid_at > datetime.fromisoformat(current_last):
                    partner_revenue[partner_id]['last_payment'] = paid_at.isoformat()
            
            # Сортируем по выручке
            sorted_partners = sorted(
                partner_revenue.items(),
                key=lambda x: x[1]['revenue'],
                reverse=True
            )[:limit]
            
            # Формируем результат
            result = []
            for rank, (partner_id, data) in enumerate(sorted_partners, 1):
                result.append({
                    'rank': rank,
                    'partner_id': partner_id,
                    'revenue': round(data['revenue'], 2),
                    'payment_count': data['payment_count'],
                    'avg_payment': round(data['revenue'] / data['payment_count'], 2) if data['payment_count'] > 0 else 0,
                    'last_payment': data['last_payment'],
                    'source': 'block_d'
                })
            
            logger.info(f"Блок D: Сформирован топ {len(result)} партнеров")
            return result
            
        except Exception as e:
            logger.error(f"Блок D: Ошибка формирования топа партнеров: {e}")
            return []
    
    def forecast_revenue(self, months: int = 3) -> Dict[str, Any]:
        """
        Прогноз доходов для блока D
        
        Args:
            months: Количество месяцев для прогноза
            
        Returns:
            Прогноз доходов
        """
        try:
            # Получаем исторические данные
            historical = self.get_daily_revenue(
                start_date=datetime.now() - timedelta(days=90),
                end_date=datetime.now()
            )
            
            if not historical:
                return {
                    'forecast_months': months,
                    'historical_months': 3,
                    'current_mrr': 0,
                    'trend': 'no_data',
                    'forecast': [],
                    'currency': 'RUB',
                    'source': 'block_d'
                }
            
            # Извлекаем выручку
            revenues = [day['revenue'] for day in historical]
            
            # Простой прогноз: средний рост 5% в месяц
            current_mrr = self.calculate_mrr()['current_mrr']
            monthly_growth_rate = 0.05  # 5%
            
            # Прогноз на будущие месяцы
            forecast = []
            current_date = datetime.now()
            
            for i in range(1, months + 1):
                month_date = current_date + timedelta(days=30 * i)
                predicted_revenue = current_mrr * (1 + monthly_growth_rate) ** i
                
                forecast.append({
                    'month': month_date.strftime("%Y-%m"),
                    'predicted_revenue': round(predicted_revenue, 2),
                    'confidence_interval': round(predicted_revenue * 0.15, 2),  # ±15%
                    'growth_rate': monthly_growth_rate * 100
                })
            
            result = {
                'forecast_months': months,
                'historical_months': 3,
                'current_mrr': current_mrr,
                'trend': 'growing',
                'forecast': forecast,
                'currency': 'RUB',
                'calculated_at': datetime.utcnow().isoformat(),
                'source': 'block_d'
            }
            
            logger.info(f"Блок D: Сформирован прогноз на {months} месяцев")
            return result
            
        except Exception as e:
            logger.error(f"Блок D: Ошибка прогноза доходов: {e}")
            return {
                'error': str(e),
                'source': 'block_d'
            }
    
    def generate_report(self, report_type: str = 'monthly') -> Dict[str, Any]:
        """
        Генерация отчета блока D
        
        Args:
            report_type: Тип отчета (daily, weekly, monthly)
            
        Returns:
            Отчет
        """
        try:
            if report_type == 'daily':
                period_days = 1
            elif report_type == 'weekly':
                period_days = 7
            elif report_type == 'monthly':
                period_days = 30
            else:
                period_days = 30
            
            report = {
                'report_type': report_type,
                'period_days': period_days,
                'generated_at': datetime.utcnow().isoformat(),
                'mrr': self.calculate_mrr(),
                'churn_rate': self.calculate_churn_rate(period_days),
                'daily_revenue': self.get_daily_revenue(
                    start_date=datetime.now() - timedelta(days=period_days),
                    end_date=datetime.now()
                ),
                'top_partners': self.get_top_partners(limit=5, period_days=period_days),
                'revenue_forecast': self.forecast_revenue(months=3),
                'summary': {
                    'total_revenue': sum(day['revenue'] for day in self.get_daily_revenue(
                        start_date=datetime.now() - timedelta(days=period_days),
                        end_date=datetime.now()
                    )),
                    'active_partners': len(set(
                        p['partner_id'] for p in self._payments 
                        if p.get('source') == 'block_d' and p['status'] == 'completed'
                    )),
                    'avg_revenue_per_partner': 0,
                    'source': 'block_d'
                }
            }
            
            # Рассчитываем среднюю выручку на партнера
            total_revenue = report['summary']['total_revenue']
            active_partners = report['summary']['active_partners']
            if active_partners > 0:
                report['summary']['avg_revenue_per_partner'] = round(total_revenue / active_partners, 2)
            
            logger.info(f"Блок D: Сгенерирован отчет типа '{report_type}'")
            return report
            
        except Exception as e:
            logger.error(f"Блок D: Ошибка генерации отчета: {e}")
            return {
                'error': str(e),
                'source': 'block_d'
            }

# Экспорт
__all__ = ['RevenueAnalytics']
EOF
