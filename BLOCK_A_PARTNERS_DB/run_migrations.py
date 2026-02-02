#!/usr/bin/env python3
"""
Скрипт для запуска миграций базы данных
"""

import os
import sys
from models.base import create_tables

if __name__ == "__main__":
    print("🔄 Запуск миграций базы данных...")
    
    try:
        # Создаем таблицы через SQLAlchemy
        create_tables()
        
        # Или используем Alembic
        os.system("alembic upgrade head")
        
        print("✅ Миграции успешно выполнены!")
        
    except Exception as e:
        print(f"❌ Ошибка при выполнении миграций: {e}")
        sys.exit(1)
