from flask import Blueprint, request, jsonify
from app.services.partner_service import create_partner, get_partner_by_inn
from app import db

bp = Blueprint('api', __name__)

@bp.route('/partners', methods=['POST'])
def create_partner_endpoint():
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No input data'}), 400

    # Проверка обязательных полей
    required = ['inn', 'name']
    for field in required:
        if field not in data:
            return jsonify({'error': f'Missing field: {field}'}), 400

    # Проверка уникальности ИНН
    existing = get_partner_by_inn(data['inn'])
    if existing:
        return jsonify({'error': 'Partner with this INN already exists'}), 409

    # Создание партнёра
    partner = create_partner(data)
    return jsonify({'id': partner.partner_id}), 201
