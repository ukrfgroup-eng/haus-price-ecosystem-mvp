# Добавьте импорт
from backend.routes.payment_routes import payment_bp

# После создания app регистрируйте blueprint
app.register_blueprint(payment_bp)
