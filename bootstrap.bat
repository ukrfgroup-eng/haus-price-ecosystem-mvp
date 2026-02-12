@echo off
setlocal enabledelayedexpansion

echo [1/9] Проверка наличия репозитория...
if not exist haus-price-ecosystem-mvp (
    git clone https://github.com/ukrfgroup-англ/haus-price-ecosystem-mvp.git
)
cd haus-price-ecosystem-mvp

echo [2/9] Создание недостающих папок...
if not exist block_b mkdir block_b
if not exist block_c mkdir block_c
if not exist block_d mkdir block_d
if not exist tests\mocks mkdir tests\mocks
if not exist logs mkdir logs

echo [3/9] Копирование корневого .env...
if not exist .env (
    copy .env.example .env
) else (
    echo .env уже существует, пропускаем
)

echo [4/9] Копирование .env в блоки...
copy .env BLOCK_A_PARTNERS_DB\.env
copy .env block_b\.env 2>nul
copy .env block_c\.env 2>nul
copy .env block_d\.env 2>nul

echo [5/9] Копирование локальных .env.example...
copy BLOCK_A_PARTNERS_DB\.env.example BLOCK_A_PARTNERS_DB\.env /Y
copy block_b\.env.example block_b\.env /Y 2>nul
copy block_c\.env.example block_c\.env /Y 2>nul
copy block_d\.env.example block_d\.env /Y 2>nul

echo [6/9] Запуск Docker контейнеров...
docker-compose up -d
if %errorlevel% neq 0 (
    echo Ошибка запуска Docker. Убедитесь, что Docker Desktop запущен.
    pause
    exit /b
)

echo [7/9] Ожидание готовности БД...
timeout /t 15 /nobreak

echo [8/9] Установка зависимостей и миграции Блока A...
cd BLOCK_A_PARTNERS_DB
python -m venv venv
call venv\Scripts\activate.bat
pip install -r requirements.txt
set FLASK_APP=run.py
flask db upgrade
cd ..

echo [9/9] Проверка доступности сервисов...
timeout /t 10 /nobreak
curl http://localhost:5000/health

echo ✅ Среда успешно развёрнута!
pause
