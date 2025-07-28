FROM python:3.13-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app/parser_service/

# Устанавливаем PYTHONPATH, чтобы Python видел parser_service как пакет
ENV PYTHONPATH=/app

# Запускаем parser.py из пакета
CMD ["sh", "-c", "python /app/parser_service/wait_for_db.py && python /app/parser_service/parser.py"]