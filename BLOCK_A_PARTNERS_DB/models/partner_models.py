"""
Модели данных для партнеров
Блок A: База партнеров + Верификация
"""

from enum import Enum
from datetime import datetime
from typing import Optional, List, Dict, Any
from dataclasses import dataclass, field
from decimal import Decimal


class LegalForm(Enum):
    """Организационно-правовая форма"""
    OOO = "ООО"          # Общество с ограниченной ответственностью
    IP = "ИП"            # Индивидуальный предприниматель
    AO = "АО"            # Акционерное общество
    ZAO = "ЗАО"          # Закрытое акционерное общество
    INVALID = "Не определено"


class VerificationStatus(Enum):
    """Статусы верификации партнера"""
    PENDING = "pending"           # Ожидает верификации
    IN_PROGRESS = "in_progress"   # В процессе проверки
    VERIFIED = "verified"         # Верифицирован
    REJECTED = "rejected"         # Отклонен
    SUSPENDED = "suspended"       # Приостановлен


class PartnerTier(Enum):
    """Тарифный план партнера"""
    BASIC = "basic"               # Бесплатный тариф (3 активных заявки)
    PRO = "pro"                   # Платный тариф (10 активных заявок)
    ENTERPRISE = "enterprise"     # Корпоративный (безлимит)


@dataclass
class PartnerContact:
    """Контактные данные партнера"""
    phone: str                    # Основной телефон
    email: str                    # Email
    contact_person: str           # Контактное лицо
    position: str                 # Должность
    telegram: Optional[str] = None
    whatsapp: Optional[str] = None
    website: Optional[str] = None
    additional_phones: List[str] = field(default_factory=list)


@dataclass
class PartnerService:
    """Услуга партнера с ценами"""
    id: str                      # Уникальный ID услуги
    name: str                    # Название услуги (например, "Ремонт ванной комнаты")
    description: str             # Подробное описание
    unit: str                    # Единица измерения: м², м³, шт., услуга, час
    price_min: Decimal           # Минимальная цена
    price_max: Decimal           # Максимальная цена
    currency: str = "RUB"        # Валюта (RUB, USD, EUR)
    category: Optional[str] = None  # Категория (ремонт, строительство, отделка)
    tags: List[str] = field(default_factory=list)  # Теги (элитный, бюджетный, срочный)
    is_active: bool = True       # Активна ли услуга
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class PartnerDocument:
    """Документ партнера"""
    id: str                      # Уникальный ID документа
    type: str                    # Тип: inn_certificate, ogrn_certificate, passport, license, insurance, extract
    name: str                    # Оригинальное имя файла
    s3_path: str                 # Путь в S3 хранилище
    mime_type: str               # MIME-тип (application/pdf, image/jpeg)
    size_bytes: int              # Размер в байтах
    uploaded_at: datetime        # Дата загрузки
    verified: bool = False       # Проверен ли документ
    verification_notes: Optional[str] = None  # Комментарии при верификации
    verified_by: Optional[str] = None         # Кто проверил (system или admin_id)
    verified_at: Optional[datetime] = None    # Когда проверили


@dataclass
class Partner:
    """Основная модель партнера"""
    # === Идентификаторы ===
    id: str                      # Внутренний UUID
    public_id: str               # Публичный ID для клиентов (например, PART-001)
    
    # === Юридическая информация ===
    legal_name: str              # Юридическое название (полное)
    trading_name: Optional[str] = None  # Торговое название (если отличается)
    legal_form: LegalForm = LegalForm.INVALID
    inn: str = ""                # ИНН (10 цифр для юр.лиц, 12 для ИП)
    ogrn: Optional[str] = None   # ОГРН/ОГРНИП
    kpp: Optional[str] = None    # КПП (только для юр.лиц)
    legal_address: str = ""      # Юридический адрес
    actual_address: Optional[str] = None  # Фактический адрес
    
    # === Контактная информация ===
    contact: Optional[PartnerContact] = None
    
    # === Профиль услуг ===
    main_category: str = ""      # Основная категория деятельности
    specializations: List[str] = field(default_factory=list)  # Специализации
    services: List[PartnerService] = field(default_factory=list)  # Услуги с ценами
    portfolio_items: List[Dict[str, Any]] = field(default_factory=list)  # Портфолио
    
    # === География работы ===
    regions: List[str] = field(default_factory=list)  # Коды регионов (например, ["77", "50"])
    cities: List[str] = field(default_factory=list)   # Названия городов
    work_radius_km: Optional[int] = None  # Радиус работы в км от указанных городов
    
    # === Верификация ===
    verification_status: VerificationStatus = VerificationStatus.PENDING
    verification_score: float = 0.0  # Баллы верификации от 0 до 100
    verification_date: Optional[datetime] = None
    verified_by: Optional[str] = None  # system или admin_id
    rejection_reason: Optional[str] = None
    
    # === Документы ===
    documents: List[PartnerDocument] = field(default_factory=list)
    
    # === Настройки и статус ===
    tier: PartnerTier = PartnerTier.BASIC
    is_active: bool = True       # Активен ли партнер в системе
    is_blocked: bool = False     # Заблокирован администратором
    max_active_leads: int = 3    # Максимум активных заявок (зависит от тарифа)
    subscription_expires: Optional[datetime] = None  # Окончание подписки
    
    # === Рейтинг и статистика ===
    rating: float = 0.0          # Средний рейтинг от 0 до 5
    reviews_count: int = 0       # Количество отзывов
    completed_projects: int = 0  # Завершенных проектов
    response_time_avg: Optional[float] = None  # Среднее время ответа в часах
    
    # === Технические поля ===
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    created_by: Optional[str] = None  # Кто создал (bot, admin, api)
    metadata: Dict[str, Any] = field(default_factory=dict)  # Дополнительные данные
    
    def to_dict(self) -> Dict[str, Any]:
        """Преобразование в словарь для API"""
        return {
            "id": self.id,
            "public_id": self.public_id,
            "legal_name": self.legal_name,
            "trading_name": self.trading_name,
            "legal_form": self.legal_form.value,
            "verification_status": self.verification_status.value,
            "verification_score": self.verification_score,
            "rating": self.rating,
            "reviews_count": self.reviews_count,
            "is_active": self.is_active,
            "tier": self.tier.value,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }


@dataclass
class VerificationLog:
    """Лог верификации партнера"""
    id: str
    partner_id: str
    action: str                  # inn_check, document_upload, admin_review, status_change
    status: str                  # success, failed, pending
    details: Dict[str, Any]      # Детали действия
    performed_by: str            # system, admin_id, partner_id
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class SearchFilters:
    """Фильтры для поиска партнеров"""
    region: Optional[str] = None
    city: Optional[str] = None
    specialization: Optional[str] = None
    service_name: Optional[str] = None
    min_rating: float = 0.0
    max_price: Optional[Decimal] = None
    min_completed_projects: int = 0
    verification_required: bool = True  # Только верифицированные
    tier: Optional[PartnerTier] = None
    page: int = 1
    page_size: int = 20
    sort_by: str = "rating"      # rating, price, reviews, response_time
    sort_order: str = "desc"     # asc, desc


@dataclass
class PartnerStats:
    """Статистика партнера"""
    partner_id: str
    total_leads: int = 0
    accepted_leads: int = 0
    rejected_leads: int = 0
    completed_leads: int = 0
    avg_response_time_hours: Optional[float] = None
    customer_satisfaction: float = 0.0  # 0-100%
    last_activity: Optional[datetime] = None
    calculated_at: datetime = field(default_factory=datetime.utcnow)
