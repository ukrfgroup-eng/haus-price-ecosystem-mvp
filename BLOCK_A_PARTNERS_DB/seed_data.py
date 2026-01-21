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
