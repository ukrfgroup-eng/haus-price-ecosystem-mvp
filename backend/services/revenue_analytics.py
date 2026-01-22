"""
Минимальная версия для тестов
"""

class RevenueAnalytics:
    def get_monthly_revenue(self, year=None, month=None):
        return {
            'total_revenue': 0,
            'payment_count': 0,
            'average_payment': 0
        }
    
    def get_partner_lifetime_value(self, partner_id):
        return {
            'total_spent': 0,
            'payment_count': 0
        }
