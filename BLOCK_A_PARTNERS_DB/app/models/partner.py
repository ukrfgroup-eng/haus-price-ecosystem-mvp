from app import db
from datetime import datetime
import uuid

class Partner(db.Model):
    __tablename__ = 'partners'

    id = db.Column(db.Integer, primary_key=True)
    partner_id = db.Column(db.String(50), unique=True, nullable=False, default=lambda: f"P{uuid.uuid4().hex[:8].upper()}")
    inn = db.Column(db.String(12), unique=True, nullable=False, index=True)
    name = db.Column(db.String(200), nullable=False)
    phone = db.Column(db.String(20))
    email = db.Column(db.String(100))
    legal_form = db.Column(db.String(50))  # ООО, ИП и т.д.
    verification_status = db.Column(db.String(20), default='pending')  # pending, verified, rejected
    is_active = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'partner_id': self.partner_id,
            'inn': self.inn,
            'name': self.name,
            'phone': self.phone,
            'email': self.email,
            'legal_form': self.legal_form,
            'verification_status': self.verification_status,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
