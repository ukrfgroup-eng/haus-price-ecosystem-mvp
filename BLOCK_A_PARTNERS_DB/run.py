"""
Основной файл запуска Блока A
"""

from flask import Flask, jsonify
from flask_cors import CORS
from datetime import datetime
import logging
import os
import sys

# Добавляем путь для импорта модулей
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from api.routes import bp as partners_bp
from api.admin_routes import bp as admin_bp
from config import config
from models.base import engine
import sqlalchemy

# Настройка логирования
logging.basicConfig(
    level=getattr(logging, config.log_level.upper()),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('app.log')
    ]
)

logger = logging.getLogger(__name__)

# Создаем приложение Flask
app = Flask(__name__)

# Настройка CORS
CORS(app, resources={
    r"/api/*": {
        "origins": ["*"],  # В production заменить на конкретные домены
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization", "X-Requested-With"]
    }
})

# Конфигурация приложения
app.config['SECRET_KEY'] = config.api.secret_key
app.config['JSON_SORT_KEYS'] = False
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True

# Регистрируем Blueprints
app.register_blueprint(partners_bp)
app.register_blueprint(admin_bp)

@app.route('/')
def index():
    """Главная страница API"""
    return jsonify({
        'service': 'Block A - Partners Database & Verification',
        'version': '1.0.0',
        'status': 'running',
        'timestamp': datetime.utcnow().isoformat(),
        'endpoints': {
            'root': '/',
            'health': '/health',
            'partners_api': '/api/v1/partners',
            'admin_api': '/api/v1/admin',
            'documentation': '/docs'  # TODO: добавить Swagger
        }
    })

@app.route('/health')
def health_check():
    """Health check для мониторинга"""
    health_status = {
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat(),
        'services': {}
    }
    
    # Проверка базы данных
    try:
        with engine.connect() as conn:
            conn.execute(sqlalchemy.text("SELECT 1"))
        health_status['services']['database'] = {
            'status': 'healthy',
            'type': 'postgresql',
            'url': str(engine.url).replace(config.database.password, '***')
        }
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        health_status['services']['database'] = {
            'status': 'unhealthy',
            'error': str(e)
        }
        health_status['status'] = 'unhealthy'
    
    # Проверка Redis (если настроен)
    if hasattr(config, 'redis') and config.redis.host:
        try:
            import redis
            r = redis.Redis(
                host=config.redis.host,
                port=config.redis.port,
                password=config.redis.password,
                db=config.redis.db,
                socket_timeout=5
            )
            r.ping()
            health_status['services']['redis'] = {
                'status': 'healthy',
                'host': config.redis.host,
                'port': config.redis.port
            }
        except Exception as e:
            logger.warning(f"Redis health check failed: {e}")
            health_status['services']['redis'] = {
                'status': 'unhealthy',
                'error': str(e)
            }
            # Redis не критичен для работы, поэтому не меняем общий статус
    
    # Проверка API ключа ФНС
    if hasattr(config, 'fns') and config.fns.api_key:
        if config.fns.api_key and len(config.fns.api_key) > 10:
            health_status['services']['fns_api'] = {
                'status': 'configured',
                'note': 'API key is set'
            }
        else:
            health_status['services']['fns_api'] = {
                'status': 'mock_mode',
                'note': 'Using mock mode for development'
            }
    
    # Информация о приложении
    health_status['application'] = {
        'environment': config.env,
        'log_level': config.log_level,
        'host': config.api.host,
        'port': config.api.port,
        'debug': config.api.debug
    }
    
    return jsonify(health_status)

@app.route('/docs')
def api_docs():
    """Документация API (заглушка)"""
    return jsonify({
        'message': 'API Documentation',
        'note': 'Swagger/OpenAPI documentation will be available soon',
        'endpoints': [
            {'method': 'GET', 'path': '/api/v1/partners/search', 'description': 'Поиск партнеров'},
            {'method': 'POST', 'path': '/api/v1/partners/register', 'description': 'Регистрация партнера'},
            {'method': 'GET', 'path': '/api/v1/partners/<id>', 'description': 'Получение партнера'},
            {'method': 'PUT', 'path': '/api/v1/partners/<id>', 'description': 'Обновление партнера'},
            {'method': 'POST', 'path': '/api/v1/partners/<id>/verify', 'description': 'Верификация партнера'}
        ]
    })

if __name__ == '__main__':
    # Выводим информацию о запуске
    print(f"""
    🚀 ЗАПУСК БЛОКА A - ПАРТНЕРСКАЯ БАЗА ДАННЫХ
    {'='*50}
    
    📊 Конфигурация:
    • Режим: {config.env}
    • Логирование: {config.log_level}
    • API: http://{config.api.host}:{config.api.port}
    • База данных: {config.database.host}:{config.database.port}/{config.database.name}
    
    📡 Доступные эндпоинты:
    • GET  /              - Статус API
    • GET  /health        - Health check
    • GET  /docs          - Документация
    • POST /api/v1/partners/register - Регистрация партнера
    • GET  /api/v1/partners/search   - Поиск партнеров
    
    🔧 Отладка: {'Включена' if config.api.debug else 'Отключена'}
    
    Для остановки нажмите Ctrl+C
    """)
    
    # Запускаем приложение
    app.run(
        host=config.api.host,
        port=config.api.port,
        debug=config.api.debug,
        threaded=True,
        use_reloader=config.api.debug
    )
