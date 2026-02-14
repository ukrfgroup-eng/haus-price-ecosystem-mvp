@echo off
echo [1/8] Клонирование репозитория...
git clone https://github.com/ВАШ_ЛОГИН/haus-price-ecosystem-mvp.git
cd haus-price-ecosystem-mvp

echo [2/8] Создание недостающих папок и файлов-заглушек...
if not exist block_b mkdir block_b
if not exist block_c mkdir block_c
if not exist block_d mkdir block_d
if not exist tests\mocks mkdir tests\mocks

echo [3/8] Копирование .env...
copy .env.example .env
copy block_a\.env.example block_a\.env
copy block_b\.env.example block_b\.env 2>nul
copy block_c\.env.example block_c\.env 2>nul
copy block_d\.env.example block_d\.env 2>nul

echo [4/8] Запуск Docker контейнеров...
docker-compose up -d
if %errorlevel% neq 0 ( echo Ошибка запуска Docker & pause & exit /b )

echo [5/8] Ожидание готовности БД...
timeout /t 10 /nobreak

echo [6/8] Установка зависимостей и миграции Блока A...
cd block_a
python -m venv venv
call venv\Scripts\activate.bat
pip install -r requirements.txt
flask db upgrade
cd ..

echo [7/8] Запуск заглушек внешних сервисов (моки)...
start python tests\mocks\mock_protalk.py
start python tests\mocks\mock_tilda.py
start python tests\mocks\mock_umnico.py

echo [8/8] Проверка работоспособности...
timeout /t 5
curl http://localhost:5000/health
curl http://localhost:5001/health
curl http://localhost:5002/health
curl http://localhost:5003/health

echo ✅ Среда успешно развёрнута!
pause
