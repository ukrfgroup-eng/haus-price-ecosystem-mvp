@echo off
setlocal enabledelayedexpansion

echo [1/8] Клонирование репозитория (пропускаем, если уже есть)...
if not exist haus-price-ecosystem-mvp (
    git clone https://github.com/ukrfgroup-англ/haus-price-ecosystem-mvp.git
)
cd haus-price-ecosystem-mvp

echo [2/8] Создание недостающих папок...
if not exist block_b mkdir block_b
if not exist block_c mkdir block_c
if not exist block_d mkdir block_d
if not exist tests\mocks mkdir tests\mocks
if not exist logs mkdir logs

echo [3/8] Копирование корневого .env...
if not exist .env (
    copy .env.example .env
) else (
    echo .env уже существует, пропускаем
)

echo [4/8] Копирование .env в блоки...
copy .env BLOCK_A_PARTNERS_DB\.env
copy .env block_b\.env 2>nul
copy .env block_c\.env 2>nul
copy .env block_d\.env 2>nul

echo [5/8] Копирование локальных .env.example...
copy BLOCK_A_PARTNERS_DB\.env.example BLOCK_A_PARTNERS_DB\.env /Y
copy block_b\.env.example block_b\.env /Y 2>nul
copy block_c\.env.example block_c\.env /Y 2>nul
copy block_d\.env.example block_d\.env /Y 2>nul

echo [6/8] Запуск Docker контейнеров...
docker-compose up -d
if %errorlevel% neq 0 (
    echo Ошибка запуска Docker. Убедитесь, что Docker Desktop запущен.
    pause
    exit /b
)

echo [7/8] Ожидание готовности БД...
timeout /t 15 /nobreak

echo [8/8] Установка зависимостей и миграции Блока A...
cd BLOCK_A_PARTNERS_DB
if %errorlevel% neq 0 (
    echo Ошибка: папка BLOCK_A_PARTNERS_DB не найдена!
    pause
    exit /b
)

python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Ошибка: Python не установлен или не добавлен в PATH
    pause
    exit /b
)

python -m venv venv
if %errorlevel% neq 0 (
    echo Ошибка создания виртуального окружения
    pause
    exit /b
)

call venv\Scripts\activate.bat
if %errorlevel% neq 0 (
    echo Ошибка активации виртуального окружения
    pause
    exit /b
)

pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo Ошибка установки зависимостей
    pause
    exit /b
)

set FLASK_APP=run.py
flask db upgrade
if %errorlevel% neq 0 (
    echo Ошибка применения миграций
    pause
    exit /b
)

cd ..

echo [9/9] Проверка доступности сервисов...
timeout /t 10 /nobreak
curl http://localhost:5000/health
if %errorlevel% neq 0 (
    echo Внимание: сервис block-a не отвечает. Проверьте логи Docker.
)

echo ✅ Среда успешно развёрнута!
pause
