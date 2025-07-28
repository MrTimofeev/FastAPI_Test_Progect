from datetime import date
import pytest


@pytest.mark.asyncio
async def test_get_last_trading_dates(client, mock_db_session):
    mock_result = mock_db_session.execute.return_value
    mock_result.all.return_value = [
        (date(2023, 12, 5),),
        (date(2023, 12, 4),),
    ]

    response = client.get("/trading/last_dates", params={"n": 2})

    assert response.status_code == 200
    assert response.json() == {"dates": ["2023-12-05", "2023-12-04"]}


@pytest.mark.asyncio
async def test_get_last_trading_dates_cached(client, mock_redis, mock_db_session):
    """Тестируем кэширование"""
    # Устанавливаем закэшированный ответ
    mock_redis.get.return_value = b'{"dates": ["2023-10-01"]}'

    response = client.get("/trading/last_dates", params={"n": 1})

    assert response.status_code == 200
    assert response.json() == {"dates": ["2023-10-01"]}
    # Проверяем, что запрос в БД НЕ делался
    assert mock_db_session.execute.called is False


@pytest.mark.asyncio
async def test_get_last_trading_dates_invalid_n(client):
    """Тестируем валидацию параметра n"""
    response = client.get("/trading/last_dates", params={"n": 0})
    assert response.status_code == 422  # ValidationError
