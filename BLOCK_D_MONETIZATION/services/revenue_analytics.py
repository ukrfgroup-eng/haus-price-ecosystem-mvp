cat > services/revenue_analytics.py << 'EOF'
"""
RevenueAnalytics - аналитика доходов и метрик
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple
import statistics
from collections import defaultdict

logger = logging.getLogger(__name__)

class RevenueAnalytics:
    """Аналитика доходов и метрик бизнеса"""
    
    def __init__(self, config):
        """
        Инициализация аналитики
        
        Args:
            config: Конфигурация блока D
        """
        self.config = config
        
        # В production данные будут браться из БД
        self._sample_data = self._generate_sample_data()
    
    def _generate_sample_data(self) -> List[Dict]:
        """Генерация тестовых данных для демонстрации"""
        data = []
        start_date = datetime.now() - timedelta(days=365)
        
        for i in range(365):
            date = start_date + timedelta(days=i)
            
            # Имитация сезонности (больше доходов в рабочие дни)
            is_weekend = date.weekday() >= 5
            base_revenue = 50000 if not is_weekend else 15000
            
            # Имитация роста
            growth_factor = 1 + (i / 365) * 0.5  # 50% рост за год
            
            # Случайные колебания
            random_factor = 0.8 + (i % 10) * 0.04
            
            revenue = base_revenue * growth_factor * random_factor
            
            data.append({
                'date': date.date().isoformat(),
                'revenue': round(revenue, 2),
                'new_customers': 3 if not is_weekend else 1,
                'churned_customers': 1 if i % 30 == 0 else 0,
                'active_subscriptions': 100 + i // 3
            })
        
        return data
    
    def get_daily_revenue(self, start_date: datetime = None,
                         end_date: datetime = None) -> List[Dict]:
        """
        Получение ежедневной выручки
        
        Args:
            start_date: Начальная дата
            end_date: Конечная дата
            
        Returns:
            Список данных по дням
        """
        if not start_date:
            start_date = datetime.now() - timedelta(days=30)
        if not end_date:
            end_date = datetime.now()
        
        filtered_data = []
        for entry in self._sample_data:
            entry_date = datetime.fromisoformat(entry['date']).date()
            if start_date.date() <= entry_date <= end_date.date():
                filtered_data.append(entry)
        
        return sorted(filtered_data, key=lambda x: x['date'])
    
    def calculate_mrr(self) -> Dict[str, Any]:
        """
        Расчет Monthly Recurring Revenue (MRR)
        
        Returns:
            Dict с MRR метриками
        """
        # В production брать данные из подписок
        current_month = datetime.now().strftime("%Y-%m")
        
        # Имитация данных
        subscriptions = [
            {'tariff': 'start', 'price': 0, 'count': 50},
            {'tariff': 'professional', 'price': 5000, 'count': 30},
            {'tariff': 'business', 'price': 15000, 'count': 20}
        ]
        
        mrr = sum(sub['price'] * sub['count'] for sub in subscriptions)
        
        # Расчет изменений
        prev_mrr = mrr * 0.95  # Имитация роста 5%
        
        return {
            'current_mrr': round(mrr, 2),
            'previous_mrr': round(prev_mrr, 2),
            'growth_amount': round(mrr - prev_mrr, 2),
            'growth_percentage': round(((mrr - prev_mrr) / prev_mrr) * 100, 2) if prev_mrr > 0 else 0,
            'breakdown': subscriptions,
            'currency': 'RUB',
            'calculated_at': datetime.utcnow().isoformat()
        }
    
    def calculate_churn_rate(self, period_days: int = 30) -> Dict[str, Any]:
        """
        Расчет уровня оттока (Churn Rate)
        
        Args:
            period_days: Период для расчета
            
        Returns:
            Dict с метриками оттока
        """
        end_date = datetime.now()
        start_date = end_date - timedelta(days=period_days)
        
        # Имитация данных
        total_customers_start = 150
        total_customers_end = 160
        churned_customers = 12
        
        churn_rate = (churned_customers / total_customers_start) * 100
        
        return {
            'period_days': period_days,
            'start_date': start_date.date().isoformat(),
            'end_date': end_date.date().isoformat(),
            'total_customers_start': total_customers_start,
            'total_customers_end': total_customers_end,
            'churned_customers': churned_customers,
            'new_customers': total_customers_end - total_customers_start + churned_customers,
            'churn_rate': round(churn_rate, 2),
            'net_growth': total_customers_end - total_customers_start,
            'growth_rate': round(((total_customers_end - total_customers_start) / total_customers_start) * 100, 2),
            'calculated_at': datetime.utcnow().isoformat()
        }
    
    def calculate_ltv(self, period_months: int = 12) -> Dict[str, Any]:
        """
        Расчет Lifetime Value (LTV)
        
        Args:
            period_months: Период для расчета в месяцах
            
        Returns:
            Dict с LTV метриками
        """
        # Имитация данных
        avg_revenue_per_user = 7500  # Средний доход с пользователя в месяц
        avg_lifespan_months = 8.5    # Средняя продолжительность жизни клиента
        
        ltv = avg_revenue_per_user * avg_lifespan_months
        
        # Расчет CAC (Customer Acquisition Cost)
        cac = 25000  # Имитация
        
        return {
            'period_months': period_months,
            'avg_revenue_per_user': avg_revenue_per_user,
            'avg_lifespan_months': round(avg_lifespan_months, 2),
            'ltv': round(ltv, 2),
            'cac': cac,
            'ltv_to_cac_ratio': round(ltv / cac, 2),
            'currency': 'RUB',
            'calculated_at': datetime.utcnow().isoformat()
        }
    
    def forecast_revenue(self, months: int = 3) -> Dict[str, Any]:
        """
        Прогноз доходов на будущие периоды
        
        Args:
            months: Количество месяцев для прогноза
            
        Returns:
            Dict с прогнозом
        """
        # Простая линейная регрессия на основе исторических данных
        historical = self.get_daily_revenue(
            start_date=datetime.now() - timedelta(days=180),
            end_date=datetime.now()
        )
        
        if not historical:
            return {'error': 'Недостаточно данных для прогноза'}
        
        # Извлекаем выручку
        revenues = [day['revenue'] for day in historical]
        
        # Расчет тренда
        if len(revenues) >= 2:
            # Простой линейный тренд
            x = list(range(len(revenues)))
            slope = self._linear_regression_slope(x, revenues)
            
            # Прогноз на будущие месяцы
            forecast = []
            current_date = datetime.now()
            
            for i in range(months):
                month_date = current_date + timedelta(days=30 * (i + 1))
                predicted_revenue = revenues[-1] + slope * (len(revenues) + i)
                
                forecast.append({
                    'month': month_date.strftime("%Y-%m"),
                    'predicted_revenue': round(predicted_revenue, 2),
                    'confidence_interval': round(predicted_revenue * 0.1, 2)  # ±10%
                })
        else:
            forecast = []
        
        return {
            'forecast_months': months,
            'historical_months': 6,
            'current_mrr': self.calculate_mrr()['current_mrr'],
            'trend': 'growing' if slope > 0 else 'declining' if slope < 0 else 'stable',
            'forecast': forecast,
            'currency': 'RUB',
            'calculated_at': datetime.utcnow().isoformat()
        }
    
    def get_top_partners(self, limit: int = 10, 
                        period_days: int = 30) -> List[Dict]:
        """
        Получение топ партнеров по объему платежей
        
        Args:
            limit: Количество партнеров в топе
            period_days: Период для анализа
            
        Returns:
            Список топ партнеров
        """
        # Имитация данных партнеров
        partners = []
        for i in range(1, 31):
            revenue = 50000 + i * 10000 + (i % 5) * 25000
            partners.append({
                'partner_id': f'partner_{i:03d}',
                'partner_name': f'Партнер {i}',
                'revenue': revenue,
                'subscription_tier': 'business' if i <= 5 else 'professional' if i <= 15 else 'start',
                'payment_count': 12 + (i % 6),
                'last_payment_date': (datetime.now() - timedelta(days=i % 30)).isoformat()
            })
        
        # Сортировка по выручке
        top_partners = sorted(partners, key=lambda x: x['revenue'], reverse=True)[:limit]
        
        # Добавляем ранги
        for i, partner in enumerate(top_partners, 1):
            partner['rank'] = i
            partner['revenue_share'] = round(
                (partner['revenue'] / sum(p['revenue'] for p in top_partners)) * 100, 2
            )
        
        return top_partners
    
    def analyze_seasonality(self) -> Dict[str, Any]:
        """
        Анализ сезонности спроса
        
        Returns:
            Dict с анализом сезонности
        """
        # Агрегация по месяцам
        monthly_data = defaultdict(lambda: {'revenue': 0, 'count': 0})
        
        for entry in self._sample_data:
            date = datetime.fromisoformat(entry['date'])
            month_key = date.strftime("%Y-%m")
            monthly_data[month_key]['revenue'] += entry['revenue']
            monthly_data[month_key]['count'] += 1
        
        # Преобразование в список
        seasonality = []
        for month, data in monthly_data.items():
            seasonality.append({
                'month': month,
                'avg_daily_revenue': round(data['revenue'] / data['count'], 2),
                'total_revenue': round(data['revenue'], 2),
                'day_count': data['count']
            })
        
        # Сортировка по месяцам
        seasonality.sort(key=lambda x: x['month'])
        
        # Расчет сезонных коэффициентов
        if seasonality:
            avg_revenue = sum(s['avg_daily_revenue'] for s in seasonality) / len(seasonality)
            
            for s in seasonality:
                s['seasonality_factor'] = round(s['avg_daily_revenue'] / avg_revenue, 3)
        
        return {
            'analysis_period': 'year',
            'total_months': len(seasonality),
            'avg_daily_revenue': round(avg_revenue, 2) if seasonality else 0,
            'seasonality': seasonality,
            'peak_month': max(seasonality, key=lambda x: x['avg_daily_revenue']) if seasonality else None,
            'low_month': min(seasonality, key=lambda x: x['avg_daily_revenue']) if seasonality else None,
            'calculated_at': datetime.utcnow().isoformat()
        }
    
    def generate_report(self, report_type: str = 'monthly') -> Dict[str, Any]:
        """
        Генерация отчета
        
        Args:
            report_type: Тип отчета (daily, weekly, monthly, quarterly)
            
        Returns:
            Dict с отчетом
        """
        if report_type == 'daily':
            period_days = 1
        elif report_type == 'weekly':
            period_days = 7
        elif report_type == 'monthly':
            period_days = 30
        elif report_type == 'quarterly':
            period_days = 90
        else:
            period_days = 30
        
        return {
            'report_type': report_type,
            'period_days': period_days,
            'generated_at': datetime.utcnow().isoformat(),
            'mrr': self.calculate_mrr(),
            'churn_rate': self.calculate_churn_rate(period_days),
            'ltv': self.calculate_ltv(),
            'top_partners': self.get_top_partners(limit=5),
            'revenue_forecast': self.forecast_revenue(months=3),
            'seasonality': self.analyze_seasonality() if report_type == 'yearly' else None,
            'summary': self._generate_summary()
        }
    
    def _generate_summary(self) -> Dict[str, Any]:
        """Генерация краткого summary"""
        mrr = self.calculate_mrr()
        churn = self.calculate_churn_rate()
        ltv = self.calculate_ltv()
        
        return {
            'current_mrr': mrr['current_mrr'],
            'mrr_growth': mrr['growth_percentage'],
            'churn_rate': churn['churn_rate'],
            'ltv': ltv['ltv'],
            'healthy_business': ltv['ltv_to_cac_ratio'] > 3 and churn['churn_rate'] < 5,
            'key_metrics': {
                'mrr_target': 1000000,  # Целевой MRR
                'churn_target': 3.0,    # Целевой уровень оттока
                'ltv_target': 100000    # Целевой LTV
            }
        }
    
    def _linear_regression_slope(self, x: List, y: List) -> float:
        """Расчет наклона линейной регрессии"""
        if len(x) != len(y) or len(x) < 2:
            return 0
        
        n = len(x)
        sum_x = sum(x)
        sum_y = sum(y)
        sum_xy = sum(xi * yi for xi, yi in zip(x, y))
        sum_x2 = sum(xi * xi for xi in x)
        
        try:
            slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x * sum_x)
        except ZeroDivisionError:
            slope = 0
        
        return slope
EOF
