# tests/parser/test_parser_download_xls.py
import pytest
import io
from unittest.mock import AsyncMock, MagicMock
from parser_service.parser import ParserTrade


@pytest.mark.asyncio
async def test_download_xls_success(mocker):
    # 1. Мокаем response
    mock_response = MagicMock()
    mock_response.status = 200
    mock_response.read = AsyncMock(return_value=b"fake excel content")

    # 2. Мокаем контекстный менеджер для session.get()
    mock_cm = MagicMock()
    mock_cm.__aenter__ = AsyncMock(return_value=mock_response)
    mock_cm.__aexit__ = AsyncMock()

    # 3. Мокаем session.get() → возвращает объект с __aenter__/__aexit__
    mock_session = MagicMock()  # Не AsyncMock! Чтобы можно было контролировать get
    mock_session.get.return_value = mock_cm

    # 4. Мокаем ClientSession() → возвращаем mock_session при создании
    mock_client_session = mocker.patch("aiohttp.ClientSession", autospec=True)
    mock_client_session.return_value.__aenter__.return_value = mock_session
    mock_client_session.return_value.__aexit__ = AsyncMock()

    # 5. Запускаем тестируемый метод
    parser = ParserTrade()
    result = await parser.download_xls("https://spimex.com/file.xls")

    # 6. Проверяем результат
    assert result is not None, "Result is None — likely due to failed async context or status != 200"
    assert isinstance(result, io.BytesIO)
    assert result.getvalue() == b"fake excel content"

    # 7. Проверяем, что всё было вызвано
    mock_client_session.assert_called_once()
    mock_session.get.assert_called_once_with("https://spimex.com/file.xls", timeout=10)
    mock_cm.__aenter__.assert_called_once()