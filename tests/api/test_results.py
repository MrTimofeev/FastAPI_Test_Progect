from datetime import date
import pytest
import json
from api_service.models import ParsedData


@pytest.mark.asyncio
async def test_get_trading_results_last_date(client, mock_db_session):
    """Возвращаем последние торги за последнюю дату"""
    # Мок: последняя дата
    last_date_result = mock_db_session.execute.return_value
    last_date_result.scalar_one_or_none.return_value = date(2023, 10, 5)

    # Мок: данные за эту дату
    fake_data = [
        ParsedData(
            oil_id="OIL001",
            delivery_type_id="DT1",
            delivery_basis_id="DB1",
            date=date(2023, 10, 5),
            volume=1000,
        )
    ]
    data_result = mock_db_session.execute.return_value
    data_result.all.return_value = [(item,) for item in fake_data]

    # Два вызова execute(): сначала last_date, потом данные
    mock_db_session.execute.side_effect = [last_date_result, data_result]

    response = client.get("/trading/results")

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["date"] == "2023-10-05"


@pytest.mark.asyncio
async def test_get_trading_results_with_filters(client, mock_db_session):
    """С фильтрами — только подходящие записи"""
    last_date_result = mock_db_session.execute.return_value
    last_date_result.scalar_one_or_none.return_value = date(2023, 10, 5)

    fake_data = [ParsedData(oil_id="OIL001", delivery_type_id="DT1", date=date(2023, 10, 5))]
    data_result = mock_db_session.execute.return_value
    data_result.all.return_value = [(item,) for item in fake_data]

    mock_db_session.execute.side_effect = [last_date_result, data_result]

    response = client.get("/trading/results", params={"oil_id": "OIL001"})

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["oil_id"] == "OIL001"

    # Проверяем, что WHERE по oil_id был добавлен
    calls = mock_db_session.execute.call_args_list
    second_call_query = str(calls[1][0][0])
    assert "oil_id" in second_call_query


@pytest.mark.asyncio
async def test_get_trading_results_no_data(client, mock_db_session):
    """Если нет данных — возвращаем пустой список"""
    last_date_result = mock_db_session.execute.return_value
    last_date_result.scalar_one_or_none.return_value = None  # Нет последней даты

    mock_db_session.execute.return_value = last_date_result

    response = client.get("/trading/results")

    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.asyncio
async def test_get_trading_results_cached(client, mock_redis, mock_db_session):
    cached_data = [
        {
            "exchange_product_id": "EP1",
            "exchange_product_name": "Fuel",
            "oil_id": "OIL001",
            "delivery_basis_id": "DB1",
            "delivery_basis_name": "Basis 1",
            "delivery_type_id": "DT1",
            "volume": 1000,
            "total": 75000,
            "count": 1,
            "date": "2023-10-05",  
            "created_on": "2023-10-05",
            "updated_on": "2023-10-05"
        }
    ]
    mock_redis.get.return_value = json.dumps(cached_data)

    response = client.get("/trading/results", params={"oil_id": "OIL001"})

    assert response.status_code == 200
    assert response.json() == cached_data

    # БД не должна вызываться
    assert mock_db_session.execute.called is False