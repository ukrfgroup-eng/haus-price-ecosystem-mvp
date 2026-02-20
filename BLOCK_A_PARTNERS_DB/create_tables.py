from run import create_app
from app import db

app = create_app()
with app.app_context():
    db.create_all()
    print("Таблицы успешно созданы!")
