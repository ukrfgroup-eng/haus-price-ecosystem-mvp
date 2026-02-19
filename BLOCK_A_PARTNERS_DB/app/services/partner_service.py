from app import db
from app.models.partner import Partner

def create_partner(data):
    """Создаёт нового партнёра в БД."""
    partner = Partner(
        inn=data['inn'],
        name=data['name'],
        phone=data.get('phone'),
        email=data.get('email'),
        legal_form=data.get('legal_form', 'unknown')
    )
    db.session.add(partner)
    db.session.commit()
    return partner

def get_partner_by_id(partner_id):
    return Partner.query.filter_by(partner_id=partner_id).first()

def get_partner_by_inn(inn):
    return Partner.query.filter_by(inn=inn).first()

def update_partner(partner, data):
    for key, value in data.items():
        if hasattr(partner, key) and key not in ['id', 'partner_id', 'created_at']:
            setattr(partner, key, value)
    db.session.commit()
    return partner
