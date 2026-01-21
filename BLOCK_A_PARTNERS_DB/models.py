"""
МОДЕЛИ ДАННЫХ ДЛЯ БАЗЫ ПАРТНЕРОВ
Согласно ТЗ: МОДЕЛЬ ПАРТНЕРА
"""

from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.dialects.postgresql import JSONB

db = SQLAlchemy()

class Partner(db.Model):
    """Модель партнера (строительной компании)"""
    __tablename__ = 'partners'
    
    # Основной идентификатор
    id = db.Column(db.Integer, primary_key=True)
    partner_code = db.Column(db.String(50), unique=True, nullable=False)  # P-20231215-0001
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # ==================== ЮРИДИЧЕСКИЕ ДАННЫЕ ====================
    company_name = db.Column(db.String(200), nullable=False)
    legal_form = db.Column(db.String(20), nullable=False)  # ООО, ИП, АО
    inn = db.Column(db.String(12), unique=True, nullable=False)  # 10-12 цифр
    ogrn = db.Column(db.String(15))
    kpp = db.Column(db.String(9))
    legal_address = db.Column(db.Text)
    actual_address = db.Column(db.Text)
    registration_date = db.Column(db.Date)  # Дата регистрации в ЕГРЮЛ
    
    # ==================== КОНТАКТНЫЕ ДАННЫЕ ====================
    contact_person = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    website = db.Column(db.String(200))
    telegram = db.Column(db.String(50))
    whatsapp = db.Column(db.String(20))
    
    # ==================== ПРОФИЛЬ УСЛУГ ====================
    main_category = db.Column(db.String(50), nullable=False)  # подрядчик, производитель, продавец, исполнитель
    specializations = db.Column(JSONB, default=list)  # ["каркасные дома", "отделка", "кровля"]
    
    # Услуги в формате JSON
    services = db.Column(JSONB, default=list)  # [{service_name: "Строительство дома", price_range: {min: 1000000, max: 3000000, currency: "RUB"}}]
    
    # ==================== ГЕОГРАФИЯ ====================
    regions = db.Column(JSONB, default=list)  # ["Московская область", "Ленинградская область"]
    cities = db.Column(JSONB, default=list)   # ["Москва", "Санкт-Петербург"]
    radius_km = db.Column(db.Integer, default=50)  # Радиус работы в км
    
    # ==================== ВЕРИФИКАЦИЯ ====================
    verification_status = db.Column(db.String(20), default='pending', nullable=False)  # pending, verified, rejected
    verification_date = db.Column(db.DateTime)
    verified_by = db.Column(db.String(50))  # system/admin ID
    documents = db.Column(JSONB, default=list)  # [{type: "ОГРН", url: "...", verified: true}]
    rejection_reason = db.Column(db.Text)
    
    # ==================== СТАТУС И НАСТРОЙКИ ====================
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    subscription_type = db.Column(db.String(20), default='free', nullable=False)  # free, basic, premium
    subscription_expires = db.Column(db.DateTime)
    max_active_leads = db.Column(db.Integer, default=3)
    
    # Рейтинг и статистика
    rating = db.Column(db.Float, default=0.0)  # 0-5
    completed_projects = db.Column(db.Integer, default=0)
    response_rate = db.Column(db.Float, default=0.0)  # процент ответов на заявки
    
    # Технические поля
    settings = db.Column(JSONB, default=dict)  # notification_settings и другие настройки
    
    def to_dict(self):
        """Преобразование в словарь для API"""
        return {
            'partner_code': self.partner_code,
            'company_name': self.company_name,
            'legal_form': self.legal_form,
            'inn': self.inn,
            'verification_status': self.verification_status,
            'is_active': self.is_active,
            'contact_person': self.contact_person,
            'phone': self.phone,
            'email': self.email,
            'main_category': self.main_category,
            'specializations': self.specializations,
            'regions': self.regions,
            'rating': self.rating,
            'subscription_type': self.subscription_type,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class PartnerVerificationLog(db.Model):
    """Лог верификации партнеров"""
    __tablename__ = 'partner_verification_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    partner_id = db.Column(db.Integer, db.ForeignKey('partners.id'), nullable=False)
    partner_code = db.Column(db.String(50), nullable=False)
    
    # Детали действия
    action = db.Column(db.String(50), nullable=False)  # inn_check, document_upload, manual_review
    status = db.Column(db.String(20), nullable=False)  # success, failed, pending
    details = db.Column(JSONB)  # {request: {...}, response: {...}, error: "..."}
    
    # Кто выполнил
    performed_by = db.Column(db.String(50))  # system, admin_id, user_id
    performed_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    # Связь
    partner = db.relationship('Partner', backref=db.backref('verification_logs', lazy=True))
