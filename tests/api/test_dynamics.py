from datetime import date
import pytest
import json
from api_service.models import ParsedData


@pytest.mark.asyncio
async def test_get_dynamics_no_filters(client, mock_db_session):
    """Без фильтров — возвращаем все данные за период"""
    fake_data = [
        ParsedData(
            exchange_product_id="EP1",
            exchange_product_name="Fuel",
            oil_id="OIL001",
            delivery_basis_id="DB1",
            delivery_basis_name="Basis 1",
            delivery_type_id="DT1",
            volume=1000,
            total=75000,
            count=1,
            date=date(2023, 10, 5),
        ),
        ParsedData(
            exchange_product_id="EP2",
            exchange_product_name="Diesel",
            oil_id="OIL002",
            delivery_basis_id="DB2",
            delivery_basis_name="Basis 2",
            delivery_type_id="DT2",
            volume=1200,
            total=90000,
            count=1,
            date=date(2023, 10, 6),
        ),
    ]

    # Мокируем результат БД
    mock_result = mock_db_session.execute.return_value
    mock_result.all.return_value = [(item,) for item in fake_data]

    response = client.get("/trading/dynamics")

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]["oil_id"] == "OIL001"


@pytest.mark.asyncio
async def test_get_dynamics_with_filters(client, mock_db_session):
    """С фильтрами — только подходящие записи"""
    fake_data = [
        ParsedData(
            oil_id="OIL001",
            delivery_type_id="DT1",
            delivery_basis_id="DB1",
            date=date(2023, 10, 5),
            volume=1000,
        )
    ]
    mock_result = mock_db_session.execute.return_value
    mock_result.all.return_value = [(item,) for item in fake_data]

    response = client.get(
        "/trading/dynamics",
        params={
            "oil_id": "OIL001",
            "delivery_type_id": "DT1",
            "start_date": "2023-10-01",
            "end_date": "2023-10-10",
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["oil_id"] == "OIL001"

    assert mock_db_session.execute.called
    


@pytest.mark.asyncio
async def test_get_dynamics_cached(client, mock_redis, mock_db_session):
    # ✅ Только поля из ParsedDataSchema, с правильными типами
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

    response = client.get("/trading/dynamics", params={"oil_id": "OIL001"})

    assert response.status_code == 200
    assert response.json() == cached_data

    # БД не должна вызываться
    assert mock_db_session.execute.called is False