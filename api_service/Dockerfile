FROM python:3.13-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . /app/api_service/

ENV PYTHONPATH=/app
CMD ["uvicorn", "api_service.main:app", "--host", "0.0.0.0", "--port", "8000"]