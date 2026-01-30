"""
Административные API маршруты для управления партнерами
"""

from flask import Blueprint, request, jsonify
from datetime import datetime

bp = Blueprint('admin_api', __name__, url_prefix='/api/v1/admin')


@bp.route('/partners', methods=['GET'])
def get_all_partners():
    """
    Получение списка всех партнеров (с пагинацией)
    
    Query параметры:
    - page: номер страницы (default: 1)
    - page_size: размер страницы (default: 20)
    - status: фильтр по статусу (pending, verified, rejected)
    - sort_by: поле для сортировки (created_at, rating, etc.)
    """
    try:
        # Получаем параметры
        page = int(request.args.get('page', 1))
        page_size = int(request.args.get('page_size', 20))
        status_filter = request.args.get('status')
        sort_by = request.args.get('sort_by', 'created_at')
        
        # Заглушка - в реальности запрос к БД
        all_partners = _get_test_partners()
        
        # Фильтрация по статусу
        if status_filter:
            all_partners = [
                p for p in all_partners 
                if p['verification_status'] == status_filter
            ]
        
        # Сортировка
        if sort_by == 'created_at':
            all_partners.sort(key=lambda x: x['created_at'], reverse=True)
        elif sort_by == 'rating':
            all_partners.sort(key=lambda x: x['rating'], reverse=True)
        elif sort_by == 'company_name':
            all_partners.sort(key=lambda x: x['company_name'])
        
        # Пагинация
        total = len(all_partners)
        start_idx = (page - 1) * page_size
        end_idx = start_idx + page_size
        paginated = all_partners[start_idx:end_idx]
        
        return jsonify({
            'success': True,
            'partners': paginated,
            'pagination': {
                'page': page,
                'page_size': page_size,
                'total': total,
                'total_pages': (total + page_size - 1) // page_size
            }
        })
        
    except Exception as e:
        return jsonify({
            'error': f'Ошибка при получении партнеров: {str(e)}'
        }), 500


@bp.route('/partners/<partner_id>', methods=['GET'])
def get_partner_details(partner_id):
    """Получение детальной информации о партнере"""
    try:
        # Заглушка
        partner = {
            'id': partner_id,
            'company_name': 'ООО Тестовая компания',
            'inn': '1234567890',
            'verification_status': 'verified',
            'verification_score': 85.5,
            'documents': [
                {'type': 'inn', 'verified': True},
                {'type': 'ogrn', 'verified': True},
                {'type': 'passport', 'verified': True}
            ],
            'created_at': '2024-01-01T12:00:00',
            'last_activity': '2024-01-15T14:30:00',
            'statistics': {
                'total_leads': 15,
                'accepted_leads': 12,
                'completed_leads': 10,
                'avg_response_time': 2.5
            }
        }
        
        return jsonify({
            'success': True,
            'partner': partner
        })
        
    except Exception as e:
        return jsonify({
            'error': f'Ошибка при получении партнера: {str(e)}'
        }), 500


@bp.route('/partners/<partner_id>/verify', methods=['POST'])
def verify_partner_admin(partner_id):
    """
    Ручная верификация партнера администратором
    
    Request body:
    {
        "approved": true,
        "notes": "Все документы в порядке",
        "admin_id": "admin123"
    }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'Нет данных в запросе'}), 400
        
        approved = data.get('approved', False)
        notes = data.get('notes', '')
        admin_id = data.get('admin_id', 'unknown')
        
        # Здесь будет логика верификации
        # Пока заглушка
        
        action = 'approved' if approved else 'rejected'
        
        return jsonify({
            'success': True,
            'message': f'Партнер {action} администратором {admin_id}',
            'partner_id': partner_id,
            'approved': approved,
            'notes': notes,
            'verified_by': admin_id,
            'verified_at': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            'error': f'Ошибка при верификации: {str(e)}'
        }), 500


@bp.route('/partners/<partner_id>/status', methods=['PUT'])
def update_partner_status(partner_id):
    """
    Изменение статуса партнера
    
    Request body:
    {
        "status": "verified",  # или "rejected", "suspended"
        "reason": "Причина изменения статуса",
        "admin_id": "admin123"
    }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'Нет данных в запросе'}), 400
        
        status = data.get('status')
        reason = data.get('reason', '')
        admin_id = data.get('admin_id', 'unknown')
        
        # Проверяем валидность статуса
        valid_statuses = ['pending', 'verified', 'rejected', 'suspended']
        if status not in valid_statuses:
            return jsonify({
                'error': f'Некорректный статус. Допустимые: {", ".join(valid_statuses)}'
            }), 400
        
        # Здесь будет логика обновления статуса
        # Пока заглушка
        
        return jsonify({
            'success': True,
            'message': f'Статус партнера обновлен на {status}',
            'partner_id': partner_id,
            'new_status': status,
            'reason': reason,
            'updated_by': admin_id,
            'updated_at': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            'error': f'Ошибка при обновлении статуса: {str(e)}'
        }), 500


@bp.route('/partners/<partner_id>/block', methods=['POST'])
def block_partner(partner_id):
    """Блокировка партнера"""
    try:
        data = request.get_json() or {}
        reason = data.get('reason', 'Нарушение правил платформы')
        admin_id = data.get('admin_id', 'unknown')
        
        # Здесь будет логика блокировки
        # Пока заглушка
        
        return jsonify({
            'success': True,
            'message': 'Партнер заблокирован',
            'partner_id': partner_id,
            'blocked': True,
            'reason': reason,
            'blocked_by': admin_id,
            'blocked_at': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            'error': f'Ошибка при блокировке: {str(e)}'
        }), 500


@bp.route('/partners/<partner_id>/unblock', methods=['POST'])
def unblock_partner(partner_id):
    """Разблокировка партнера"""
    try:
        data = request.get_json() or {}
        admin_id = data.get('admin_id', 'unknown')
        
        # Здесь будет логика разблокировки
        # Пока заглушка
        
        return jsonify({
            'success': True,
            'message': 'Партнер разблокирован',
            'partner_id': partner_id,
            'blocked': False,
            'unblocked_by': admin_id,
            'unblocked_at': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            'error': f'Ошибка при разблокировке: {str(e)}'
        }), 500


@bp.route('/partners/stats', methods=['GET'])
def get_partners_stats():
    """Получение статистики по партнерам"""
    try:
        # Заглушка со статистикой
        stats = {
            'total_partners': 150,
            'verified_partners': 120,
            'pending_partners': 20,
            'rejected_partners': 10,
            'active_today': 45,
            'new_this_week': 15,
            'verification_rate': 80.0,  # процент верифицированных
            'avg_rating': 4.3,
            'total_reviews': 1250,
            'updated_at': datetime.utcnow().isoformat()
        }
        
        return jsonify({
            'success': True,
            'statistics': stats
        })
        
    except Exception as e:
        return jsonify({
            'error': f'Ошибка при получении статистики: {str(e)}'
        }), 500


def _get_test_partners():
    """Тестовые данные для администратора"""
    return [
        {
            'id': 'PART-001',
            'company_name': 'ООО СтройМастер',
            'inn': '7712345678',
            'verification_status': 'verified',
            'rating': 4.5,
            'created_at': '2024-01-01T10:00:00',
            'last_activity': '2024-01-15T14:30:00'
        },
        {
            'id': 'PART-002',
            'company_name': 'ИП Иванов Сантехник',
            'inn': '123456789012',
            'verification_status': 'verified',
            'rating': 4.2,
            'created_at': '2024-01-02T11:30:00',
            'last_activity': '2024-01-14T09:15:00'
        },
        {
            'id': 'PART-003',
            'company_name': 'ООО Электрик Профи',
            'inn': '7723456789',
            'verification_status': 'pending',
            'rating': 4.7,
            'created_at': '2024-01-03T14:45:00',
            'last_activity': '2024-01-13T16:20:00'
        },
        {
            'id': 'PART-004',
            'company_name': 'ООО Отделочные работы',
            'inn': '7734567890',
            'verification_status': 'verified',
            'rating': 4.0,
            'created_at': '2024-01-04T09:15:00',
            'last_activity': '2024-01-12T11:45:00'
        }
    ]
