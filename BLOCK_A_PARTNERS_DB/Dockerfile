FROM python:3.11-slim

WORKDIR /app

# Копируем requirements.txt из папки блока A
COPY BLOCK_A_PARTNERS_DB/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем весь код блока A
COPY BLOCK_A_PARTNERS_DB/ .

ENV FLASK_APP=run.py
ENV PORT=5000

EXPOSE 5000

CMD ["flask", "run", "--host=0.0.0.0", "--port=5000"]
