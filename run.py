#!/usr/bin/env python3
"""
Единая точка входа для Haus Price Ecosystem MVP
Запускает блок A (партнеры) как основной модуль
"""

import os
import sys

# Добавляем путь к блоку A
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'BLOCK_A_PARTNERS_DB'))

try:
    from BLOCK_A_PARTNERS_DB.run import app
    print("✅ Запуск блока A (партнеры)")
    
    if __name__ == '__main__':
        app.run(debug=True, host='0.0.0.0', port=5000)
        
except ImportError as e:
    print(f"❌ Ошибка импорта блока A: {e}")
    print("Убедитесь, что зависимости установлены: pip install -r BLOCK_A_PARTNERS_DB/requirements.txt")
    sys.exit(1)
