"""
Модели данных SQLAlchemy для партнеров
"""

from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime, JSON, Text, ForeignKey, Enum, Numeric
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from datetime import datetime
import enum

from .base import Base

class LegalForm(enum.Enum):
    OOO = "ООО"
    IP = "ИП"
    AO = "АО"
    ZAO = "ЗАО"
    INVALID = "Не определено"

class VerificationStatus(enum.Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    VERIFIED = "verified"
    REJECTED = "rejected"
    SUSPENDED = "suspended"

class PartnerTier(enum.Enum):
    BASIC = "basic"
    PRO = "pro"
    ENTERPRISE = "enterprise"

class Partner(Base):
    __tablename__ = "partners"

    # Идентификаторы
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    public_id = Column(String(50), unique=True, nullable=False)
    
    # Юридическая информация
    company_name = Column(String(200), nullable=False)
    trading_name = Column(String(200))
    legal_form = Column(Enum(LegalForm), nullable=False, default=LegalForm.INVALID)
    inn = Column(String(12), unique=True, nullable=False)
    ogrn = Column(String(15))
    kpp = Column(String(9))
    legal_address = Column(Text, nullable=False, default="")
    actual_address = Column(Text)
    
    # Контактная информация
    phone = Column(String(20))
    email = Column(String(120))
    website = Column(String(200))
    contact_person = Column(String(100))
    contact_position = Column(String(100))
    telegram = Column(String(100))
    whatsapp = Column(String(20))
    
    # Профиль услуг
    main_category = Column(String(100))
    specializations = Column(JSON, default=[])
    services = Column(JSON, default=[])
    portfolio = Column(JSON, default=[])
    
    # География работы
    regions = Column(JSON, default=[])
    cities = Column(JSON, default=[])
    work_radius_km = Column(Integer)
    
    # Верификация
    verification_status = Column(Enum(VerificationStatus), default=VerificationStatus.PENDING)
    verification_score = Column(Float, default=0.0)
    verification_date = Column(DateTime)
    verified_by = Column(String(50))
    rejection_reason = Column(Text)
    
    # Документы
    documents = Column(JSON, default=[])
    
    # Настройки и статус
    tier = Column(Enum(PartnerTier), default=PartnerTier.BASIC)
    is_active = Column(Boolean, default=True)
    is_blocked = Column(Boolean, default=False)
    max_active_leads = Column(Integer, default=3)
    subscription_expires = Column(DateTime)
    
    # Рейтинг и статистика
    rating = Column(Float, default=0.0)
    reviews_count = Column(Integer, default=0)
    completed_projects = Column(Integer, default=0)
    response_time_avg = Column(Float)
    
    # Технические поля
    created_by = Column(String(50))
    metadata = Column(JSON, default={})
    
    # Временные метки
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            "id": str(self.id),
            "public_id": self.public_id,
            "company_name": self.company_name,
            "legal_form": self.legal_form.value,
            "verification_status": self.verification_status.value,
            "is_active": self.is_active,
            "rating": self.rating,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }

class VerificationLog(Base):
    __tablename__ = "verification_logs"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    partner_id = Column(UUID(as_uuid=True), ForeignKey('partners.id'))
    action = Column(String(50))
    status = Column(String(20))
    details = Column(JSON, default={})
    performed_by = Column(String(50))
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Связь с партнером
    partner = relationship("Partner")

# Инициализируем все модели
__all__ = ['Partner', 'VerificationLog', 'LegalForm', 'VerificationStatus', 'PartnerTier']
