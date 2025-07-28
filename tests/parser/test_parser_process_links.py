import pytest
from unittest.mock import AsyncMock
from bs4 import BeautifulSoup
from datetime import datetime
from parser_service.parser import ParserTrade

HTML_SAMPLE = """
<div class="accordeon-inner__item">
    <a href="/upload/oil_xls/file.xls" class="accordeon-inner__item-title link xls">Скачать</a>
    <span>01.01.2023</span>
</div>
<div class="accordeon-inner__item">
    <a href="/upload/oil_xls/file2.xls" class="accordeon-inner__item-title link xls">Скачать</a>
    <span>02.01.2023</span>
</div>
"""

@pytest.mark.asyncio
async def test_process_link_parsers_correctly(mocker):
    parser = ParserTrade(min_date=datetime(2023,1,1))
    
    mock_download = AsyncMock(return_value=b"fake_xls")
    mock_process_xls = AsyncMock()
    
    mocker.patch.object(parser, "download_xls", mock_download)
    mocker.patch.object(parser, "process_xls_and_save", mock_process_xls)
    
    content = HTML_SAMPLE.encode("utf-8")
    await parser._process_links(content)
    
    
    assert mock_download.call_count == 2
    assert mock_process_xls.call_count == 2
    
    first_call = mock_process_xls.call_args_list[0]
    _, args = first_call[0]
    assert args == datetime(2023, 1, 1)
    