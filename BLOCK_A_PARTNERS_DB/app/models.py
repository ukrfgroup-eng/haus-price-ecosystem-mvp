from datetime import datetime
from app import db

class Partner(db.Model):
    __tablename__ = 'partners'

    id = db.Column(db.Integer, primary_key=True)
    partner_id = db.Column(db.String(50), unique=True, nullable=False)
    company_name = db.Column(db.String(200), nullable=False)
    inn = db.Column(db.String(12), unique=True, nullable=False)
    ogrn = db.Column(db.String(15))
    contact_email = db.Column(db.String(120))
    contact_phone = db.Column(db.String(20))
    website = db.Column(db.String(200))
    logo_url = db.Column(db.String(500))
    description = db.Column(db.Text)
    verified = db.Column(db.Boolean, default=False)
    rating = db.Column(db.Float, default=0.0)
    tariff = db.Column(db.String(20), default='base')  # base, pro, premium
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'partner_id': self.partner_id,
            'company_name': self.company_name,
            'inn': self.inn,
            'contact_phone': self.contact_phone,
            'contact_email': self.contact_email,
            'website': self.website,
            'rating': self.rating,
            'tariff': self.tariff,
            'verified': self.verified
        }

class Service(db.Model):
    __tablename__ = 'services'
    id = db.Column(db.Integer, primary_key=True)
    partner_id = db.Column(db.Integer, db.ForeignKey('partners.id'))
    category = db.Column(db.String(50))       # строительство, отделка, материалы, проект
    specialization = db.Column(db.String(100)) # каркасные, кирпичные, брус...
    price_min = db.Column(db.Integer)
    price_max = db.Column(db.Integer)
    region = db.Column(db.JSON)               # массив регионов РФ
    is_active = db.Column(db.Boolean, default=True)

class ClientRequest(db.Model):
    __tablename__ = 'client_requests'
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.String(100))    # Telegram id / UUID
    raw_text = db.Column(db.Text)
    parsed_params = db.Column(db.JSON)        # {region, budget, house_type, area}
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Recommendation(db.Model):
    __tablename__ = 'recommendations'
    id = db.Column(db.Integer, primary_key=True)
    request_id = db.Column(db.Integer, db.ForeignKey('client_requests.id'))
    partner_id = db.Column(db.Integer, db.ForeignKey('partners.id'))
    rank = db.Column(db.Integer)
    viewed = db.Column(db.Boolean, default=False)
    contacted = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Lead(db.Model):
    __tablename__ = 'leads'
    id = db.Column(db.Integer, primary_key=True)
    partner_id = db.Column(db.Integer, db.ForeignKey('partners.id'))
    client_contact = db.Column(db.String(100))  # телефон или email
    request_text = db.Column(db.Text)
    status = db.Column(db.String(20), default='new')  # new, contacted, closed
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
