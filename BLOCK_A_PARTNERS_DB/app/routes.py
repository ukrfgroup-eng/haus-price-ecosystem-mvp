from flask import request, jsonify
from app import bp

@bp.route('/health')
def health():
    return jsonify({"status": "ok", "block": "A"})

@bp.route('/analyze', methods=['POST'])
def analyze():
    """Анализ запроса клиента (заглушка)"""
    data = request.json
    # Здесь будет вызов ai_helpers.extract_params
    return jsonify({
        "intent": "search",
        "params": {"region": "Московская область", "budget": 3000000},
        "confidence": 0.95
    })

@bp.route('/search/partners', methods=['POST'])
def search_partners():
    """Подбор партнёров (заглушка)"""
    # Здесь будет вызов search_engine.search_partners
    return jsonify([
        {
            "partner_id": 1,
            "name": "СтройГрад",
            "contact": "+79991234567",
            "price_range": "2.5M-4M",
            "rating": 4.8
        }
    ])

@bp.route('/lead', methods=['POST'])
def lead():
    """Фиксация обращения клиента к партнёру"""
    return jsonify({"status": "ok"})

@bp.route('/partners', methods=['POST'])
def create_partner():
    """Создание нового партнёра (используется блоком C)"""
    return jsonify({"partner_id": 123})

@bp.route('/partners/<int:pid>', methods=['GET'])
def get_partner(pid):
    """Получение профиля партнёра"""
    return jsonify({"partner_id": pid, "name": "Тестовая компания"})

@bp.route('/partners/<int:pid>/tariff', methods=['PUT'])
def update_tariff(pid):
    """Смена тарифа (используется блоком D)"""
    return jsonify({"status": "ok"})
