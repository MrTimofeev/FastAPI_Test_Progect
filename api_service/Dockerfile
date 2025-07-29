FROM python:3.13-slim

WORKDIR /app

# Копируем зависимости API
COPY requirements/api.txt .

# Устанавливаем зависимости
RUN pip install --no-cache-dir -r api.txt

COPY pyproject.toml .
COPY src/ src/

# Устанавливаем проект в editable-режиме
RUN pip install -e .

# Запускаем API
CMD ["uvicorn", "api_service.main:app", "--host", "0.0.0.0", "--port", "8000"]