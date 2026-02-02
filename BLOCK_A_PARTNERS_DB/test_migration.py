#!/usr/bin/env python3
"""
Тестирование миграций и работы базы данных
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from models.base import engine
    
    # Проверяем подключение к базе
    with engine.connect() as conn:
        result = conn.execute("SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public'")
        table_count = result.scalar()
        print(f"✅ База данных подключена. Таблиц: {table_count}")
        
        # Проверяем существование таблиц
        result = conn.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'")
        tables = [row[0] for row in result]
        print(f"✅ Таблицы в базе: {tables}")
        
        if 'partners' in tables:
            print("✅ Таблица 'partners' создана успешно")
        else:
            print("❌ Таблица 'partners' не найдена")
            
        if 'verification_logs' in tables:
            print("✅ Таблица 'verification_logs' создана успешно")
        else:
            print("❌ Таблица 'verification_logs' не найдена")
            
except Exception as e:
    print(f"❌ Ошибка: {e}")
    sys.exit(1)
