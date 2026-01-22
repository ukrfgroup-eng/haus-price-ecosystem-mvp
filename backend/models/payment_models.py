"""
Модели для системы платежей
"""

from datetime import datetime
from backend import db


class Payment(db.Model):
    __tablename__ = 'payments'
    
    id = db.Column(db.Integer, primary_key=True)
    payment_number = db.Column(db.String(50), unique=True, nullable=False)
    partner_id = db.Column(db.String(50), db.ForeignKey('partners.partner_id'), nullable=False)
    
    amount = db.Column(db.Float, nullable=False)
    currency = db.Column(db.String(3), default='RUB')
    status = db.Column(db.String(20), default='pending')  # pending, processing, completed, failed, refunded
    payment_type = db.Column(db.String(30))  # subscription, lead_purchase, service
    
    tariff_plan = db.Column(db.String(30))
    description = db.Column(db.Text)
    
    # Данные для счета
    invoice_data = db.Column(db.JSON)
    invoice_file = db.Column(db.String(255))
    
    # Данные платежной системы
    payment_system = db.Column(db.String(30))  # yookassa, tinkoff, sberbank
    payment_system_id = db.Column(db.String(100))
    payment_url = db.Column(db.String(500))
    
    # Временные метки
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    paid_at = db.Column(db.DateTime)
    
    def to_dict(self):
        return {
            'id': self.id,
            'payment_number': self.payment_number,
            'partner_id': self.partner_id,
            'amount': self.amount,
            'currency': self.currency,
            'status': self.status,
            'payment_type': self.payment_type,
            'tariff_plan': self.tariff_plan,
            'description': self.description,
            'payment_url': self.payment_url,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'paid_at': self.paid_at.isoformat() if self.paid_at else None
        }


class Subscription(db.Model):
    __tablename__ = 'subscriptions'
    
    id = db.Column(db.Integer, primary_key=True)
    partner_id = db.Column(db.String(50), db.ForeignKey('partners.partner_id'), nullable=False)
    
    tariff_plan = db.Column(db.String(30), nullable=False)
    status = db.Column(db.String(20), default='active')  # active, expired, cancelled, suspended
    
    price = db.Column(db.Float, nullable=False)
    period = db.Column(db.String(20))  # monthly, quarterly, yearly
    leads_included = db.Column(db.Integer, default=0)
    
    starts_at = db.Column(db.DateTime, nullable=False)
    expires_at = db.Column(db.DateTime, nullable=False)
    auto_renewal = db.Column(db.Boolean, default=True)
    
    # Ссылка на последний платеж
    last_payment_id = db.Column(db.Integer, db.ForeignKey('payments.id'))
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'partner_id': self.partner_id,
            'tariff_plan': self.tariff_plan,
            'status': self.status,
            'price': self.price,
            'period': self.period,
            'leads_included': self.leads_included,
            'starts_at': self.starts_at.isoformat() if self.starts_at else None,
            'expires_at': self.expires_at.isoformat() if self.expires_at else None,
            'auto_renewal': self.auto_renewal,
            'days_remaining': (self.expires_at - datetime.utcnow()).days if self.expires_at else 0
        }
