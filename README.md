🏗️ ТЕХНИЧЕСКОЕ ЗАДАНИЕ: MVP "ДОМА-ЦЕНЫ.РФ"
📁 КОМПЛЕКТ ФАЙЛОВ ДЛЯ НЕМЕДЛЕННОГО СОЗДАНИЯ
1. КОРНЕВЫЕ ФАЙЛЫ (8 файлов)
📄 README.md (главное описание):

markdown
# 🏗️ ДОМА-ЦЕНЫ.РФ - MVP Экосистема

🚀 **Первая в России AI-экосистема загородного строительства**
> Автоматический подбор исполнителей | Верифицированные партнеры | AI-анализ запросов

## 🎯 ЦЕЛЬ MVP
Создать работающий прототип за 4 недели с 4 независимыми блоками:

1. **Блок A** - База верифицированных партнеров (недели 1-2)
2. **Блок B** - Бот-проводник с AI-анализом (недели 2-3)
3. **Блок C** - Внешние интеграции (недели 3-4)
4. **Блок D** - Система монетизации (неделя 4)

## 🏗️ СТРУКТУРА ПРОЕКТА
haus-price-ecosystem-mvp/
├── 📁 BLOCK_A_PARTNERS_DB/ # Блок A: База партнеров + верификация
├── 📁 BLOCK_B_BOT_AI/ # Блок B: Бот-проводник + AI-анализ
├── 📁 BLOCK_C_INTEGRATIONS/ # Блок C: Внешние интеграции
├── 📁 BLOCK_D_MONETIZATION/ # Блок D: Система монетизации
├── 📁 infrastructure/ # Инфраструктура (Docker, Nginx)
├── 📁 tests/ # Тесты для каждого блока
├── 📁 docs/ # Документация
├── 📁 .github/workflows/ # GitHub Actions для автоматического тестирования
├── 📄 docker-compose.yml # Docker Compose для запуска всей системы
├── 📄 requirements.txt # Зависимости Python
└── 📄 .env.example # Шаблон переменных окружения

text

## 🚀 БЫСТРЫЙ СТАРТ

### Для разработчиков:
```bash
# Клонирование репозитория
git clone https://github.com/ваш-аккаунт/haus-price-ecosystem-mvp.git

# Установка зависимостей
pip install -r requirements.txt

# Запуск в Docker (рекомендуется)
docker-compose up -d

# Или запуск локально
cd BLOCK_A_PARTNERS_DB
python main.py
Для пользователей:
Открыть сайт: https://дома-цены.рф

Начать чат с ботом-проводником

Получить подборку исполнителей за 5 минут

📞 КОНТАКТЫ
Технические вопросы: haus-price@yandex.ru
Партнерства: haus-price@yandex.ru
Экстренная поддержка: через бота на сайте

📄 ЛИЦЕНЗИЯ
MIT License - смотрите файл LICENSE

text

**📄 requirements.txt** (основные зависимости):
```txt
# Основной стек
Flask==2.3.3
Flask-SQLAlchemy==3.0.5
Flask-CORS==4.0.0
Flask-Migrate==4.0.4

# База данных
psycopg2-binary==2.9.7
SQLAlchemy==2.0.19

# AI и обработка данных
nltk==3.8.1
scikit-learn==1.3.0
pandas==2.1.1
numpy==1.24.3

# HTTP клиенты
requests==2.31.0
aiohttp==3.8.5

# Валидация
pydantic==2.3.0
marshmallow==3.20.1

# Утилиты
python-dotenv==1.0.0
python-dateutil==2.8.2
pytz==2023.3

# Тестирование
pytest==7.4.2
pytest-cov==4.1.0
factory-boy==3.3.0

# Документация
sphinx==7.2.6
📄 .env.example (шаблон переменных окружения):

env
# ==================== ОСНОВНЫЕ НАСТРОЙКИ ====================
APP_ENV=development
DEBUG=True
SECRET_KEY=change-this-in-production
APP_NAME=haus-price-mvp

# ==================== БАЗА ДАННЫХ ====================
DATABASE_URL=postgresql://user:password@localhost:5432/haus_price_db
DATABASE_TEST_URL=postgresql://user:password@localhost:5433/haus_price_test

# ==================== API КЛЮЧИ ====================
# API ФНС для верификации ИНН
FNS_API_KEY=your_fns_api_key_here
FNS_API_URL=https://api-fns.ru/api/egr

# API для проверки юрлиц
DADATA_API_KEY=your_dadata_api_key_here
DADATA_SECRET=your_dadata_secret_here

# ==================== БОТЫ И ИНТЕГРАЦИИ ====================
# Protalk боты
PROTALK_CLIENT_BOT_TOKEN=your_protalk_client_bot_token
PROTALK_PARTNER_BOT_TOKEN=your_protalk_partner_bot_token
PROTALK_WEBHOOK_SECRET=your_webhook_secret

# Umnico (чат на сайте)
UMNICO_WIDGET_TOKEN=your_umnico_widget_token
UMNICO_API_KEY=your_umnico_api_key

# Telegram (альтернатива)
TELEGRAM_BOT_TOKEN=your_telegram_bot_token

# ==================== ПЛАТЕЖНЫЕ СИСТЕМЫ ====================
# ЮKassa (Яндекс.Касса)
YUKASSA_SHOP_ID=your_shop_id
YUKASSA_SECRET_KEY=your_secret_key

# CloudPayments
CLOUDPAYMENTS_PUBLIC_ID=your_public_id
CLOUDPAYMENTS_API_SECRET=your_api_secret

# ==================== EMAIL И УВЕДОМЛЕНИЯ ====================
SMTP_HOST=smtp.yandex.ru
SMTP_PORT=587
SMTP_USER=your_email@yandex.ru
SMTP_PASSWORD=your_email_password
EMAIL_FROM=noreply@дома-цены.рф

# ==================== URL СЕРВИСОВ ====================
FRONTEND_URL=https://дома-цены.рф
PARTNER_PORTAL_URL=https://партнер.дома-цены.рф
API_BASE_URL=http://localhost:5000/api/v1

# ==================== ЛИМИТЫ И ТАРИФЫ ====================
FREE_TIER_LEADS_LIMIT=3
BASIC_TIER_LEADS_LIMIT=15
PREMIUM_TIER_LEADS_LIMIT=50

# ==================== НАСТРОЙКИ AI ====================
AI_CONFIDENCE_THRESHOLD=0.7
MAX_PARTNERS_PER_REQUEST=5
DEFAULT_RESPONSE_TIME_HOURS=24
📄 docker-compose.yml (Docker для всей системы):

yaml
version: '3.8'

services:
  # PostgreSQL база данных
  postgres:
    image: postgres:15-alpine
    container_name: haus_price_db
    environment:
      POSTGRES_DB: haus_price_db
      POSTGRES_USER: haus_user
      POSTGRES_PASSWORD: haus_password
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./infrastructure/postgresql/init.sql:/docker-entrypoint-initdb.d/init.sql
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U haus_user"]
      interval: 10s
      timeout: 5s
      retries: 5

  # Тестовая база данных
  postgres_test:
    image: postgres:15-alpine
    container_name: haus_price_test_db
    environment:
      POSTGRES_DB: haus_price_test
      POSTGRES_USER: test_user
      POSTGRES_PASSWORD: test_password
    ports:
      - "5433:5432"
    volumes:
      - postgres_test_data:/var/lib/postgresql/data

  # MATRIX CORE API (Блоки A, C, D)
  api:
    build:
      context: .
      dockerfile: ./infrastructure/docker/Dockerfile.api
    container_name: haus_price_api
    ports:
      - "5000:5000"
    environment:
      - DATABASE_URL=postgresql://haus_user:haus_password@postgres:5432/haus_price_db
      - APP_ENV=production
    depends_on:
      postgres:
        condition: service_healthy
    volumes:
      - ./logs:/app/logs
    restart: unless-stopped

  # Nginx для прокси
  nginx:
    image: nginx:alpine
    container_name: haus_price_nginx
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./infrastructure/nginx/nginx.conf:/etc/nginx/nginx.conf
      - ./infrastructure/nginx/ssl:/etc/nginx/ssl
    depends_on:
      - api
    restart: unless-stopped

  # Redis для кэширования
  redis:
    image: redis:7-alpine
    container_name: haus_price_redis
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    command: redis-server --appendonly yes

volumes:
  postgres_data:
  postgres_test_data:
  redis_data:
📄 .gitignore:

gitignore
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Virtual Environment
venv/
env/
ENV/
.env
.env.local
.env.*.local

# Database
*.db
*.sqlite
*.sqlite3

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
.DS_Store?
._*
.Spotlight-V100
.Trashes
ehthumbs.db
Thumbs.db

# Logs
*.log
logs/

# Testing
.coverage
.pytest_cache/
.mypy_cache/

# Docker
docker-compose.override.yml

# Secrets
secrets/
*.pem
*.key

# Temporary files
tmp/
temp/
📄 LICENSE (MIT лицензия):

text
MIT License

Copyright (c) 2024 Дома-Цены.РФ

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
2. ПАПКА BLOCK_A_PARTNERS_DB (8 файлов + README)
📁 BLOCK_A_PARTNERS_DB/init.py:

python
"""
БЛОК A: БАЗА ПАРТНЕРОВ + ВЕРИФИКАЦИЯ
Ядро системы - база верифицированных партнеров с услугами и ценами
"""

__version__ = "1.0.0"
__description__ = "База данных партнеров с верификацией через ФНС API"

from .models import db, Partner, PartnerVerificationLog
from .verification_service import VerificationService
from .partner_manager import PartnerManager

__all__ = [
    'db',
    'Partner', 
    'PartnerVerificationLog',
    'VerificationService',
    'PartnerManager'
]
📁 BLOCK_A_PARTNERS_DB/models.py:

python
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
📁 BLOCK_A_PARTNERS_DB/api_routes.py:

python
"""
API ДЛЯ РАБОТЫ С ПАРТНЕРАМИ
Согласно ТЗ: API ДЛЯ РАБОТЫ С ПАРТНЕРАМИ
"""

from flask import Blueprint, request, jsonify, current_app
from sqlalchemy.exc import IntegrityError
from .models import db, Partner, PartnerVerificationLog
from .verification_service import VerificationService

partner_bp = Blueprint('partners', __name__, url_prefix='/api/v1/partners')
verification_service = VerificationService()

@partner_bp.route('/register', methods=['POST'])
def register_partner():
    """Регистрация нового партнера"""
    try:
        data = request.get_json()
        
        # Валидация обязательных полей
        required_fields = ['company_name', 'legal_form', 'inn', 'contact_person', 'phone', 'email']
        for field in required_fields:
            if not data.get(field):
                return jsonify({
                    'success': False,
                    'error': f'Не заполнено обязательное поле: {field}'
                }), 400
        
        # Проверка ИНН через API ФНС
        inn_verification = verification_service.verify_inn(data['inn'])
        if not inn_verification['success']:
            return jsonify({
                'success': False,
                'error': 'Ошибка верификации ИНН',
                'details': inn_verification.get('error')
            }), 400
        
        # Генерация кода партнера
        from datetime import datetime
        import random
        date_str = datetime.now().strftime('%y%m%d')
        random_str = ''.join(random.choices('0123456789', k=4))
        partner_code = f"P-{date_str}-{random_str}"
        
        # Создание партнера
        partner = Partner(
            partner_code=partner_code,
            company_name=data['company_name'],
            legal_form=data['legal_form'],
            inn=data['inn'],
            contact_person=data['contact_person'],
            phone=data['phone'],
            email=data['email'],
            verification_data=inn_verification.get('data'),
            verification_status='pending_documents' if inn_verification['success'] else 'rejected',
            status='registration_in_progress',
            registration_stage='inn_verified'
        )
        
        # Опциональные поля
        if data.get('ogrn'):
            partner.ogrn = data['ogrn']
        if data.get('legal_address'):
            partner.legal_address = data['legal_address']
        if data.get('website'):
            partner.website = data['website']
        
        db.session.add(partner)
        
        # Логирование верификации
        log = PartnerVerificationLog(
            partner_id=partner.id,
            partner_code=partner_code,
            action='inn_check',
            status='success' if inn_verification['success'] else 'failed',
            details=inn_verification,
            performed_by='system'
        )
        db.session.add(log)
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'partner': partner.to_dict(),
            'message': 'Регистрация начата успешно',
            'next_steps': [
                {
                    'step': 'upload_documents',
                    'description': 'Загрузите документы компании',
                    'url': f"/partner/upload/{partner_code}"
                },
                {
                    'step': 'complete_profile',
                    'description': 'Заполните профиль услуг и специализаций',
                    'url': f"/partner/profile/{partner_code}"
                }
            ]
        }), 201
        
    except IntegrityError:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': 'Компания с таким ИНН уже зарегистрирована'
        }), 409
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Ошибка регистрации партнера: {e}")
        return jsonify({
            'success': False,
            'error': 'Внутренняя ошибка сервера'
        }), 500

@partner_bp.route('/search', methods=['POST'])
def search_partners():
    """Поиск партнеров по критериям"""
    try:
        criteria = request.get_json()
        
        # Базовый запрос только верифицированных и активных партнеров
        query = Partner.query.filter(
            Partner.verification_status == 'verified',
            Partner.is_active == True
        )
        
        # Фильтр по региону
        if criteria.get('region'):
            query = query.filter(Partner.regions.contains([criteria['region']]))
        
        # Фильтр по специализациям
        if criteria.get('specializations'):
            query = query.filter(
                Partner.specializations.overlap(criteria['specializations'])
            )
        
        # Фильтр по категории
        if criteria.get('main_category'):
            query = query.filter(Partner.main_category == criteria['main_category'])
        
        # Сортировка по рейтингу
        query = query.order_by(Partner.rating.desc(), Partner.created_at.desc())
        
        # Пагинация
        page = criteria.get('page', 1)
        per_page = min(criteria.get('per_page', 10), 50)
        partners = query.paginate(page=page, per_page=per_page, error_out=False)
        
        return jsonify({
            'success': True,
            'partners': [p.to_dict() for p in partners.items],
            'pagination': {
                'page': partners.page,
                'per_page': partners.per_page,
                'total': partners.total,
                'pages': partners.pages
            }
        })
        
    except Exception as e:
        current_app.logger.error(f"Ошибка поиска партнеров: {e}")
        return jsonify({
            'success': False,
            'error': 'Ошибка при поиске партнеров'
        }), 500

@partner_bp.route('/<partner_code>', methods=['GET'])
def get_partner(partner_code):
    """Получение информации о партнере"""
    partner = Partner.query.filter_by(partner_code=partner_code).first()
    
    if not partner:
        return jsonify({'success': False, 'error': 'Партнер не найден'}), 404
    
    return jsonify({'success': True, 'partner': partner.to_dict()})

@partner_bp.route('/<partner_code>/profile', methods=['PUT'])
def update_partner_profile(partner_code):
    """Обновление профиля партнера"""
    try:
        partner = Partner.query.filter_by(partner_code=partner_code).first()
        if not partner:
            return jsonify({'success': False, 'error': 'Партнер не найден'}), 404
        
        data = request.get_json()
        
        # Обновление полей профиля
        update_fields = ['main_category', 'specializations', 'services', 'regions', 'cities']
        for field in update_fields:
            if field in data:
                setattr(partner, field, data[field])
        
        partner.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Профиль успешно обновлен',
            'partner': partner.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Ошибка обновления профиля: {e}")
        return jsonify({'success': False, 'error': 'Ошибка обновления'}), 500
📁 BLOCK_A_PARTNERS_DB/verification_service.py:

python
"""
СЕРВИС ВЕРИФИКАЦИИ ПАРТНЕРОВ
Проверка ИНН через API ФНС и другие реестры
"""

import requests
import logging
from datetime import datetime
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class VerificationService:
    """Сервис верификации юридических данных"""
    
    def __init__(self):
        self.fns_api_url = "https://api-fns.ru/api/egr"
        self.dadata_api_url = "https://suggestions.dadata.ru/suggestions/api/4_1/rs/findById/party"
        
    def verify_inn(self, inn: str) -> Dict[str, Any]:
        """Проверка ИНН через API ФНС"""
        try:
            # Базовая валидация формата
            if not self._validate_inn_format(inn):
                return {'success': False, 'error': 'Неверный формат ИНН'}
            
            # Запрос к API ФНС
            response = self._call_fns_api(inn)
            
            if response.get('status') == 'success':
                data = response.get('data', {})
                
                return {
                    'success': True,
                    'data': {
                        'inn': inn,
                        'company_name': data.get('name'),
                        'ogrn': data.get('ogrn'),
                        'legal_address': data.get('address'),
                        'registration_date': data.get('reg_date'),
                        'status': data.get('status'),  # ACTIVE, LIQUIDATED, etc.
                        'legal_form': data.get('legal_form'),
                        'verified_at': datetime.utcnow().isoformat()
                    },
                    'message': 'ИНН успешно верифицирован'
                }
            else:
                return {
                    'success': False,
                    'error': 'Компания не найдена в реестре ФНС',
                    'details': response
                }
                
        except Exception as e:
            logger.error(f"Ошибка верификации ИНН {inn}: {e}")
            return {
                'success': False,
                'error': f'Ошибка при верификации: {str(e)}'
            }
    
    def _validate_inn_format(self, inn: str) -> bool:
        """Валидация формата ИНН"""
        if not inn or not inn.isdigit():
            return False
        
        length = len(inn)
        if length not in [10, 12]:  # 10 для юрлиц, 12 для ИП
            return False
        
        return True
    
    def _call_fns_api(self, inn: str) -> Dict[str, Any]:
        """Вызов API ФНС"""
        # Здесь должен быть реальный вызов API
        # Пока возвращаем тестовые данные
        return {
            'status': 'success',
            'data': {
                'name': f'Компания ИНН {inn}',
                'ogrn': '1234567890123',
                'address': 'Москва, ул. Примерная, д. 1',
                'reg_date': '2020-01-15',
                'status': 'ACTIVE',
                'legal_form': 'ООО'
            }
        }
    
    def verify_documents(self, documents: list) -> Dict[str, Any]:
        """Верификация загруженных документов"""
        verified_docs = []
        
        for doc in documents:
            doc_type = doc.get('type')
            doc_url = doc.get('url')
            
            # Здесь должна быть логика проверки документов
            verified_docs.append({
                'type': doc_type,
                'url': doc_url,
                'verified': True,  # В реальности нужно проверять
                'verified_at': datetime.utcnow().isoformat()
            })
        
        return {
            'success': True,
            'documents': verified_docs,
            'message': f'Проверено {len(verified_docs)} документов'
        }
📁 BLOCK_A_PARTNERS_DB/schema.sql:

sql
-- SQL СХЕМА БАЗЫ ДАННЫХ ДЛЯ ПАРТНЕРОВ
-- Блок A: База партнеров + верификация

-- Таблица партнеров
CREATE TABLE IF NOT EXISTS partners (
    id SERIAL PRIMARY KEY,
    partner_code VARCHAR(50) UNIQUE NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
    
    -- Юридические данные
    company_name VARCHAR(200) NOT NULL,
    legal_form VARCHAR(20) NOT NULL,
    inn VARCHAR(12) UNIQUE NOT NULL,
    ogrn VARCHAR(15),
    kpp VARCHAR(9),
    legal_address TEXT,
    actual_address TEXT,
    registration_date DATE,
    
    -- Контактные данные
    contact_person VARCHAR(100) NOT NULL,
    phone VARCHAR(20) NOT NULL,
    email VARCHAR(120) NOT NULL,
    website VARCHAR(200),
    telegram VARCHAR(50),
    whatsapp VARCHAR(20),
    
    -- Профиль услуг
    main_category VARCHAR(50) NOT NULL,
    specializations JSONB DEFAULT '[]',
    services JSONB DEFAULT '[]',
    
    -- География
    regions JSONB DEFAULT '[]',
    cities JSONB DEFAULT '[]',
    radius_km INTEGER DEFAULT 50,
    
    -- Верификация
    verification_status VARCHAR(20) NOT NULL DEFAULT 'pending',
    verification_date TIMESTAMP,
    verified_by VARCHAR(50),
    documents JSONB DEFAULT '[]',
    rejection_reason TEXT,
    
    -- Статус и настройки
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    subscription_type VARCHAR(20) NOT NULL DEFAULT 'free',
    subscription_expires TIMESTAMP,
    max_active_leads INTEGER DEFAULT 3,
    
    -- Рейтинг и статистика
    rating FLOAT DEFAULT 0.0,
    completed_projects INTEGER DEFAULT 0,
    response_rate FLOAT DEFAULT 0.0,
    
    -- Технические поля
    settings JSONB DEFAULT '{}',
    
    -- Индексы для быстрого поиска
    CONSTRAINT check_rating_range CHECK (rating >= 0 AND rating <= 5),
    CONSTRAINT check_response_rate CHECK (response_rate >= 0 AND response_rate <= 100)
);

-- Индексы для таблицы partners
CREATE INDEX idx_partners_verification_status ON partners(verification_status);
CREATE INDEX idx_partners_is_active ON partners(is_active);
CREATE INDEX idx_partners_regions ON partners USING GIN(regions);
CREATE INDEX idx_partners_specializations ON partners USING GIN(specializations);
CREATE INDEX idx_partners_rating ON partners(rating DESC);
CREATE INDEX idx_partners_created_at ON partners(created_at DESC);

-- Таблица логов верификации
CREATE TABLE IF NOT EXISTS partner_verification_logs (
    id SERIAL PRIMARY KEY,
    partner_id INTEGER NOT NULL REFERENCES partners(id) ON DELETE CASCADE,
    partner_code VARCHAR(50) NOT NULL,
    
    -- Детали действия
    action VARCHAR(50) NOT NULL,
    status VARCHAR(20) NOT NULL,
    details JSONB,
    
    -- Кто выполнил
    performed_by VARCHAR(50),
    performed_at TIMESTAMP NOT NULL DEFAULT NOW(),
    
    -- Индексы
    INDEX idx_verification_logs_partner_id (partner_id),
    INDEX idx_verification_logs_performed_at (performed_at DESC)
);

-- Функция для автоматического обновления updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Триггер для автоматического обновления updated_at
CREATE TRIGGER update_partners_updated_at BEFORE UPDATE
ON partners FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Представление для быстрого доступа к верифицированным партнерам
CREATE OR REPLACE VIEW verified_partners AS
SELECT 
    p.partner_code,
    p.company_name,
    p.legal_form,
    p.inn,
    p.contact_person,
    p.phone,
    p.email,
    p.main_category,
    p.specializations,
    p.services,
    p.regions,
    p.cities,
    p.rating,
    p.completed_projects,
    p.response_rate,
    p.subscription_type
FROM partners p
WHERE p.verification_status = 'verified' 
  AND p.is_active = TRUE
  AND (p.subscription_expires IS NULL OR p.subscription_expires > NOW());

-- Статистика партнеров
CREATE OR REPLACE VIEW partners_statistics AS
SELECT 
    COUNT(*) as total_partners,
    COUNT(CASE WHEN verification_status = 'verified' THEN 1 END) as verified_partners,
    COUNT(CASE WHEN verification_status = 'pending' THEN 1 END) as pending_partners,
    COUNT(CASE WHEN is_active = TRUE THEN 1 END) as active_partners,
    AVG(rating) as average_rating,
    SUM(completed_projects) as total_projects
FROM partners;

-- Комментарии к таблицам
COMMENT ON TABLE partners IS 'Таблица партнеров (строительных компаний)';
COMMENT ON COLUMN partners.partner_code IS 'Уникальный код партнера в системе';
COMMENT ON COLUMN partners.verification_status IS 'Статус верификации: pending, verified, rejected';
COMMENT ON COLUMN partners.subscription_type IS 'Тип подписки: free, basic, premium';

COMMENT ON TABLE partner_verification_logs IS 'Логи верификации партнеров';
COMMENT ON COLUMN partner_verification_logs.action IS 'Тип действия: inn_check, document_upload, manual_review';
COMMENT ON COLUMN partner_verification_logs.status IS 'Результат: success, failed, pending';
📁 BLOCK_A_PARTNERS_DB/partner_manager.py:

python
"""
МЕНЕДЖЕР ДЛЯ РАБОТЫ С ПАРТНЕРАМИ
CRUD операции и бизнес-логика
"""

from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from .models import db, Partner, PartnerVerificationLog

class PartnerManager:
    """Менеджер для работы с партнерами"""
    
    @staticmethod
    def create_partner(data: Dict[str, Any]) -> Dict[str, Any]:
        """Создание нового партнера"""
        try:
            # Генерация кода партнера
            from datetime import datetime
            import random
            
            date_str = datetime.now().strftime('%y%m%d')
            random_num = random.randint(1000, 9999)
            partner_code = f"P-{date_str}-{random_num}"
            
            partner = Partner(
                partner_code=partner_code,
                company_name=data['company_name'],
                legal_form=data.get('legal_form', 'ООО'),
                inn=data['inn'],
                contact_person=data['contact_person'],
                phone=data['phone'],
                email=data['email'],
                verification_status='pending',
                is_active=False
            )
            
            db.session.add(partner)
            db.session.commit()
            
            return {
                'success': True,
                'partner': partner.to_dict(),
                'message': 'Партнер создан успешно'
            }
            
        except Exception as e:
            db.session.rollback()
            return {
                'success': False,
                'error': f'Ошибка создания партнера: {str(e)}'
            }
    
    @staticmethod
    def update_partner(partner_code: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Обновление данных партнера"""
        try:
            partner = Partner.query.filter_by(partner_code=partner_code).first()
            if not partner:
                return {'success': False, 'error': 'Партнер не найден'}
            
            # Поля, которые можно обновлять
            updatable_fields = [
                'company_name', 'contact_person', 'phone', 'email', 'website',
                'main_category', 'specializations', 'services', 'regions', 'cities',
                'radius_km', 'settings'
            ]
            
            for field in updatable_fields:
                if field in data:
                    setattr(partner, field, data[field])
            
            partner.updated_at = datetime.utcnow()
            db.session.commit()
            
            return {
                'success': True,
                'partner': partner.to_dict(),
                'message': 'Данные партнера обновлены'
            }
            
        except Exception as e:
            db.session.rollback()
            return {
                'success': False,
                'error': f'Ошибка обновления партнера: {str(e)}'
            }
    
    @staticmethod
    def verify_partner(partner_code: str, verified_by: str = 'system') -> Dict[str, Any]:
        """Верификация партнера"""
        try:
            partner = Partner.query.filter_by(partner_code=partner_code).first()
            if not partner:
                return {'success': False, 'error': 'Партнер не найден'}
            
            partner.verification_status = 'verified'
            partner.verification_date = datetime.utcnow()
            partner.verified_by = verified_by
            partner.is_active = True
            
            # Логирование
            log = PartnerVerificationLog(
                partner_id=partner.id,
                partner_code=partner_code,
                action='manual_verification',
                status='success',
                details={'verified_by': verified_by},
                performed_by=verified_by
            )
            db.session.add(log)
            
            db.session.commit()
            
            return {
                'success': True,
                'partner': partner.to_dict(),
                'message': 'Партнер успешно верифицирован'
            }
            
        except Exception as e:
            db.session.rollback()
            return {
                'success': False,
                'error': f'Ошибка верификации партнера: {str(e)}'
            }
    
    @staticmethod
    def search_partners(criteria: Dict[str, Any], page: int = 1, per_page: int = 10) -> Dict[str, Any]:
        """Поиск партнеров по критериям"""
        try:
            query = Partner.query.filter(
                Partner.verification_status == 'verified',
                Partner.is_active == True
            )
            
            # Применение фильтров
            if criteria.get('region'):
                query = query.filter(Partner.regions.contains([criteria['region']]))
            
            if criteria.get('specializations'):
                query = query.filter(
                    Partner.specializations.overlap(criteria['specializations'])
                )
            
            if criteria.get('main_category'):
                query = query.filter(Partner.main_category == criteria['main_category'])
            
            if criteria.get('min_rating'):
                query = query.filter(Partner.rating >= criteria['min_rating'])
            
            # Сортировка
            sort_by = criteria.get('sort_by', 'rating')
            sort_order = criteria.get('sort_order', 'desc')
            
            if sort_by == 'rating':
                if sort_order == 'desc':
                    query = query.order_by(Partner.rating.desc())
                else:
                    query = query.order_by(Partner.rating.asc())
            elif sort_by == 'response_rate':
                if sort_order == 'desc':
                    query = query.order_by(Partner.response_rate.desc())
                else:
                    query = query.order_by(Partner.response_rate.asc())
            else:
                query = query.order_by(Partner.created_at.desc())
            
            # Пагинация
            pagination = query.paginate(page=page, per_page=per_page, error_out=False)
            
            return {
                'success': True,
                'partners': [p.to_dict() for p in pagination.items],
                'pagination': {
                    'page': pagination.page,
                    'per_page': pagination.per_page,
                    'total': pagination.total,
                    'pages': pagination.pages
                }
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Ошибка поиска партнеров: {str(e)}'
            }
    
    @staticmethod
    def get_partner_stats() -> Dict[str, Any]:
        """Получение статистики по партнерам"""
        try:
            total = Partner.query.count()
            verified = Partner.query.filter_by(verification_status='verified').count()
            active = Partner.query.filter_by(is_active=True).count()
            pending = Partner.query.filter_by(verification_status='pending').count()
            
            return {
                'success': True,
                'stats': {
                    'total_partners': total,
                    'verified_partners': verified,
                    'active_partners': active,
                    'pending_verification': pending,
                    'verified_percentage': round((verified / total * 100) if total > 0 else 0, 2)
                }
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Ошибка получения статистики: {str(e)}'
            }
📁 BLOCK_A_PARTNERS_DB/config.py:

python
"""
КОНФИГУРАЦИЯ БЛОКА A
"""

import os
from typing import Dict, Any

class BlockAConfig:
    """Конфигурация для блока A (База партнеров)"""
    
    # Настройки базы данных
    DATABASE_CONFIG = {
        'pool_size': 10,
        'max_overflow': 20,
        'pool_timeout': 30,
        'pool_recycle': 3600,
        'echo': False
    }
    
    # Настройки верификации
    VERIFICATION_CONFIG = {
        'inn_check_timeout': 10,  # секунд
        'max_retries': 3,
        'cache_ttl': 3600,  # кэширование результатов на 1 час
        'auto_verify_after_days': 7  # автоматическая верификация через 7 дней
    }
    
    # Настройки поиска
    SEARCH_CONFIG = {
        'default_per_page': 10,
        'max_per_page': 50,
        'default_sort': 'rating_desc',
        'search_timeout': 5
    }
    
    # Категории партнеров (согласно ТЗ)
    PARTNER_CATEGORIES = [
        'подрядчик',
        'производитель', 
        'продавец',
        'исполнитель'
    ]
    
    # Специализации (согласно ТЗ)
    SPECIALIZATIONS = [
        'каркасные дома',
        'кирпичные дома',
        'отделочные работы',
        'кровельные работы',
        'фундаменты',
        'электромонтаж',
        'сантехника',
        'окна и двери',
        'отопление и вентиляция',
        'ландшафтный дизайн'
    ]
    
    # Регионы работы
    REGIONS = [
        'Московская область',
        'Ленинградская область',
        'Краснодарский край',
        'Свердловская область',
        'Новосибирская область',
        'Республика Татарстан',
        'Ростовская область',
        'Челябинская область',
        'Нижегородская область',
        'Самарская область'
    ]
    
    @classmethod
    def get_database_url(cls) -> str:
        """Получение URL базы данных из переменных окружения"""
        return os.getenv('DATABASE_URL', 'postgresql://user:password@localhost:5432/haus_price_db')
    
    @classmethod
    def get_fns_api_key(cls) -> str:
        """Получение ключа API ФНС"""
        return os.getenv('FNS_API_KEY', '')
    
    @classmethod
    def to_dict(cls) -> Dict[str, Any]:
        """Преобразование конфигурации в словарь"""
        return {
            'database': cls.DATABASE_CONFIG,
            'verification': cls.VERIFICATION_CONFIG,
            'search': cls.SEARCH_CONFIG,
            'categories': cls.PARTNER_CATEGORIES,
            'specializations': cls.SPECIALIZATIONS,
            'regions': cls.REGIONS
        }
📁 BLOCK_A_PARTNERS_DB/seed_data.py:

python
"""
СЕЕД-ДАННЫЕ ДЛЯ ТЕСТИРОВАНИЯ БЛОКА A
Тестовые данные для демонстрации работы системы
"""

import random
from datetime import datetime, timedelta
from .models import db, Partner

def seed_test_partners(count: int = 20):
    """Создание тестовых партнеров"""
    
    # Тестовые данные
    companies = [
        "ООО 'СтройДом'", "ИП 'МастерОтделка'", "ООО 'ФундаментПро'", 
        "АО 'КровельныеТехнологии'", "ООО 'КаркасныеДома'", "ИП 'ЭлектроМастер'",
        "ООО 'СантехникПро'", "ИП 'ОкнаМир'", "ООО 'ТеплоДом'", "АО 'ЛандшафтДизайн'"
    ]
    
    categories = ['подрядчик', 'производитель', 'продавец', 'исполнитель']
    specializations_list = [
        ['каркасные дома', 'фундаменты'],
        ['отделочные работы', 'окна и двери'],
        ['кровельные работы'],
        ['электромонтаж'],
        ['сантехника'],
        ['отопление и вентиляция'],
        ['ландшафтный дизайн']
    ]
    
    regions_list = [
        ['Московская область', 'Москва'],
        ['Ленинградская область', 'Санкт-Петербург'],
        ['Краснодарский край', 'Сочи', 'Краснодар'],
        ['Свердловская область', 'Екатеринбург'],
        ['Республика Татарстан', 'Казань']
    ]
    
    created = 0
    
    for i in range(count):
        company = random.choice(companies)
        inn = f"{random.randint(1000000000, 9999999999)}"
        
        partner = Partner(
            partner_code=f"P-TEST-{i+1:04d}",
            company_name=f"{company} Тестовая",
            legal_form=random.choice(['ООО', 'ИП', 'АО']),
            inn=inn,
            ogrn=f"{random.randint(1000000000000, 9999999999999)}",
            contact_person=f"Иванов Иван Иванович {i+1}",
            phone=f"+7{random.randint(9000000000, 9999999999)}",
            email=f"test{i+1}@example.com",
            website=f"https://example{i+1}.com",
            
            main_category=random.choice(categories),
            specializations=random.choice(specializations_list),
            
            services=[
                {
                    "service_name": "Строительство каркасного дома",
                    "description": "Полный цикл строительства",
                    "price_range": {"min": 1500000, "max": 3000000, "currency": "RUB"},
                    "unit": "проект"
                }
            ],
            
            regions=random.choice(regions_list)[:1],
            cities=random.choice(regions_list)[1:],
            radius_km=random.randint(50, 300),
            
            verification_status='verified',
            verification_date=datetime.utcnow() - timedelta(days=random.randint(1, 30)),
            verified_by='system',
            
            is_active=True,
            subscription_type=random.choice(['free', 'basic', 'premium']),
            subscription_expires=datetime.utcnow() + timedelta(days=random.randint(30, 365)),
            
            rating=round(random.uniform(3.5, 5.0), 1),
            completed_projects=random.randint(5, 100),
            response_rate=round(random.uniform(70, 100), 1)
        )
        
        db.session.add(partner)
        created += 1
    
    try:
        db.session.commit()
        print(f"✅ Создано {created} тестовых партнеров")
        return {'success': True, 'created': created}
    except Exception as e:
        db.session.rollback()
        print(f"❌ Ошибка при создании тестовых данных: {e}")
        return {'success': False, 'error': str(e)}

def clear_test_data():
    """Очистка тестовых данных"""
    try:
        deleted = Partner.query.filter(Partner.partner_code.like('P-TEST-%')).delete()
        db.session.commit()
        print(f"✅ Удалено {deleted} тестовых записей")
        return {'success': True, 'deleted': deleted}
    except Exception as e:
        db.session.rollback()
        print(f"❌ Ошибка при удалении тестовых данных: {e}")
        return {'success': False, 'error': str(e)}

if __name__ == "__main__":
    # Для запуска из командной строки
    import sys
    from flask import Flask
    
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    db.init_app(app)
    
    with app.app_context():
        db.create_all()
        
        if len(sys.argv) > 1 and sys.argv[1] == 'clear':
            clear_test_data()
        else:
            seed_test_partners(10)
📁 BLOCK_A_PARTNERS_DB/README.md:

markdown
# 🗃️ БЛОК A: БАЗА ПАРТНЕРОВ + ВЕРИФИКАЦИЯ

## 🎯 ЦЕЛЬ БЛОКА
Создать ядро системы - базу верифицированных партнеров с услугами и ценами.

## 📊 СТРУКТУРА ДАННЫХ
Согласно ТЗ, партнер содержит:

### Юридические данные:
- `company_name` - название компании
- `legal_form` - ООО, ИП, АО
- `inn` (ИНН) - ключевое для верификации
- `ogrn` - ОГРН
- `legal_address` - юридический адрес
- `actual_address` - фактический адрес

### Контактные данные:
- `phone` - телефон
- `email` - email
- `website` - сайт (опционально)
- `contact_person` - ФИО представителя

### Профиль услуг:
- `main_category` - основная категория
- `specializations` - специализации
- `services` - массив услуг с ценами

### География:
- `regions` - регионы работы
- `cities` - города работы
- `radius_km` - радиус работы

### Верификация:
- `verification_status` - статус верификации
- `verification_date` - дата верификации
- `documents` - документы

## 🔐 ПРОЦЕСС ВЕРИФИКАЦИИ
ВХОДНЫЕ ДАННЫЕ → ПРОВЕРКА → ВЕРИФИКАЦИЯ → АКТИВАЦИЯ

РЕГИСТРАЦИЯ:

Партнер заполняет форму в боте/ЛК

Основные данные: название, ИНН, контакты

ПРОВЕРКА ЧЕРЕЗ API ФНС:

Автоматическая проверка ИНН в ЕГРЮЛ/ЕГРИП

Подтверждение юридического статуса

Проверка действующей регистрации

ВЕРИФИКАЦИЯ ДОКУМЕНТОВ:

Загрузка сканов документов

Проверка реквизитов

Подтверждение специализаций

АКТИВАЦИЯ:

Активация аккаунта

Назначение тарифа

Доступ к базе заказчиков

text

## 📁 ФАЙЛЫ БЛОКА

### Основные файлы:
1. **models.py** - SQLAlchemy модели партнеров и логов верификации
2. **api_routes.py** - Flask роуты для API партнеров
3. **verification_service.py** - сервис верификации через API ФНС
4. **partner_manager.py** - CRUD операции с партнерами
5. **schema.sql** - SQL схемы таблиц
6. **config.py** - конфигурация блока
7. **seed_data.py** - тестовые данные для демо

## 🚀 БЫСТРЫЙ СТАРТ

### 1. Установка зависимостей:
```bash
cd BLOCK_A_PARTNERS_DB
pip install -r ../requirements.txt
2. Настройка базы данных:
bash
# Создание БД
createdb haus_price_db

# Применение схемы
psql haus_price_db < schema.sql
3. Настройка переменных окружения:
bash
cp .env.example .env
# Отредактируйте .env файл
4. Запуск тестовых данных:
python
python seed_data.py
5. Запуск API:
python
# Создайте app.py с:
from flask import Flask
from .models import db
from .api_routes import partner_bp

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://...'
app.register_blueprint(partner_bp)

db.init_app(app)

if __name__ == '__main__':
    app.run(debug=True)
📊 API ЭНДПОИНТЫ
Регистрация партнера:
http
POST /api/v1/partners/register
Content-Type: application/json

{
  "company_name": "ООО 'СтройДом'",
  "legal_form": "ООО",
  "inn": "7712345678",
  "contact_person": "Иван Иванов",
  "phone": "+79991234567",
  "email": "info@stroydom.ru"
}
Поиск партнеров:
http
POST /api/v1/partners/search
Content-Type: application/json

{
  "region": "Московская область",
  "specializations": ["каркасные дома"],
  "page": 1,
  "per_page": 10
}
Получение партнера:
http
GET /api/v1/partners/{partner_code}
Обновление профиля:
http
PUT /api/v1/partners/{partner_code}/profile
Content-Type: application/json

{
  "main_category": "подрядчик",
  "specializations": ["каркасные дома", "отделка"],
  "regions": ["Московская область"]
}
🧪 ТЕСТИРОВАНИЕ
Запуск тестов:
bash
pytest tests/test_block_a/
Основные тесты:
Тестирование моделей (test_models.py)

Тестирование верификации (test_verification.py)

Тестирование API (test_api_routes.py)

🔗 ИНТЕГРАЦИЯ С ДРУГИМИ БЛОКАМИ
С блоком B (Бот-проводник):
Бот отправляет запросы на регистрацию

Бот получает данные партнеров для показа заказчикам

С блоком C (Интеграции):
Интеграция с API ФНС для верификации

Интеграция с Tilda для личного кабинета

С блоком D (Монетизация):
Хранение данных о подписках

Ограничения по тарифам

📈 СТАТУС РАЗРАБОТКИ
Модели данных

SQL схемы

API роуты

Сервис верификации

Тестовые данные

Интеграция с API ФНС (реальная)

Документация API

Тестирование

🆘 ПОДДЕРЖКА
Для вопросов и помощи:

Ознакомьтесь с комментариями в коде

Проверьте тесты

Создайте issue в репозитории

Блок A является фундаментом всей системы. Без работающей базы партнеров невозможна работа других блоков.
