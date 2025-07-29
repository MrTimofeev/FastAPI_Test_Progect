# parser_service/Dockerfile
FROM python:3.13-slim

WORKDIR /app

# Копируем зависимости парсера
COPY requirements/parser.txt .

# Устанавливаем зависимости
RUN pip install --no-cache-dir -r parser.txt

# Копируем pyproject.toml и src/
COPY pyproject.toml .
COPY src/ src/

# Устанавливаем проект в editable-режиме
RUN pip install -e .

# Запускаем парсер
CMD ["sh", "-c", "python -c 'from parser_service.parser import ParserTrade; import asyncio; asyncio.run(ParserTrade().run())'"]