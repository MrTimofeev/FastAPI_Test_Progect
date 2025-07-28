import pytest
import io
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock
from xlrd import Book
from xlrd.sheet import Sheet
from parser_service.parser import ParserTrade
from parser_service.models import ParsedData


def create_fake_book():
    book = MagicMock(spec=Book)
    sheet = MagicMock(spec=Sheet)
    sheet.nrows = 2
    sheet.row_values.side_effect = [
        ["", "A1234567890", "Бензин", "Санкт-Петербург", "100", "50000", "5"],
        ["", "B2345678901", "ДТ", "Москва", "200", "100000", "10"]
    ]
    book.sheet_by_index.return_value = sheet
    return book

@pytest.mark.asyncio
async def test_process_xls_and_save(mocker):
    # 1. Мокаем лист Excel
    mock_sheet = MagicMock()
    mock_sheet.nrows = 2
    mock_sheet.row_values.side_effect = [
        ["", "A1234567890", "Бензин", "СПб", "100", "50000", "5"],
        ["", "B2345678901", "ДТ", "Москва", "200", "100000", "10"]
    ]

    # 2. Мокаем xlrd.open_workbook
    mock_book = MagicMock()
    mock_book.sheet_by_index.return_value = mock_sheet
    mocker.patch("xlrd.open_workbook", return_value=mock_book)

    # 3. Мокаем сессию
    mock_session = AsyncMock()
    mock_session.execute = AsyncMock()
    mock_session.commit = AsyncMock()

    # 4. Мокаем AsyncSessionLocal как асинхронный контекстный менеджер
    mock_session_cm = AsyncMock()
    mock_session_cm.__aenter__.return_value = mock_session
    mock_session_cm.__aexit__ = AsyncMock()

    # Самое важное: мокаем фабрику сессий
    mocker.patch("parser_service.parser.AsyncSessionLocal", return_value=mock_session_cm)

    # 5. Запускаем тестируемую функцию
    parser = ParserTrade()
    fake_xls = io.BytesIO(b"fake content")
    test_date = datetime(2023, 1, 1)

    await parser.process_xls_and_save(fake_xls, test_date)

    assert mock_session.execute.call_count == 1
    call_args = mock_session.execute.call_args
    stmt = call_args[0][0]  # объект Insert

    # === Достаём и разбираем данные ===
    params_values = list(stmt.compile().params.values())

    field_names = [
        "exchange_product_id",
        "exchange_product_name",
        "oil_id",
        "delivery_basis_id",
        "delivery_basis_name",
        "delivery_type_id",
        "volume",
        "total",
        "count",
        "date"
    ]

    chunk_size = len(field_names)
    assert len(params_values) % chunk_size == 0, "Количество значений не кратно числу полей"

    rows = [params_values[i:i + chunk_size] for i in range(0, len(params_values), chunk_size)]
    inserted_data = [dict(zip(field_names, row)) for row in rows]

    # === Проверяем результат ===
    assert len(inserted_data) == 2

    assert inserted_data[0]["exchange_product_id"] == "A1234567890"
    assert inserted_data[0]["oil_id"] == "A123"
    assert inserted_data[0]["volume"] == 100
    assert inserted_data[0]["date"] == test_date.date()

    assert inserted_data[1]["exchange_product_id"] == "B2345678901"
    assert inserted_data[1]["oil_id"] == "B234"
    assert inserted_data[1]["volume"] == 200