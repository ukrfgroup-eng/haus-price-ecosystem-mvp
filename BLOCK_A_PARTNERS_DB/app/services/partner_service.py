from app import db
from app.models import Partner
import uuid

def create_partner(data):
    """
    Создаёт нового партнёра из словаря data.
    Ожидаемые поля: inn, name (company_name), phone, email и др.
    Возвращает созданный объект Partner.
    """
    # Генерируем уникальный partner_id (короткий UUID)
    partner_id = str(uuid.uuid4())[:8]

    partner = Partner(
        partner_id=partner_id,
        company_name=data['name'],
        inn=data['inn'],
        contact_phone=data.get('phone'),
        contact_email=data.get('email'),
        # остальные поля опциональны
        verified=False,
        rating=0.0,
        tariff='base'
    )
    db.session.add(partner)
    db.session.commit()
    return partner

def get_partner_by_inn(inn):
    """Возвращает партнёра по ИНН или None."""
    return Partner.query.filter_by(inn=inn).first()
