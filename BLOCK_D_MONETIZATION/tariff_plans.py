"""
МОДЕЛИ ТАРИФОВ ДЛЯ ПАРТНЕРОВ
Согласно ТЗ: МОДЕЛИ ТАРИФОВ
"""

from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from enum import Enum

class TariffTier(Enum):
    """Уровни тарифов"""
    FREE = "free"
    START = "start"
    BASIC = "basic"
    PREMIUM = "premium"
    BUSINESS = "business"

class BillingPeriod(Enum):
    """Периоды биллинга"""
    MONTHLY = "monthly"
    YEARLY = "yearly"
    QUARTERLY = "quarterly"

# Конфигурация тарифных планов согласно ТЗ
TARIFF_PLANS = {
    TariffTier.FREE.value: {
        'name': 'Бесплатный',
        'description': 'Базовый доступ для ознакомления',
        'price': 0,
        'currency': 'RUB',
        'leads_per_month': 3,
        'max_active_projects': 1,
        'features': [
            'basic_listing',
            'email_notifications',
            'profile_creation'
        ],
        'verification': 'standard',
        'support': 'email_only',
        'analytics': 'basic',
        'placement_priority': 3,
        'commission_rate': 0.15,  # 15% комиссия
        'min_contract_amount': 0
    },
    
    TariffTier.START.value: {
        'name': 'Старт',
        'description': 'Для начинающих подрядчиков',
        'price': 2500,
        'currency': 'RUB',
        'leads_per_month': 10,
        'max_active_projects': 3,
        'features': [
            'priority_listing',
            'phone_notifications',
            'basic_analytics',
            'profile_highlight'
        ],
        'verification': 'priority',
        'support': 'priority_email',
        'analytics': 'advanced',
        'placement_priority': 2,
        'commission_rate': 0.10,  # 10% комиссия
        'min_contract_amount': 100000
    },
    
    TariffTier.BASIC.value: {
        'name': 'Базовый',
        'description': 'Для активно работающих компаний',
        'price': 5000,
        'currency': 'RUB',
        'leads_per_month': 25,
        'max_active_projects': 10,
        'features': [
            'top_placement',
            'push_notifications',
            'advanced_analytics',
            'dedicated_support',
            'custom_profile',
            'portfolio_showcase'
        ],
        'verification': 'express',
        'support': 'phone_support',
        'analytics': 'premium',
        'placement_priority': 1,
        'commission_rate': 0.07,  # 7% комиссия
        'min_contract_amount': 500000
    },
    
    TariffTier.PREMIUM.value: {
        'name': 'Премиум',
        'description': 'Для ведущих компаний рынка',
        'price': 15000,
        'currency': 'RUB',
        'leads_per_month': 50,
        'max_active_projects': 25,
        'features': [
            'featured_placement',
            'instant_notifications',
            'ai_analytics',
            'personal_manager',
            'custom_integrations',
            'api_access',
            'white_label'
        ],
        'verification': 'instant',
        'support': 'dedicated_manager',
        'analytics': 'ai_powered',
        'placement_priority': 0,
        'commission_rate': 0.05,  # 5% комиссия
        'min_contract_amount': 2000000
    },
    
    TariffTier.BUSINESS.value: {
        'name': 'Бизнес',
        'description': 'Для крупных строительных компаний',
        'price': 30000,
        'currency': 'RUB',
        'leads_per_month': 100,
        'max_active_projects': 50,
        'features': [
            'exclusive_placement',
            'enterprise_analytics',
            'custom_development',
            'multi_user_access',
            'sla_guarantee',
            'market_research'
        ],
        'verification': 'enterprise',
        'support': '24/7_priority',
        'analytics': 'enterprise',
        'placement_priority': -1,  # Высший приоритет
        'commission_rate': 0.03,  # 3% комиссия
        'min_contract_amount': 5000000
    }
}

class TariffManager:
    """Менеджер тарифных планов и расчетов"""
    
    def __init__(self):
        self.plans = TARIFF_PLANS
    
    def get_tariff(self, tariff_name: str) -> Optional[Dict[str, Any]]:
        """Получение информации о тарифе"""
        tariff = self.plans.get(tariff_name)
        if tariff:
            return {**tariff, 'code': tariff_name}
        return None
    
    def get_all_tariffs(self) -> Dict[str, Dict[str, Any]]:
        """Получение всех тарифных планов"""
        return self.plans
    
    def calculate_price(self, tariff_name: str, period: str = 'monthly') -> Dict[str, Any]:
        """Расчет стоимости тарифа с учетом периода"""
        tariff = self.get_tariff(tariff_name)
        if not tariff:
            return {'success': False, 'error': 'Тариф не найден'}
        
        base_price = tariff['price']
        
        # Расчет с учетом периода
        if period == 'yearly':
            final_price = base_price * 10  # 2 месяца в подарок
            discount = (base_price * 12 - final_price) / (base_price * 12) * 100
        elif period == 'quarterly':
            final_price = base_price * 3
            discount = 0
        else:  # monthly
            final_price = base_price
            discount = 0
        
        return {
            'success': True,
            'tariff': tariff_name,
            'period': period,
            'base_price': base_price,
            'final_price': final_price,
            'currency': tariff['currency'],
            'discount_percentage': round(discount, 2),
            'discount_amount': base_price * 12 - final_price if period == 'yearly' else 0,
            'period_text': self._get_period_text(period)
        }
    
    def compare_tariffs(self, tariff1: str, tariff2: str) -> Dict[str, Any]:
        """Сравнение двух тарифных планов"""
        t1 = self.get_tariff(tariff1)
        t2 = self.get_tariff(tariff2)
        
        if not t1 or not t2:
            return {'success': False, 'error': 'Один из тарифов не найден'}
        
        comparison = {
            'tariff1': t1['name'],
            'tariff2': t2['name'],
            'price_difference': t2['price'] - t1['price'],
            'leads_difference': t2['leads_per_month'] - t1['leads_per_month'],
            'features_difference': {
                'only_in_tariff1': list(set(t1['features']) - set(t2['features'])),
                'only_in_tariff2': list(set(t2['features']) - set(t1['features']))
            },
            'recommendation': self._get_recommendation(t1, t2)
        }
        
        return {'success': True, 'comparison': comparison}
    
    def get_recommended_tariff(self, 
                              monthly_volume: float, 
                              project_count: int,
                              company_size: str = 'small') -> Dict[str, Any]:
        """Рекомендация тарифа на основе параметров компании"""
        
        # Логика рекомендации
        if monthly_volume > 5000000 or project_count > 20:
            recommended = TariffTier.BUSINESS.value
        elif monthly_volume > 2000000 or project_count > 10:
            recommended = TariffTier.PREMIUM.value
        elif monthly_volume > 500000 or project_count > 5:
            recommended = TariffTier.BASIC.value
        elif monthly_volume > 100000 or project_count > 2:
            recommended = TariffTier.START.value
        else:
            recommended = TariffTier.FREE.value
        
        tariff = self.get_tariff(recommended)
        
        return {
            'success': True,
            'recommended_tariff': recommended,
            'tariff_name': tariff['name'],
            'monthly_price': tariff['price'],
            'expected_roi': self._calculate_roi(monthly_volume, tariff['price'], tariff['commission_rate']),
            'reasoning': self._get_recommendation_reasoning(monthly_volume, project_count, company_size)
        }
    
    def validate_upgrade(self, current_tariff: str, new_tariff: str) -> Dict[str, Any]:
        """Валидация перехода на новый тариф"""
        current = self.get_tariff(current_tariff)
        new = self.get_tariff(new_tariff)
        
        if not current or not new:
            return {'success': False, 'error': 'Тариф не найден'}
        
        # Проверка что это upgrade, а не downgrade
        tariff_order = [TariffTier.FREE.value, TariffTier.START.value, 
                       TariffTier.BASIC.value, TariffTier.PREMIUM.value, 
                       TariffTier.BUSINESS.value]
        
        current_index = tariff_order.index(current_tariff)
        new_index = tariff_order.index(new_tariff)
        
        is_upgrade = new_index > current_index
        
        return {
            'success': True,
            'is_upgrade': is_upgrade,
            'price_difference': new['price'] - current['price'],
            'features_gained': list(set(new['features']) - set(current['features'])),
            'features_lost': list(set(current['features']) - set(new['features'])),
            'prorated_amount': self._calculate_prorated_amount(current['price'], new['price'])
        }
    
    def calculate_yearly_savings(self, tariff_name: str) -> Dict[str, Any]:
        """Расчет годовой экономии при годовой оплате"""
        monthly_price = self.plans[tariff_name]['price']
        yearly_price = monthly_price * 10  # 2 месяца бесплатно
        
        return {
            'success': True,
            'tariff': tariff_name,
            'monthly_total': monthly_price * 12,
            'yearly_total': yearly_price,
            'savings': monthly_price * 12 - yearly_price,
            'savings_percentage': round(((monthly_price * 12 - yearly_price) / (monthly_price * 12)) * 100, 2),
            'effective_monthly': round(yearly_price / 12, 2)
        }
    
    def _get_period_text(self, period: str) -> str:
        """Получение текстового описания периода"""
        period_texts = {
            'monthly': 'в месяц',
            'quarterly': 'в квартал',
            'yearly': 'в год'
        }
        return period_texts.get(period, 'в месяц')
    
    def _calculate_roi(self, monthly_volume: float, tariff_price: float, commission_rate: float) -> float:
        """Расчет ROI (Return on Investment)"""
        if monthly_volume == 0 or tariff_price == 0:
            return 0
        
        # Предполагаем, что система приносит 30% дополнительного объема
        additional_volume = monthly_volume * 0.3
        commission_savings = additional_volume * commission_rate
        
        roi = (commission_savings - tariff_price) / tariff_price * 100
        return round(roi, 2)
    
    def _get_recommendation_reasoning(self, monthly_volume: float, project_count: int, company_size: str) -> str:
        """Формирование обоснования рекомендации"""
        reasoning = []
        
        if monthly_volume > 1000000:
            reasoning.append("Высокий месячный оборот требует расширенных возможностей")
        
        if project_count > 5:
            reasoning.append("Множество одновременных проектов требует улучшенного управления")
        
        if company_size == 'medium' or company_size == 'large':
            reasoning.append("Размер компании требует профессиональных инструментов")
        
        if not reasoning:
            reasoning.append("Базовый тариф подходит для начала работы")
        
        return ". ".join(reasoning)
    
    def _calculate_prorated_amount(self, current_price: float, new_price: float) -> float:
        """Расчет пропорциональной суммы при смене тарифа"""
        # Предполагаем, что смена тарифа происходит в середине месяца
        days_in_month = 30
        days_used = 15
        
        remaining_days = days_in_month - days_used
        daily_current = current_price / days_in_month
        daily_new = new_price / days_in_month
        
        refund = daily_current * remaining_days
        charge = daily_new * remaining_days
        
        return charge - refund
    
    def _get_recommendation(self, t1: Dict, t2: Dict) -> str:
        """Получение рекомендации при сравнении тарифов"""
        if t2['price'] - t1['price'] <= 0:
            return f"{t2['name']} выгоднее по цене"
        
        price_per_lead_t1 = t1['price'] / t1['leads_per_month'] if t1['leads_per_month'] > 0 else 0
        price_per_lead_t2 = t2['price'] / t2['leads_per_month'] if t2['leads_per_month'] > 0 else 0
        
        if price_per_lead_t2 < price_per_lead_t1:
            return f"{t2['name']} предлагает более низкую стоимость за лид"
        else:
            return f"{t1['name']} более экономичен для вашего объема"
    
    def get_feature_matrix(self) -> Dict[str, Any]:
        """Получение матрицы возможностей всех тарифов"""
        features = set()
        for tariff in self.plans.values():
            features.update(tariff['features'])
        
        matrix = {}
        for feature in sorted(features):
            matrix[feature] = {}
            for tariff_code, tariff in self.plans.items():
                matrix[feature][tariff_code] = feature in tariff['features']
        
        return {
            'success': True,
            'features': list(features),
            'matrix': matrix,
            'tariffs': list(self.plans.keys())
        }
