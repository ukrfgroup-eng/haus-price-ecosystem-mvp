#!/bin/bash
set -e

echo "[1/9] Клонирование репозитория..."
if [ ! -d "haus-price-ecosystem-mvp" ]; then
    git clone https://github.com/ukrfgroup-англ/haus-price-ecosystem-mvp.git
fi
cd haus-price-ecosystem-mvp

echo "[2/9] Создание недостающих папок..."
mkdir -p block_b block_c block_d tests/mocks logs

echo "[3/9] Копирование корневого .env..."
if [ ! -f ".env" ]; then
    cp .env.example .env
else
    echo ".env уже существует, пропускаем"
fi

echo "[4/9] Копирование .env в блоки..."
cp .env BLOCK_A_PARTNERS_DB/.env
cp .env block_b/.env 2>/dev/null || :
cp .env block_c/.env 2>/dev/null || :
cp .env block_d/.env 2>/dev/null || :

echo "[5/9] Копирование локальных .env.example..."
cp BLOCK_A_PARTNERS_DB/.env.example BLOCK_A_PARTNERS_DB/.env
cp block_b/.env.example block_b/.env 2>/dev/null || :
cp block_c/.env.example block_c/.env 2>/dev/null || :
cp block_d/.env.example block_d/.env 2>/dev/null || :

echo "[6/9] Запуск Docker контейнеров..."
docker-compose up -d

echo "[7/9] Ожидание готовности БД..."
sleep 15

echo "[8/9] Установка зависимостей и миграции Блока A..."
cd BLOCK_A_PARTNERS_DB
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
export FLASK_APP=run.py
flask db upgrade
cd ..

echo "[9/9] Проверка доступности сервисов..."
sleep 10
curl http://localhost:5000/health

echo "✅ Среда успешно развёрнута!"
