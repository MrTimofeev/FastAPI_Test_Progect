FROM python:3.13-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Запуск скрипта с ожиданием БД
CMD ["sh", "-c", "python wait_for_db.py && python parser.py"]