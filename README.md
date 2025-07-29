# FASTAPI_TEST_PROGECT

Микросервис для получения данных о торгах с сайта торгов через парсер и предоставления их через REST API.

---

## 🧱 Архитектура проекта

Проект состоит из нескольких сервисов:

- **API** — FastAPI, предоставляющий данные из БД.
- **Parser** — асинхронный парсер, собирающий данные с сайта и сохраняющий их в БД.
- **PostgreSQL** — основная база данных.
- **Redis** — кэширование результатов запросов.

---

## 📦 Структура проекта

```
spimex-trading-api/
│
├── src/                       # Общая кодовая база
│ ├── api_service/             # FastAPI сервис
│ │ ├── main.py                # Точка входа
│ │ ├── routers/trading.py     # Эндпоинты
│ │ ├── models.py              # ORM-модели
│ │ ├── schemas.py             # Pydantic-схемы
│ │ ├── database.py            # Асинхронная сессия
│ │ └── redis_cache.py         # Кэширование через Redis
│ └── parser_service/          # Парсер
│ ├── parser.py                # Основная логика парсинга
│ ├── models.py                # ORM-модели (общие с API)
│ └── database.py              # Подключение к БД
│
├── requirements/              # Зависимости
│ ├── api.txt                  # Зависимости API
│ └── parser.txt               # Зависимости парсера
│
├── api_service/               # Сборка API
│ └── Dockerfile
│
├── parser_service/            # Сборка парсера
│ └── Dockerfile
│
│ ├── api/                     # Тесты API
│ ├── parser/                  # Тесты парсера
│ └── conftest.py              # Общие фикстуры
├── tests/                     # Тесты
│
├── pyproject.toml             # Метаданные пакета (src/)
├── docker-compose.yml         # Оркестрация сервисов
├── .gitignore                 # Исключённые файлы
└── README.md                  # Этот файл
```

---

## 🔧 Установка

1. Клонируй репозиторий:
   ```bash
   git clone https://github.com/MrTimofeev/FastAPI_Test_Progect.git
   cd FastAPI_Test_Progect
   ```

2. Установи Docker и Docker Compose:
   - [Docker](https://docs.docker.com/get-docker/)
   - [Docker Compose](https://docs.docker.com/compose/install/)

3. Собери и запусти проект:
   ```bash
   docker-compose up -d --build
   ```

4. Открой документацию API:
   ```
   http://localhost:8000/docs
   ```

---

## 🕹️ Использование

### 1. API

API доступен по адресу:  
👉 `http://localhost:8000/trading/...`

#### GET `/trading/last_dates`

Возвращает последние N торговых дат.

Пример:
```
GET /trading/last_dates?n=5
```

#### GET `/trading/dynamics`

Возвращает данные за определённый период с фильтрами.

Параметры:
- `oil_id` — идентификатор нефти
- `delivery_type_id` — тип поставки
- `delivery_basis_id` — базис поставки
- `start_date` — начало периода
- `end_date` — конец периода

Пример:
```
GET /trading/dynamics?oil_id=A592&start_date=2024-01-01
```

#### GET `/trading/results`

Возвращает самые свежие торги.

Параметры:
- `oil_id` — идентификатор нефти
- `delivery_type_id` — тип поставки
- `delivery_basis_id` — базис поставки

Пример:
```
GET /trading/results?oil_id=A592
```

--- 
## 🗂️ Переменные окружения

Используются `.env` файлы в каждом сервисе.

`.env` для `api-service` и `parser-service`:
```env
DATABASE_URL=postgresql+asyncpg://user:password@postgres/spimex_db
```
---

## 🧪 Как проверить работу с БД

Подключись к PostgreSQL:
```bash
docker exec -it spimex-trading-api-postgres-1 psql -U user -d spimex_db
```

Выполни SQL-запрос:
```sql
SELECT * FROM parsed_data LIMIT 10;
```
