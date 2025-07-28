import pytest
from unittest.mock import AsyncMock, MagicMock
from fastapi.testclient import TestClient
import pytest_asyncio
from datetime import date

from api_service.main import app
from api_service.database import get_db
from api_service.models import ParsedData
from api_service.routers.trading import get_redis_client  # ← импортируем зависимость


@pytest_asyncio.fixture
async def client(mock_db_session, mock_redis):
    # Заменяем зависимости
    app.dependency_overrides[get_db] = lambda: mock_db_session
    app.dependency_overrides[get_redis_client] = lambda: mock_redis

    with TestClient(app) as c:
        yield c

    # Очищаем
    app.dependency_overrides.clear()


@pytest.fixture
def mock_redis():
    redis_mock = AsyncMock()
    redis_mock.get = AsyncMock(return_value=None)  # кэш пуст
    redis_mock.setex = AsyncMock()  # setex работает
    return redis_mock


@pytest.fixture
def mock_db_session():
    mock = AsyncMock()

    # Создаём мок для результата db.execute()
    mock_result = MagicMock()

    # 1. Для .all() → возвращаем список (НЕ корутину!)
    mock_result.all.return_value = [
        (ParsedData(oil_id="OIL001", delivery_type_id="DT1", date=date(2023, 10, 5)),),
        (ParsedData(oil_id="OIL002", delivery_type_id="DT2", date=date(2023, 10, 4)),),
    ]

    # 2. Если используется .scalars().all() → тоже настраиваем
    mock_result.scalars.return_value.all.return_value = [
        ParsedData(oil_id="OIL001", delivery_type_id="DT1", date=date(2023, 10, 5)),
        ParsedData(oil_id="OIL002", delivery_type_id="DT2", date=date(2023, 10, 4)),
    ]

    # 3. Для .scalar_one_or_none() — возвращаем один объект или None
    mock_result.scalar_one_or_none.return_value = date(2023, 10, 5)

    # Привязываем результат к execute
    mock.execute.return_value = mock_result

    return mock