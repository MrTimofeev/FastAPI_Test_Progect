import pytest
from unittest.mock import AsyncMock
from fastapi.testclient import TestClient
import pytest_asyncio

from api_service.main import app
from api_service.database import get_db
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
    yield mock