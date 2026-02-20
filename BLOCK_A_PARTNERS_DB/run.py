import os
from flask import Flask, jsonify
from flask_migrate import Migrate
from dotenv import load_dotenv
from app import db   # db теперь импортируется из app/__init__.py

# Загружаем корневой .env (из родительской папки проекта)
env_path = os.path.join(os.path.dirname(__file__), '..', '.env')
load_dotenv(dotenv_path=env_path)
# Загружаем локальный .env (переопределяет)
load_dotenv()

migrate = Migrate()

def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)
    migrate.init_app(app, db)

    @app.route('/')
    def home():
        return jsonify({
            "name": "Block A - MATRIX CORE",
            "status": "running",
            "version": "0.1.0"
        })

    @app.route('/health')
    def health():
        return jsonify({"status": "ok", "block": "A"})

    # Регистрация blueprint'ов
    from app.routes import bp as api_bp
    app.register_blueprint(api_bp, url_prefix='/api/v1')

    return app

if __name__ == '__main__':
    app = create_app()
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
