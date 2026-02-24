from flask import Blueprint, request, jsonify, current_app
from app.services.partner_service import create_partner, get_partner_by_inn
from app import db
from app.models import Partner, Service, ClientRequest, Lead, Recommendation
from app.analyzer import parse_query
import logging
import random
from datetime import datetime

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

@bp.route('/analyze', methods=['POST'])
def analyze():
    data = request.get_json()
    if not data or 'text' not in data:
        return jsonify({'error': 'Missing text'}), 400

    text = data['text']
    parsed = parse_query(text)

    # Логируем
    current_app.logger.info(f"Analyzed text: {text} -> {parsed}")

    # Сохраняем запрос в БД (поле session_id опущено, т.к. не передаётся)
    client_req = ClientRequest(
        raw_text=text,
        parsed_params=parsed
    )
    db.session.add(client_req)
    db.session.commit()

    return jsonify(parsed), 200

@bp.route('/search', methods=['POST'])
def search():
    data = request.get_json() or {}
    text = data.get('text', '')

    # Сохраняем запрос
    parsed = parse_query(text) if text else {}
    client_req = ClientRequest(
        raw_text=text,
        parsed_params=parsed
    )
    db.session.add(client_req)
    db.session.commit()

    # Заглушка: возвращаем фиксированный список партнёров
    # В будущем здесь будет реальный поиск по БД
    mock_partners = [
        {"id": 1, "name": "СтройДом", "rating": 4.5, "verified": True},
        {"id": 2, "name": "ЭкоДрев", "rating": 4.8, "verified": True},
        {"id": 3, "name": "КаркасСтрой", "rating": 4.2, "verified": False},
        {"id": 4, "name": "ДомСтрой", "rating": 4.9, "verified": True},
        {"id": 5, "name": "УютСервис", "rating": 4.0, "verified": False}
    ]
    return jsonify(mock_partners), 200

@bp.route('/stats', methods=['GET'])
def stats():
    # Генерируем синтетическую статистику
    stats_data = {
        "active_clients": random.randint(1000, 1500),
        "requests_today": random.randint(50, 150),
        "partners_online": random.randint(10, 50)
    }
    return jsonify(stats_data), 200

@bp.route('/partners/<int:id>/verify', methods=['PUT'])
def update_verified(id):
    partner = Partner.query.get_or_404(id)
    data = request.get_json()
    if 'verified' not in data:
        return jsonify({'error': 'Missing verified field'}), 400

    partner.verified = bool(data['verified'])
    db.session.commit()

    current_app.logger.info(f"Partner {id} verified set to {partner.verified}")
    return jsonify({'id': partner.id, 'verified': partner.verified}), 200

@bp.route('/partners/<int:id>/tariff', methods=['PUT'])
def update_tariff(id):
    partner = Partner.query.get_or_404(id)
    data = request.get_json()
    if 'tariff' not in data:
        return jsonify({'error': 'Missing tariff field'}), 400

    partner.tariff = data['tariff']
    db.session.commit()

    current_app.logger.info(f"Partner {id} tariff set to {partner.tariff}")
    return jsonify({'id': partner.id, 'tariff': partner.tariff}), 200
